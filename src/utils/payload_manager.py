"""
Gerenciamento de payloads do sistema de logging.

Este módulo fornece funcionalidades para salvar, rotacionar e limpar
arquivos de payload gerados durante a execução do sistema.
"""
import json
import gzip
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Tuple
from datetime import datetime, timedelta
import logging

from .error_codes import ErrorCode

class PayloadManager:
    """Gerencia o armazenamento e rotação de payloads de log."""
    
    def __init__(self, base_dir: str = "logs/payloads", logger: Optional[logging.Logger] = None):
        """Inicializa o gerenciador de payloads.
        
        Args:
            base_dir: Diretório base para armazenamento de payloads
            logger: Instância de logger para mensagens de depuração/erro
        """
        self.base_dir = Path(base_dir)
        self.logger = logger or logging.getLogger(__name__)
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """Garante que o diretório base de payloads existe."""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            error_msg = (
                f"[{ErrorCode.LOGGER_INIT_FAILED}] "
                f"Falha ao criar diretório de payloads: {self.base_dir}. Erro: {str(e)}"
            )
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def save_payload(
        self,
        source: str,
        data: Any,
        data_type: str = 'json',
        compress: bool = True,
        max_payloads: int = 50,
        max_age_days: int = 30
    ) -> str:
        """Salva um payload no sistema de arquivos."""
        try:
            source_dir = self.base_dir / source.replace(" ", "_")
            source_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            ext = data_type.lower()
            filename = f"{timestamp}.{ext}"
            
            if compress:
                filename += ".gz"
            
            filepath = source_dir / filename
            
            # Serialização dos dados
            if data_type == 'json':
                data_str = json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, (str, bytes, bytearray)) else str(data)
                self._write_data(filepath, data_str, compress)
            elif data_type in ('html', 'xml', 'text'):
                self._write_data(filepath, str(data), compress, mode='wt')
            elif data_type == 'binary':
                data_bytes = data if isinstance(data, (bytes, bytearray)) else str(data).encode('utf-8')
                self._write_data(filepath, data_bytes, compress, mode='wb')
            else:
                raise ValueError(
                    f"[{ErrorCode.OUTPUT_FORMAT_ERROR}] "
                    f"Tipo de dados não suportado: {data_type}"
                )
            
            self.cleanup_old_payloads(source, max_payloads, max_age_days)
            
            if self.logger:
                self.logger.debug(
                    f"Payload salvo: {filepath} "
                    f"(Tipo: {data_type}, Tamanho: {filepath.stat().st_size} bytes)"
                )
            
            return str(filepath)
            
        except Exception as e:
            error_msg = f"[{ErrorCode.OUTPUT_WRITE_ERROR}] Falha ao salvar payload: {str(e)}"
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            raise IOError(error_msg) from e
    
    def _write_data(self, filepath: Path, data: Any, compress: bool, mode: str = 'wt') -> None:
        """Método auxiliar para escrita de dados."""
        if compress:
            open_fn = gzip.open if 'b' in mode else lambda f, m, **k: gzip.open(f, m, encoding='utf-8')
            with open_fn(filepath, mode) as f:
                f.write(data)
        else:
            with open(filepath, mode, encoding=None if 'b' in mode else 'utf-8') as f:
                f.write(data)
    
    def cleanup_old_payloads(
        self,
        source: str,
        max_files: int = 50,
        max_age_days: int = 30
    ) -> Tuple[int, int]:
        """Remove payloads antigos ou em excesso.
        
        Args:
            source: Nome da fonte de dados
            max_files: Número máximo de arquivos a manter por fonte
            max_age_days: Idade máxima em dias para manter os arquivos
            
        Returns:
            Tupla com (arquivos_removidos, erros_ocorridos)
        """
        source_dir = self.base_dir / source.replace(" ", "_")
        if not source_dir.exists() or not source_dir.is_dir():
            return 0, 0
        
        removed = 0
        errors = 0
        now = datetime.now()
        cutoff_time = now - timedelta(days=max_age_days)
        
        try:
            # Lista todos os arquivos no diretório da fonte
            files = []
            for f in source_dir.iterdir():
                if f.is_file():
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    files.append((f, mtime))
            
            # Ordena por data de modificação (mais antigos primeiro)
            files.sort(key=lambda x: x[1])
            
            # Remove por limite de idade
            for filepath, mtime in files:
                if mtime < cutoff_time:
                    try:
                        filepath.unlink()
                        removed += 1
                        if self.logger:
                            self.logger.debug(
                                f"Removido payload antigo: {filepath} "
                                f"(Última modificação: {mtime})"
                            )
                    except Exception as e:
                        errors += 1
                        if self.logger:
                            self.logger.warning(
                                f"[{ErrorCode.LOG_RETENTION_CLEANUP_FAILED}] "
                                f"Falha ao remover arquivo antigo {filepath}: {e}"
                            )
            
            # Remove por limite de quantidade (mantém apenas os N mais recentes)
            remaining_files = [f for f, _ in files if f.exists()]  # Apenas arquivos que ainda existem
            if len(remaining_files) > max_files:
                # Pega os arquivos mais antigos para remoção
                for filepath in remaining_files[:-(max_files)]:
                    try:
                        filepath.unlink()
                        removed += 1
                        if self.logger:
                            self.logger.debug(
                                f"Removido payload em excesso: {filepath}"
                            )
                    except Exception as e:
                        errors += 1
                        if self.logger:
                            self.logger.warning(
                                f"[{ErrorCode.LOG_RETENTION_CLEANUP_FAILED}] "
                                f"Falha ao remover arquivo em excesso {filepath}: {e}"
                            )
            
            # Remove diretórios vazios
            try:
                if source_dir.exists() and not any(source_dir.iterdir()):
                    source_dir.rmdir()
            except Exception as e:
                if self.logger:
                    self.logger.warning(
                        f"[{ErrorCode.LOG_RETENTION_CLEANUP_FAILED}] "
                        f"Falha ao remover diretório vazio {source_dir}: {e}"
                    )
            
            return removed, errors
            
        except Exception as e:
            error_msg = (
                f"[{ErrorCode.LOG_RETENTION_CLEANUP_FAILED}] "
                f"Erro durante a limpeza de payloads antigos: {e}"
            )
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            return removed, errors + 1
    
    def cleanup_all_old_payloads(
        self,
        max_files_per_source: int = 50,
        max_age_days: int = 30
    ) -> Dict[str, Tuple[int, int]]:
        """Limpa payloads antigos para todas as fontes.
        
        Args:
            max_files_per_source: Número máximo de arquivos por fonte
            max_age_days: Idade máxima em dias para manter os arquivos
            
        Returns:
            Dicionário com estatísticas de limpeza por fonte
        """
        if not self.base_dir.exists():
            return {}
        
        results = {}
        
        # Itera sobre todos os diretórios de fonte
        for source_dir in self.base_dir.iterdir():
            if source_dir.is_dir():
                source_name = source_dir.name
                removed, errors = self.cleanup_old_payloads(
                    source=source_name,
                    max_files=max_files_per_source,
                    max_age_days=max_age_days
                )
                results[source_name] = (removed, errors)
        
        return results
    
    def get_payload_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obtém estatísticas sobre os payloads armazenados.
        
        Returns:
            Dicionário com estatísticas por fonte
        """
        if not self.base_dir.exists():
            return {}
        
        stats = {}
        
        for source_dir in self.base_dir.iterdir():
            if source_dir.is_dir():
                source_name = source_dir.name
                file_count = 0
                total_size = 0
                oldest_file = None
                newest_file = None
                
                for filepath in source_dir.iterdir():
                    if filepath.is_file():
                        file_count += 1
                        file_size = filepath.stat().st_size
                        total_size += file_size
                        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                        
                        if oldest_file is None or mtime < oldest_file[1]:
                            oldest_file = (filepath.name, mtime)
                        if newest_file is None or mtime > newest_file[1]:
                            newest_file = (filepath.name, mtime)
                
                if file_count > 0:
                    stats[source_name] = {
                        'file_count': file_count,
                        'total_size': total_size,
                        'total_size_mb': total_size / (1024 * 1024),
                        'oldest_file': oldest_file[0] if oldest_file else None,
                        'oldest_mtime': oldest_file[1].isoformat() if oldest_file else None,
                        'newest_file': newest_file[0] if newest_file else None,
                        'newest_mtime': newest_file[1].isoformat() if newest_file else None
                    }
        
        return stats
