"""
Data Collector for Motorsport Calendar

Orchestrates data collection from multiple prioritized sources,
handles source management, and coordinates the collection process.
"""

import asyncio
import concurrent.futures
import faulthandler
import importlib
import inspect
import os
import sys
import signal
import multiprocessing as mp
import queue
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Type
from pathlib import Path
import time

from sources.base_source import BaseSource
from sources.tomada_tempo import TomadaTempoSource


def _run_source_in_subprocess(module_name: str, class_name: str, data_sources_config: Dict[str, Any], target_date_iso: str) -> List[Dict[str, Any]]:
    """Função topo-de-módulo para execução em subprocesso.

    - Reinstancia a fonte sem logger/UI (para evitar objetos não-serializáveis)
    - Usa um proxy mínimo de configuração baseado em dict
    """
    # Proxy simples somente com a interface necessária
    class _ConfigProxy:
        def __init__(self, cfg: Dict[str, Any]):
            self._cfg = dict(cfg or {})

        def get_data_sources_config(self) -> Dict[str, Any]:
            return dict(self._cfg)

    # Suporte a cancelamento cooperativo via sinais (SIGTERM/SIGINT) no subprocesso
    # Usamos um holder para referenciar a instância após criação
    _source_holder: Dict[str, Any] = {"src": None}

    def _sig_cancel_handler(signum, frame):
        try:
            # Log imediato no processo-filho para visibilidade de cancelamento
            try:
                sig_label = signal.Signals(signum).name
            except Exception:
                sig_label = str(signum)
            try:
                pid = os.getpid()
                sys.stderr.write(f"⚠️ [proc-child pid={pid}] Received {sig_label}; setting cancel_event if available\n")
                sys.stderr.flush()
            except Exception:
                pass
            src = _source_holder.get("src")
            if src is not None and hasattr(src, "cancel_event") and src.cancel_event is not None:
                src.cancel_event.set()
        except Exception:
            # Evita falhas no handler interromperem o processo
            pass

    try:
        signal.signal(signal.SIGTERM, _sig_cancel_handler)
    except Exception:
        pass
    try:
        signal.signal(signal.SIGINT, _sig_cancel_handler)
    except Exception:
        pass

    # Importa classe
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)

    # Instancia com config mínima
    cfg = _ConfigProxy(data_sources_config)
    source: BaseSource = cls(config_manager=cfg, logger=None, ui_manager=None)
    _source_holder["src"] = source

    # Converte target_date
    td = datetime.fromisoformat(target_date_iso)

    # Executa coleta
    events = source.collect_events(td)
    # Normaliza para garantir serialização simples (já são dicts/strings/datetimes)
    # Datetimes dentro dos eventos devem ser serializáveis; assumimos que sim (ou strings)
    return events

def _proc_worker(result_q: mp.Queue, src_name: str, display: str, module_name: str, class_name: str, cfg: Dict[str, Any], target_iso: str) -> None:
    """Worker top-level para compatibilidade com start method 'spawn' (macOS/Windows).

    Executa a coleta via `_run_source_in_subprocess` e envia um pacote com status na fila.
    """
    try:
        events = _run_source_in_subprocess(module_name, class_name, cfg, target_iso)
        result_q.put({
            "status": "ok",
            "source_name": src_name,
            "display": display,
            "events": events,
        })
    except Exception as e:
        result_q.put({
            "status": "error",
            "source_name": src_name,
            "display": display,
            "error": f"Collection failed: {e}",
        })


class DataCollector:
    """Coordinates data collection from multiple motorsport sources."""
    
    def __init__(self, config_manager=None, logger=None, ui_manager=None, category_detector=None):
        """
        Initialize data collector.
        
        Args:
            config_manager: Configuration manager instance
            logger: Logger instance
            ui_manager: UI manager instance
            category_detector: Category detector instance
        """
        self.config = config_manager
        self.logger = logger
        self.ui = ui_manager
        self.category_detector = category_detector
        
        # Source management
        self.available_sources = {}
        self.active_sources = []
        self.source_priorities = {}
        self.excluded_sources = set()
        
        # Collection settings
        self.max_concurrent_sources = 3
        self.collection_timeout = 300  # 5 minutes
        self.retry_failed_sources = True
        self.max_retries = 1
        self.retry_backoff_seconds = 0.5
        self.use_process_pool = False
        self.per_source_timeout_seconds: Optional[float] = None
        
        # Statistics
        self.collection_stats = {
            'total_sources_attempted': 0,
            'successful_sources': 0,
            'failed_sources': 0,
            'total_events_collected': 0,
            'collection_start_time': None,
            'collection_end_time': None,
            'source_results': {}
        }
        
        # Load configuration and discover sources
        self._load_config()
        self._discover_sources()
        self._initialize_sources()
    
    def _load_config(self) -> None:
        """Load data collection configuration."""
        if not self.config:
            return
        
        data_sources_config = self.config.get_data_sources_config()
        
        # Collection settings
        self.max_concurrent_sources = data_sources_config.get('max_concurrent_sources', 3)
        self.collection_timeout = data_sources_config.get('collection_timeout_seconds', 300)
        self.retry_failed_sources = data_sources_config.get('retry_failed_sources', True)
        # Backward-compat: se max_retries não existir, usar retry_attempts
        self.max_retries = data_sources_config.get('max_retries', data_sources_config.get('retry_attempts', 1))
        self.retry_backoff_seconds = data_sources_config.get('retry_backoff_seconds', 0.5)
        self.use_process_pool = bool(data_sources_config.get('use_process_pool', False))
        self.per_source_timeout_seconds = data_sources_config.get('per_source_timeout_seconds')
        
        # Source priorities from priority_order list
        priority_order = data_sources_config.get('priority_order', [])
        for i, source_name in enumerate(priority_order):
            # Higher priority for sources earlier in the list (reverse priority)
            self.source_priorities[source_name] = 100 - (i * 10)
        
        # Excluded sources list
        excluded_list = data_sources_config.get('excluded_sources', [])
        self.excluded_sources.update(excluded_list)
    
    def _discover_sources(self) -> None:
        """Discover available source classes."""
        # Built-in sources
        built_in_sources = {
            'tomada_tempo': TomadaTempoSource,
        }
        
        self.available_sources.update(built_in_sources)
        
        # Dynamically discover sources in the sources directory
        try:
            sources_dir = Path(__file__).parent.parent / 'sources'
            if sources_dir.exists():
                for source_file in sources_dir.glob('*.py'):
                    if source_file.name.startswith('_') or source_file.name == 'base_source.py':
                        continue
                    
                    module_name = source_file.stem
                    try:
                        # Import the module
                        module = importlib.import_module(f'sources.{module_name}')
                        
                        # Find source classes
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if (issubclass(obj, BaseSource) and 
                                obj != BaseSource and 
                                name.endswith('Source')):
                                
                                source_key = module_name
                                self.available_sources[source_key] = obj
                                
                                if self.logger:
                                    self.logger.debug(f"🔍 Discovered source: {name} ({source_key})")
                    
                    except Exception as e:
                        if self.logger:
                            self.logger.debug(f"⚠️ Failed to load source module {module_name}: {e}")
        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error discovering sources: {e}")
        
        if self.logger:
            self.logger.debug(f"📋 Available sources: {list(self.available_sources.keys())}")
    
    def _initialize_sources(self) -> None:
        """Initialize active source instances."""
        # Sort sources by priority (higher priority first)
        sorted_sources = sorted(
            self.available_sources.items(),
            key=lambda x: self.source_priorities.get(x[0], 50),
            reverse=True
        )
        
        for source_name, source_class in sorted_sources:
            if source_name in self.excluded_sources:
                if self.logger:
                    self.logger.debug(f"⏭️ Skipping excluded source: {source_name}")
                continue
            
            try:
                # Initialize source instance
                source_instance = source_class(
                    config_manager=self.config,
                    logger=self.logger,
                    ui_manager=self.ui
                )
                
                self.active_sources.append(source_instance)
                
                if self.logger:
                    self.logger.debug(f"✅ Initialized source: {source_instance.get_display_name()}")
            
            except Exception as e:
                if self.logger:
                    self.logger.log_source_error(source_name, f"Failed to initialize: {e}")
    
    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Collect events from all active sources.
        
        Args:
            target_date: Target date for event collection
            
        Returns:
            List of collected events from all sources
        """
        if self.logger:
            self.logger.log_step("🏁 Starting data collection from all sources")
        
        if self.ui:
            self.ui.show_step("Data Collection", "Collecting events from multiple sources...")
        
        # Initialize collection statistics
        self.collection_stats['collection_start_time'] = datetime.now().isoformat()
        self.collection_stats['total_sources_attempted'] = len(self.active_sources)
        
        all_events = []
        
        if not self.active_sources:
            if self.logger:
                self.logger.log_error("No active sources available for data collection")
            return all_events
        
        # Determine target date if not provided
        if not target_date:
            target_date = self._get_target_weekend()
        
        if self.logger:
            self.logger.debug(f"🎯 Target date for collection: {target_date.strftime('%Y-%m-%d')}")
        
        # Habilita watchdog de stacktrace se demorar demais (ajuda diagnóstico de hang)
        # Será cancelado ao final do método.
        try:
            faulthandler.dump_traceback_later(timeout=self.collection_timeout + 30, repeat=False)
        except Exception:
            # Se não suportado no ambiente, segue sem watchdog
            pass

        try:
            # Collect from sources (with concurrency control)
            if self.max_concurrent_sources > 1:
                if self.use_process_pool:
                    all_events = self._collect_concurrent_processes(target_date)
                else:
                    all_events = self._collect_concurrent(target_date)
            else:
                all_events = self._collect_sequential(target_date)
        finally:
            # Cancela watchdog se habilitado
            try:
                faulthandler.cancel_dump_traceback_later()
            except Exception:
                pass
        
        # Update final statistics
        self.collection_stats['collection_end_time'] = datetime.now().isoformat()
        self.collection_stats['total_events_collected'] = len(all_events)
        
        # Log collection summary
        self._log_collection_summary()
        
        return all_events
    
    def _collect_sequential(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events sequentially from all sources.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of all collected events
        """
        all_events = []
        
        for source in self.active_sources:
            try:
                if self.logger:
                    self.logger.debug(f"🔄 Collecting from {source.get_display_name()}...")
                
                # Collect events from this source
                source_events = self._collect_from_source(source, target_date)
                
                # Add source metadata to events
                for event in source_events:
                    event['source_priority'] = self.source_priorities.get(source.source_name, 50)
                
                all_events.extend(source_events)
                
                # Update statistics
                self.collection_stats['successful_sources'] += 1
                self.collection_stats['source_results'][source.source_name] = {
                    'success': True,
                    'events_count': len(source_events),
                    'source_display_name': source.get_display_name()
                }
                
                if self.logger:
                    self.logger.log_source_success(source.get_display_name(), len(source_events))
            
            except Exception as e:
                error_msg = f"Collection failed: {str(e)}"
                
                self.collection_stats['failed_sources'] += 1
                self.collection_stats['source_results'][source.source_name] = {
                    'success': False,
                    'error': error_msg,
                    'source_display_name': source.get_display_name()
                }
                
                if self.logger:
                    self.logger.log_source_error(source.get_display_name(), error_msg)
        
        return all_events
    
    def _collect_concurrent(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events concurrently from multiple sources.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of all collected events
        """
        all_events = []
        
        # Não usar context manager para poder controlar shutdown(wait=False)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_sources)
        start_by_source: Dict[str, float] = {}
        try:
            # Submit tasks
            future_to_source: Dict[concurrent.futures.Future, BaseSource] = {}
            for source in self.active_sources:
                start_by_source[source.source_name] = time.time()
                if self.logger:
                    self.logger.debug(f"🔄 Collecting from {source.get_display_name()}...")
                future = executor.submit(self._collect_from_source, source, target_date)
                future_to_source[future] = source

            # Espera global até timeout por todas as futures
            done, not_done = concurrent.futures.wait(
                set(future_to_source.keys()),
                timeout=self.collection_timeout,
                return_when=concurrent.futures.ALL_COMPLETED,
            )

            # Cancela as pendentes e marca timeout
            if not_done:
                for f in not_done:
                    # Sinaliza cancelamento cooperativo na fonte
                    src = future_to_source.get(f)
                    if src is not None and hasattr(src, 'cancel_event'):
                        try:
                            src.cancel_event.set()
                        except Exception:
                            pass
                    f.cancel()
                if self.logger:
                    pending = ", ".join(
                        future_to_source[f].get_display_name() for f in not_done
                    )
                    self.logger.debug(
                        f"⏱️ Global collection timeout after {self.collection_timeout}s; cancelling: {pending}"
                    )
                # Registra erro de timeout por fonte não concluída
                for f in not_done:
                    src = future_to_source[f]
                    self._handle_source_error(
                        src,
                        f"Collection timed out after {self.collection_timeout} seconds",
                    )

            # Processa resultados concluídos
            for f in done:
                source = future_to_source[f]
                try:
                    # Se per_source_timeout_seconds configurado, aplica ao obter o resultado
                    if self.per_source_timeout_seconds and self.per_source_timeout_seconds > 0:
                        source_events = f.result(timeout=float(self.per_source_timeout_seconds))
                    else:
                        source_events = f.result()

                    # Add source metadata to events
                    for event in source_events:
                        event['source_priority'] = self.source_priorities.get(source.source_name, 50)

                    all_events.extend(source_events)

                    # Update statistics
                    self.collection_stats['successful_sources'] += 1
                    self.collection_stats['source_results'][source.source_name] = {
                        'success': True,
                        'events_count': len(source_events),
                        'source_display_name': source.get_display_name()
                    }

                    if self.logger:
                        duration = time.time() - start_by_source.get(source.source_name, time.time())
                        self.logger.log_source_success(source.get_display_name(), len(source_events))
                        self.logger.debug(f"⏱️ {source.get_display_name()} finished in {duration:.1f}s")

                except concurrent.futures.TimeoutError as e:
                    # Timeout por-fonte ao obter resultado: aciona cancel_event e registra erro
                    try:
                        if hasattr(source, 'cancel_event'):
                            source.cancel_event.set()
                    finally:
                        self._handle_source_error(source, f"Per-source timeout after {self.per_source_timeout_seconds}s: {e}")
                        if self.logger:
                            self.logger.debug(f"⛔ Cancel signalled to {source.get_display_name()} due to per-source timeout")
                        continue
                except Exception as e:
                    error_msg = f"Collection failed: {str(e)}"
                    self._handle_source_error(source, error_msg)

            return all_events
        finally:
            # Encerra sem bloquear; tenta cancelar futures remanescentes
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except TypeError:
                # Compatibilidade com versões antigas do Python
                executor.shutdown(wait=False)

    def _collect_concurrent_processes(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Coleta concorrente usando processos dedicados (multiprocessing.Process),
        com cancelamento cooperativo via sinais no subprocesso e término forçado
        por timeout (global e por-fonte) usando terminate/kill.

        Args:
            target_date: Data alvo

        Returns:
            Lista de eventos coletados
        """
        all_events: List[Dict[str, Any]] = []

        # Prepara pacote mínimo de config serializável
        data_sources_config: Dict[str, Any] = {}
        try:
            if self.config:
                data_sources_config = dict(self.config.get_data_sources_config() or {})
        except Exception:
            data_sources_config = {}

        # Fila compartilhada para resultados
        result_queue: mp.Queue = mp.Queue()

        # Estruturas de controle
        procs: Dict[str, mp.Process] = {}
        start_by_source: Dict[str, float] = {}
        display_by_source: Dict[str, str] = {}

        # worker movido para nível de módulo como `_proc_worker` para compatibilidade com 'spawn'

        # Inicia processos
        for source in self.active_sources:
            start_by_source[source.source_name] = time.time()
            display_by_source[source.source_name] = source.get_display_name()
            if self.logger:
                self.logger.debug(f"🔄 [proc] Collecting from {source.get_display_name()}...")

            cls = source.__class__
            module_name = cls.__module__
            class_name = cls.__name__
            target_iso = target_date.isoformat()

            p = mp.Process(
                target=_proc_worker,
                args=(result_queue, source.source_name, source.get_display_name(), module_name, class_name, data_sources_config, target_iso),
                name=f"collector-{source.source_name}",
            )
            p.daemon = False  # queremos controle explícito de término
            p.start()
            procs[source.source_name] = p

        total = len(procs)
        completed: Dict[str, bool] = {name: False for name in procs}

        deadline = time.time() + float(self.collection_timeout)
        per_src_timeout = float(self.per_source_timeout_seconds) if (self.per_source_timeout_seconds and self.per_source_timeout_seconds > 0) else None

        # Loop de supervisão
        while True:
            now = time.time()

            # Consome resultados disponíveis sem bloquear
            while True:
                try:
                    msg = result_queue.get_nowait()
                except queue.Empty:
                    break
                if not isinstance(msg, dict):
                    continue
                src_name = msg.get("source_name")
                if not src_name or src_name not in procs or completed.get(src_name):
                    continue

                # Marca como concluído e trata
                completed[src_name] = True
                proc = procs[src_name]
                try:
                    if proc.is_alive():
                        # processo terminou logicamente; garante reaproveitamento
                        proc.join(timeout=0.1)
                except Exception:
                    pass

                if msg.get("status") == "ok":
                    source_events = msg.get("events") or []
                    # metadados
                    for event in source_events:
                        event['source_priority'] = self.source_priorities.get(src_name, 50)
                    all_events.extend(source_events)

                    # estatísticas
                    self.collection_stats['successful_sources'] += 1
                    self.collection_stats['source_results'][src_name] = {
                        'success': True,
                        'events_count': len(source_events),
                        'source_display_name': display_by_source.get(src_name, src_name),
                    }

                    if self.logger:
                        duration = now - start_by_source.get(src_name, now)
                        self.logger.log_source_success(display_by_source.get(src_name, src_name), len(source_events))
                        self.logger.debug(f"⏱️ [proc] {display_by_source.get(src_name, src_name)} finished in {duration:.1f}s")
                else:
                    err_msg = msg.get("error") or "Unknown error"
                    # Encontra objeto source correspondente para logging estatístico
                    src_obj = next((s for s in self.active_sources if s.source_name == src_name), None)
                    if src_obj is not None:
                        self._handle_source_error(src_obj, err_msg)
                    else:
                        if self.logger:
                            self.logger.log_source_error(display_by_source.get(src_name, src_name), err_msg)

            # Verifica timeouts por-fonte
            if per_src_timeout is not None and per_src_timeout > 0:
                for src_name, proc in procs.items():
                    if completed.get(src_name):
                        continue
                    elapsed = now - start_by_source.get(src_name, now)
                    if elapsed > per_src_timeout:
                        # Timeout por-fonte: envia término (SIGTERM) e registra erro
                        try:
                            if proc.is_alive():
                                proc.terminate()  # SIGTERM em POSIX -> handler seta cancel_event
                                if self.logger:
                                    self.logger.debug(
                                        f"⏱️ [proc] Per-source timeout after {per_src_timeout}s; sending SIGTERM to {display_by_source.get(src_name, src_name)} (pid={proc.pid})"
                                    )
                        except Exception:
                            pass
                        # Loga erro estatístico e marca como concluído
                        src_obj = next((s for s in self.active_sources if s.source_name == src_name), None)
                        if src_obj is not None:
                            self._handle_source_error(src_obj, f"Per-source timeout after {per_src_timeout}s")
                        completed[src_name] = True

            # Condições de parada
            if all(completed.values()):
                break
            if now >= deadline:
                # Timeout global: encerra remanescentes
                pending = [n for n, v in completed.items() if not v]
                if self.logger and pending:
                    names = ", ".join(
                        f"{display_by_source.get(n, n)}(pid={procs[n].pid})" for n in pending
                    )
                    self.logger.debug(
                        f"⏱️ [proc] Global collection timeout after {self.collection_timeout}s; sending SIGTERM to: {names}"
                    )
                for src_name in pending:
                    proc = procs[src_name]
                    try:
                        if proc.is_alive():
                            proc.terminate()  # SIGTERM
                    except Exception:
                        pass
                    # Marca erro estatístico
                    src_obj = next((s for s in self.active_sources if s.source_name == src_name), None)
                    if src_obj is not None:
                        self._handle_source_error(src_obj, f"Collection timed out after {self.collection_timeout} seconds")
                    completed[src_name] = True
                break

            # Pequeno intervalo para evitar busy-wait; curto o bastante para responsividade
            time.sleep(0.05)

        # Pós-processamento: força kill de quaisquer processos que ainda estejam vivos
        for src_name, proc in procs.items():
            try:
                if proc.is_alive():
                    # Tentativa final de término educado
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    # Aguarda breve
                    proc.join(timeout=0.2)
                    if proc.is_alive():
                        # Kill duro (POSIX)
                        try:
                            os.kill(proc.pid, signal.SIGKILL)
                            if self.logger:
                                self.logger.debug(
                                    f"🛑 [proc] Escalating to SIGKILL for {display_by_source.get(src_name, src_name)} (pid={proc.pid})"
                                )
                        except Exception:
                            pass
                # Loga código de saída/terminação por sinal, se disponível
                if self.logger and proc.exitcode is not None:
                    if proc.exitcode < 0:
                        self.logger.debug(
                            f"⚠️ [proc] {display_by_source.get(src_name, src_name)} terminated by signal {-proc.exitcode}"
                        )
                    elif proc.exitcode > 0:
                        self.logger.debug(
                            f"⚠️ [proc] {display_by_source.get(src_name, src_name)} exited with code {proc.exitcode}"
                        )
            except Exception:
                pass

        return all_events

    def _collect_from_source(self, source: BaseSource, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events from a single source (for concurrent execution).
        
{{ ... }}
        Args:
            source: Source instance
            target_date: Target date for collection
            
        Returns:
            List of events from this source
        """
        total_attempts = 1
        if self.retry_failed_sources:
            # total tentativas = 1 (primeira) + max_retries (retries adicionais)
            total_attempts = 1 + max(0, int(self.max_retries))

        last_error: Exception | None = None

        for attempt in range(1, total_attempts + 1):
            try:
                return source.collect_events(target_date)
            except Exception as e:
                # Erros transitórios para retry
                is_transient = isinstance(e, (TimeoutError, OSError, IOError))

                # Se não habilitado, não-transitório, ou última tentativa: propagar
                if (not self.retry_failed_sources) or (not is_transient) or (attempt == total_attempts):
                    last_error = e
                    break

                # Log da tentativa e espera (backoff linear)
                if self.logger:
                    self.logger.debug(
                        f"⏳ Retry {attempt}/{total_attempts - 1} for {source.get_display_name()} after transient error: {e}"
                    )
                wait_seconds = float(self.retry_backoff_seconds) * attempt
                if wait_seconds > 0:
                    # Espera cooperativa usando cancel_event da fonte, se existir
                    try:
                        if hasattr(source, 'cancel_event') and source.cancel_event is not None:
                            # wait retorna True se cancelado; interrompe com TimeoutError
                            if source.cancel_event.wait(timeout=wait_seconds):
                                raise TimeoutError("Cancelled during retry backoff")
                        else:
                            time.sleep(wait_seconds)
                    except Exception:
                        # Se cancelado, propaga para encerrar rapidamente
                        raise

        # Se chegou aqui, falhou após tentativas
        if last_error is not None:
            raise last_error
        # fallback defensivo (não deve ocorrer)
        return []
    
    def _handle_source_error(self, source: BaseSource, error_msg: str) -> None:
        """Handle error from a source."""
        self.collection_stats['failed_sources'] += 1
        self.collection_stats['source_results'][source.source_name] = {
            'success': False,
            'error': error_msg,
            'source_display_name': source.get_display_name()
        }
        
        if self.logger:
            self.logger.log_source_error(source.get_display_name(), error_msg)
    
    def _get_target_weekend(self) -> datetime:
        """
        Determine the target weekend for event collection.
        
        Returns:
            Target weekend date
        """
        today = datetime.now()
        
        # If it's already weekend (Friday-Sunday), use current weekend
        if today.weekday() >= 4:  # Friday=4, Saturday=5, Sunday=6
            # Find the Friday of current week
            days_since_friday = today.weekday() - 4
            target_friday = today - timedelta(days=days_since_friday)
        else:
            # Use next weekend
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            target_friday = today + timedelta(days=days_until_friday)
        
        return target_friday
    
    def _log_collection_summary(self) -> None:
        """Log collection summary statistics."""
        if not self.logger:
            return
        
        stats = self.collection_stats
        
        self.logger.log_step(
            f"📊 Collection Summary: "
            f"{stats['successful_sources']}/{stats['total_sources_attempted']} sources successful, "
            f"{stats['total_events_collected']} events collected"
        )
        
        # Log individual source results
        for source_name, result in stats['source_results'].items():
            if result['success']:
                self.logger.debug(
                    f"✅ {result['source_display_name']}: {result['events_count']} events"
                )
            else:
                self.logger.debug(
                    f"❌ {result['source_display_name']}: {result['error']}"
                )
        
        # Calculate collection time
        if stats['collection_start_time'] and stats['collection_end_time']:
            start_time = datetime.fromisoformat(stats['collection_start_time'])
            end_time = datetime.fromisoformat(stats['collection_end_time'])
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"⏱️ Collection completed in {duration:.1f} seconds")
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """
        Get detailed statistics for all sources.
        
        Returns:
            Dictionary with source statistics
        """
        source_stats = {}
        
        for source in self.active_sources:
            source_stats[source.source_name] = source.get_statistics()
        
        return {
            'collection_stats': self.collection_stats,
            'source_stats': source_stats,
            'active_sources_count': len(self.active_sources),
            'available_sources_count': len(self.available_sources),
            'excluded_sources': list(self.excluded_sources)
        }
    
    def add_source(self, source_class: Type[BaseSource], priority: int = 50) -> bool:
        """
        Add a new source to the collector.
        
        Args:
            source_class: Source class to add
            priority: Priority for this source
            
        Returns:
            True if source was added successfully
        """
        try:
            source_name = source_class.__name__.replace('Source', '').lower()
            
            if source_name in self.excluded_sources:
                return False
            
            # Initialize source instance
            source_instance = source_class(
                config_manager=self.config,
                logger=self.logger,
                ui_manager=self.ui
            )
            
            self.active_sources.append(source_instance)
            self.source_priorities[source_name] = priority
            
            # Re-sort sources by priority
            self.active_sources.sort(
                key=lambda s: self.source_priorities.get(s.source_name, 50),
                reverse=True
            )
            
            if self.logger:
                self.logger.debug(f"➕ Added source: {source_instance.get_display_name()}")
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Failed to add source: {e}")
            return False
    
    def remove_source(self, source_name: str) -> bool:
        """
        Remove a source from the collector.
        
        Args:
            source_name: Name of source to remove
            
        Returns:
            True if source was removed successfully
        """
        for i, source in enumerate(self.active_sources):
            if source.source_name == source_name:
                removed_source = self.active_sources.pop(i)
                
                if self.logger:
                    self.logger.debug(f"➖ Removed source: {removed_source.get_display_name()}")
                
                return True
        
        return False
    
    def cleanup(self) -> None:
        """Clean up all source resources."""
        for source in self.active_sources:
            try:
                source.cleanup()
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"⚠️ Error cleaning up source {source.source_name}: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    def __str__(self) -> str:
        """String representation."""
        return f"DataCollector({len(self.active_sources)} active sources)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        source_names = [s.source_name for s in self.active_sources]
        return f"<DataCollector(sources={source_names})>"
