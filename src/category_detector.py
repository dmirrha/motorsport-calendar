"""
Dynamic Category Detection System for Motorsport Calendar

Intelligent system that automatically detects and classifies motorsport
categories from various data sources using fuzzy matching and machine learning.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any, Set
from pathlib import Path
from fuzzywuzzy import fuzz
from unidecode import unidecode
import jellyfish
import logging
import math
from importlib import import_module


class CategoryDetector:
    """Intelligent motorsport category detection and classification system."""
    
    def __init__(self, config_manager=None, logger=None):
        """
        Initialize category detector.
        
        Args:
            config_manager: Configuration manager instance
            logger: Logger instance
        """
        self.config = config_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # Detection settings
        self.confidence_threshold = 0.7
        self.learning_enabled = True
        
        if self.config:
            self.confidence_threshold = self.config.get_category_confidence_threshold()
            self.learning_enabled = self.config.is_learning_mode_enabled()
        
        # Initialize knowledge base
        self.category_mappings = self._load_default_mappings()
        self.type_classifications = self._load_type_classifications()
        self.alias_map = self._load_alias_map()
        self.learned_variations = {}
        self.detection_stats = {}
        # AI / embeddings settings
        self.ai_enabled = False
        self.ai_category_threshold = 0.75
        self.ai_batch_size = 16
        self._embeddings_service = None
        self._semantic_ref_vectors: List[List[float]] = []
        self._semantic_ref_labels: List[str] = []
        self._semantic_label_to_category: Dict[str, str] = {}
        
        # Load custom mappings from config
        self._load_custom_mappings()
        
        # Load AI configs if available
        if self.config:
            try:
                self.ai_enabled = bool(self.config.get('ai.enabled', False))
                self.ai_category_threshold = float(self.config.get('ai.thresholds.category', 0.75))
                self.ai_batch_size = int(self.config.get('ai.batch_size', 16))
            except Exception:
                # Mantém defaults se houver qualquer problema de leitura
                pass

        self.logger.info("🎯 Category Detector initialized with dynamic learning")

    # --- Semantic categorization helpers ---
    def _ensure_embeddings_service(self) -> bool:
        """Lazy-load do EmbeddingsService se disponível. Retorna True se ok."""
        if self._embeddings_service is not None:
            return True
        # Import dinâmico tolerante a diferentes layouts
        EmbeddingsService = None
        for mod_name in ('src.ai.embeddings_service', 'ai.embeddings_service'):
            try:
                mod = import_module(mod_name)
                EmbeddingsService = getattr(mod, 'EmbeddingsService', None)
                if EmbeddingsService:
                    break
            except Exception:
                continue
        if not EmbeddingsService:
            if self.logger:
                self.logger.warning("🤖 AI.enabled=true, mas EmbeddingsService não encontrado; usando heurísticas.")
            return False
        try:
            # Instancia sem parâmetros obrigatórios; serviço lê config internamente se necessário
            self._embeddings_service = EmbeddingsService(config=self.config, logger=self.logger)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Falha ao inicializar EmbeddingsService: {e}")
            self._embeddings_service = None
            return False

    def _build_semantic_references(self) -> None:
        """Gera e cacheia embeddings de referência para categorias e aliases."""
        if self._semantic_ref_vectors:
            return
        if not self._ensure_embeddings_service():
            return
        # Coleta textos únicos (categoria canônica + variações)
        texts: List[str] = []
        labels: List[str] = []
        label_to_category: Dict[str, str] = {}
        seen: Set[str] = set()
        for category, variations in self.category_mappings.items():
            # inclui o nome da categoria canônica
            candidates = [category] + list(variations)
            for t in candidates:
                norm = self.normalize_text(t)
                if not norm or norm in seen:
                    continue
                seen.add(norm)
                texts.append(norm)
                labels.append(norm)
                label_to_category[norm] = category
        if not texts:
            return
        try:
            vectors = self._embeddings_service.embed_texts(texts)
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erro ao gerar embeddings de referência: {e}")
            return
        # Cache
        self._semantic_ref_vectors = vectors
        self._semantic_ref_labels = labels
        self._semantic_label_to_category = label_to_category

    @staticmethod
    def _cosine_sim(u: List[float], v: List[float]) -> float:
        """Similaridade do cosseno sem dependências externas."""
        if not u or not v or len(u) != len(v):
            return 0.0
        dot = 0.0
        nu = 0.0
        nv = 0.0
        for a, b in zip(u, v):
            dot += a * b
            nu += a * a
            nv += b * b
        den = math.sqrt(nu) * math.sqrt(nv)
        return (dot / den) if den > 0 else 0.0
    
    def _load_alias_map(self) -> Dict[str, str]:
        """Load canonical alias mapping (normalized alias -> canonical category)."""
        alias_pairs = {
            # Open wheel
            "f indy": "IndyCar",
            "findy": "IndyCar",
            "f-indy": "IndyCar",
            # Trucks
            "f truck": "CopaTruck",
            "f-truck": "CopaTruck",
            "formula truck": "FormulaTruck",
            # Endurance
            "imsa weathertech": "IMSA",
            "weathertech sportscar": "IMSA",
            "fia wec": "WEC",
            "prototipos": "WEC",
            "prototypes": "WEC",
            # Rallycross
            "wrx": "Rallycross",
            # Touring / Stock
            "stock series": "StockCar",
        }
        # Normalize keys once to ensure stable lookups
        normalized_aliases: Dict[str, str] = {}
        for k, v in alias_pairs.items():
            normalized_aliases[self.normalize_text(k)] = v
        return normalized_aliases

    def _load_default_mappings(self) -> Dict[str, List[str]]:
        """Load default category mappings."""
        return {
            # Formula Series
            "F1": [
                "formula 1", "formula one", "fórmula 1", "grand prix", "gp", "f-1",
                "formula1", "f1 grand prix", "grande prêmio", "campeonato mundial"
            ],
            "F2": [
                "formula 2", "fórmula 2", "f-2", "formula2", "f2 championship"
            ],
            "F3": [
                "formula 3", "fórmula 3", "f-3", "formula3", "f3 championship"
            ],
            "F4": [
                "formula 4", "fórmula 4", "f-4", "formula4"
            ],
            "F1Academy": [
                "f1 academy", "formula 1 academy", "f-1 academy", "academia f1"
            ],
            "FormulaE": [
                "formula e", "fórmula e", "fe", "electric formula", "e-prix",
                "formula elétrica", "campeonato de formula e"
            ],
            
            # Motorcycle Series
            "MotoGP": [
                "moto gp", "motogp", "moto grand prix", "premier class",
                "world championship", "campeonato mundial de motociclismo"
            ],
            "Moto2": [
                "moto 2", "moto2", "intermediate class", "classe intermediária"
            ],
            "Moto3": [
                "moto 3", "moto3", "lightweight class", "classe leve"
            ],
            "MotoE": [
                "moto e", "motoe", "electric motorcycle", "moto elétrica"
            ],
            "WSBK": [
                "world superbike", "superbike world championship", "sbk",
                "mundial de superbike", "campeonato mundial de superbike"
            ],
            "Supersport": [
                "supersport", "world supersport", "mundial de supersport"
            ],
            
            # Stock Car and NASCAR
            "StockCar": [
                "stock car brasil", "stock car", "scb", "stock car championship",
                "campeonato de stock car"
            ],
            "CopaTruck": [
                "copa truck", "copa truck brasil", "truck series brasil"
            ],
            "FormulaTruck": [
                "formula truck", "fórmula truck", "f-truck", "f truck"
            ],
            "NASCAR": [
                "nascar cup", "nascar xfinity", "nascar truck", "nascar series",
                "cup series", "xfinity series", "truck series", "nascar cup series"
            ],
            
            # IndyCar and Open Wheel
            "IndyCar": [
                "indycar", "indy car", "indycar series", "indy 500",
                "indianapolis 500", "championship series"
            ],
            "SuperFormula": [
                "super formula", "super fórmula", "japanese formula",
                "fórmula japonesa"
            ],
            
            # Endurance Racing
            "WEC": [
                "world endurance championship", "wec", "le mans", "endurance",
                "campeonato mundial de endurance", "resistência", "fia wec",
                "prototipos", "prototypes"
            ],
            "IMSA": [
                "imsa", "imsa sportscar", "weathertech sportscar",
                "american endurance", "imsa weathertech"
            ],
            "LeMans": [
                "le mans", "24 hours of le mans", "24h le mans",
                "24 horas de le mans"
            ],
            
            # Touring Cars
            "DTM": [
                "dtm", "deutsche tourenwagen masters", "german touring car",
                "turismo alemão"
            ],
            "WTCR": [
                "wtcr", "world touring car", "touring car world cup",
                "copa do mundo de carros de turismo"
            ],
            "BTCC": [
                "btcc", "british touring car", "touring car championship"
            ],
            
            # GT Racing
            "GTWorldChallenge": [
                "gt world challenge", "gt championship", "gt racing",
                "grand touring", "gt3", "gt4"
            ],
            "SuperGT": [
                "super gt", "japanese gt", "gt japonês"
            ],
            
            # Rally
            "WRC": [
                "world rally championship", "wrc", "rally championship",
                "campeonato mundial de rally", "mundial de rally"
            ],
            "Rallycross": [
                "rallycross", "world rallycross", "rx", "mundial de rallycross",
                "wrx"
            ],
            
            # Other Categories
            "Karting": [
                "karting", "kart", "go-kart", "kartismo"
            ],
            "TurismoNacional": [
                "turismo nacional", "tn", "campeonato turismo nacional"
            ],
            "Drift": [
                "drift", "drifting", "formula drift", "drift championship"
            ],
            "Autocross": [
                "autocross", "auto cross", "slalom"
            ],
            "Hillclimb": [
                "hill climb", "hillclimb", "subida de montanha", "montanha"
            ],
            "TimeAttack": [
                "time attack", "time trial", "contra-relógio"
            ]
        }
    
    def _load_type_classifications(self) -> Dict[str, List[str]]:
        """Load category type classifications."""
        return {
            "cars": [
                "F1", "F2", "F3", "F4", "F1Academy", "FormulaE", "StockCar",
                "CopaTruck", "FormulaTruck", "NASCAR", "IndyCar", "SuperFormula",
                "WEC", "IMSA", "LeMans", "DTM", "WTCR", "BTCC",
                "GTWorldChallenge", "SuperGT", "TurismoNacional"
            ],
            "motorcycles": [
                "MotoGP", "Moto2", "Moto3", "MotoE", "WSBK", "Supersport"
            ],
            "mixed": [
                "WRC", "Rallycross"
            ],
            "other": [
                "Karting", "Drift", "Autocross", "Hillclimb", "TimeAttack"
            ]
        }
    
    def _load_custom_mappings(self) -> None:
        """Load custom mappings from configuration."""
        if not self.config:
            return
        
        custom_mappings = self.config.get('category_mapping.custom_mappings', {})
        if custom_mappings:
            # Merge custom mappings with defaults
            for category, variations in custom_mappings.items():
                if category in self.category_mappings:
                    # Add to existing category
                    self.category_mappings[category].extend(variations)
                else:
                    # New category
                    self.category_mappings[category] = variations
            
            self.logger.info(f"📚 Loaded {len(custom_mappings)} custom category mappings")
        
        # Load custom type classifications
        custom_types = self.config.get('category_mapping.type_classification', {})
        if custom_types:
            self.type_classifications.update(custom_types)
            self.logger.info(f"🏷️ Loaded custom type classifications")
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for better matching.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase and remove accents
        normalized = unidecode(text.lower())
        
        # Remove common noise words and characters
        noise_patterns = [
            r'\b(championship|campeonato|mundial|world|series|cup|copa)\b',
            r'\b(de|da|do|of|the)\b',
            r'[^\w\s]',  # Remove punctuation
            r'\s+',      # Multiple spaces to single space
        ]
        
        for pattern in noise_patterns:
            normalized = re.sub(pattern, ' ', normalized)
        
        return normalized.strip()
    
    def detect_category(self, raw_text: str, source: str = "unknown", context: Optional[Dict[str, Any]] = None) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect motorsport category from raw text.
        
        Args:
            raw_text: Raw category text from source
            source: Source name for tracking
            context: Optional additional context (e.g., name, display_name, location, country,
                     session_type, official_url, page_title, page_url, date, timezone)
        
        Returns:
            Tuple of (detected_category, confidence_score, metadata)
        """
        # Prepare context-aware input
        orig_raw_text = raw_text or ""
        context_used = False
        used_context_fields: List[str] = []
        context_combined_snippets: List[str] = []

        if context and isinstance(context, dict):
            # Common, useful context keys
            candidate_keys = [
                "name", "display_name", "page_title", "page_url", "official_url",
                "location", "country", "session_type", "date", "timezone"
            ]
            for k in candidate_keys:
                v = context.get(k)
                if isinstance(v, (str, int, float)) and str(v).strip():
                    context_combined_snippets.append(str(v).strip())
                    used_context_fields.append(k)
            if context_combined_snippets:
                # Combine raw_text with context to strengthen matching
                combined = (orig_raw_text + " " + " ".join(context_combined_snippets)).strip()
                raw_text = combined
                context_used = True

        # If nothing to match (and no context provided meaningful text)
        if not raw_text:
            return "Unknown", 0.0, {
                "raw_text": orig_raw_text,
                "raw_text_combined": raw_text,
                "source": source,
                "context_used": context_used,
                "context_fields": used_context_fields,
            }

        # Alias mapping shortcut based on the original raw text when available
        normalized_text_original = self.normalize_text(orig_raw_text)
        if normalized_text_original and normalized_text_original in self.alias_map:
            best_category = self.alias_map[normalized_text_original]
            best_score = 0.95  # high-confidence alias mapping
            metadata = {
                "raw_text": orig_raw_text,
                "raw_text_combined": raw_text,
                "normalized_text": normalized_text_original,
                "source": source,
                "best_match": "alias",
                "category_type": self._get_category_type(best_category),
                "confidence": best_score,
                "context_used": context_used,
                "context_fields": used_context_fields,
            }
            self._update_stats(source, best_category, best_score)
            if self.logger:
                self.logger.debug(
                    f"🏷️ Alias mapped: '{orig_raw_text}' → '{best_category}' (confidence: {best_score:.2f})"
                )
            return best_category, best_score, metadata

        normalized_text = self.normalize_text(raw_text)
        # 0) Alias mapping shortcut (exact normalized form) on the combined text
        if normalized_text in self.alias_map:
            best_category = self.alias_map[normalized_text]
            best_score = 0.95  # high-confidence alias mapping
            metadata = {
                "raw_text": orig_raw_text,
                "raw_text_combined": raw_text,
                "normalized_text": normalized_text,
                "source": source,
                "best_match": "alias",
                "category_type": self._get_category_type(best_category),
                "confidence": best_score,
                "context_used": context_used,
                "context_fields": used_context_fields,
            }
            self._update_stats(source, best_category, best_score)
            if self.logger:
                self.logger.debug(
                    f"🏷️ Alias mapped (combined): '{raw_text}' → '{best_category}' (confidence: {best_score:.2f})"
                )
            return best_category, best_score, metadata
        best_match = None
        best_score = 0.0
        best_category = "Unknown"
        
        # Try exact matching first
        exact_match_found = False
        for category, variations in self.category_mappings.items():
            for variation in variations:
                normalized_variation = self.normalize_text(variation)
                
                # Exact match
                if normalized_text == normalized_variation:
                    best_category = category
                    best_score = 1.0
                    best_match = variation
                    exact_match_found = True
                    break
                
                # Fuzzy matching
                similarity_scores = [
                    fuzz.ratio(normalized_text, normalized_variation) / 100.0,
                    fuzz.partial_ratio(normalized_text, normalized_variation) / 100.0,
                    fuzz.token_sort_ratio(normalized_text, normalized_variation) / 100.0,
                    fuzz.token_set_ratio(normalized_text, normalized_variation) / 100.0
                ]
                
                max_score = max(similarity_scores)
                
                # Não sobrescrever um match exato já encontrado
                if not exact_match_found and max_score > best_score:
                    best_score = max_score
                    best_category = category
                    best_match = variation
            
            # Só interrompe quando o match exato for encontrado
            if exact_match_found:
                break
        
        # Additional fuzzy matching with Jaro-Winkler
        if best_score < 0.9 and not exact_match_found:
            for category, variations in self.category_mappings.items():
                for variation in variations:
                    normalized_variation = self.normalize_text(variation)
                    jw_score = jellyfish.jaro_winkler_similarity(normalized_text, normalized_variation)
                    
                    if jw_score > best_score:
                        best_score = jw_score
                        best_category = category
                        best_match = variation
        
        # Learn new variations if enabled and confidence is high
        if (self.learning_enabled and best_score >= self.confidence_threshold 
            and best_score < 1.0 and normalized_text not in 
            [self.normalize_text(v) for v in self.category_mappings.get(best_category, [])]):
            
            self._learn_variation(best_category, raw_text, best_score)
        
        # Update detection stats
        self._update_stats(source, best_category, best_score)
        
        # Determine category type
        category_type = self._get_category_type(best_category)
        
        metadata = {
            "raw_text": orig_raw_text,
            "raw_text_combined": raw_text,
            "normalized_text": normalized_text,
            "source": source,
            "best_match": best_match,
            "category_type": category_type,
            "confidence": best_score,
            "context_used": context_used,
            "context_fields": used_context_fields,
        }
        
        if self.logger:
            self.logger.debug(f"🎯 Category detected: '{raw_text}' → '{best_category}' "
                            f"(confidence: {best_score:.2f}, type: {category_type})")
        
        return best_category, best_score, metadata
    
    def _get_category_type(self, category: str) -> str:
        """
        Get the type classification for a category.
        
        Args:
            category: Category name
            
        Returns:
            Category type (cars, motorcycles, mixed, other)
        """
        for category_type, categories in self.type_classifications.items():
            if category in categories:
                return category_type
        return "other"
    
    def _learn_variation(self, category: str, variation: str, confidence: float) -> None:
        """
        Learn a new variation for a category.
        
        Args:
            category: Category name
            variation: New variation to learn
            confidence: Confidence score
        """
        if category not in self.learned_variations:
            self.learned_variations[category] = []
        
        # Add to learned variations
        self.learned_variations[category].append({
            "variation": variation,
            "confidence": confidence,
            "learned_at": "2024-08-01"  # Would use actual timestamp
        })
        
        # Add to active mappings
        if category in self.category_mappings:
            self.category_mappings[category].append(variation)
        
        if self.logger:
            self.logger.info(f"📚 Learned new variation: '{variation}' → '{category}' "
                           f"(confidence: {confidence:.2f})")
    
    def _update_stats(self, source: str, category: str, confidence: float) -> None:
        """Update detection statistics."""
        if source not in self.detection_stats:
            self.detection_stats[source] = {}
        
        if category not in self.detection_stats[source]:
            self.detection_stats[source][category] = {
                "count": 0,
                "total_confidence": 0.0,
                "avg_confidence": 0.0
            }
        
        stats = self.detection_stats[source][category]
        stats["count"] += 1
        stats["total_confidence"] += confidence
        stats["avg_confidence"] = stats["total_confidence"] / stats["count"]
    
    def batch_detect_categories(self, events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        DEPRECATED wrapper mantido por compatibilidade, mas com comportamento
        de enriquecimento esperado pelos testes legados.

        Diferente de `detect_categories_batch`, este método retorna a lista de
        eventos enriquecidos, adicionando:
          - 'category'
          - 'category_type'
          - 'category_confidence'
          - 'raw_category_text'
          - 'category_metadata' (inclui metadados retornados pelo detector)

        Observação importante: quando 'raw_category' estiver presente, evitamos
        combinar contexto no texto de detecção para preservar matches exatos
        (ex.: 'MotoGP' → 1.0), conforme esperado pelos testes.
        """
        if self.logger:
            try:
                self.logger.debug("batch_detect_categories() is deprecated; kept for legacy enriched output")
            except Exception:
                pass

        enriched: List[Dict[str, Any]] = []

        for event in events:
            raw_category = event.get('raw_category', '') or event.get('category', '')
            event_name = event.get('name', '') or event.get('display_name', '')
            source_name = event.get('source', 'unknown')

            # Monta contexto por-evento, mas só será passado quando NÃO houver raw_category
            per_event_context: Dict[str, Any] = {
                'name': event_name,
                'display_name': event.get('display_name', ''),
                'official_url': event.get('official_url', ''),
                'timezone': event.get('timezone', ''),
                'country': event.get('country', ''),
                'location': event.get('location', ''),
                'session_type': event.get('session_type', ''),
                'date': event.get('date', ''),
            }

            # Mescla contexto aninhado em raw_data.category_context, se houver
            try:
                raw_data = event.get('raw_data', {}) or {}
                category_context = raw_data.get('category_context', {}) if isinstance(raw_data, dict) else {}
                if isinstance(category_context, dict):
                    for k in [
                        'page_title', 'page_url', 'official_url', 'location', 'country',
                        'session_type'
                    ]:
                        if k in category_context and category_context[k]:
                            per_event_context[k] = category_context[k]
            except Exception:
                pass

            # Contexto global (raro)
            if context and isinstance(context, dict):
                per_event_context.update({k: v for k, v in context.items() if v})

            # Texto principal: se houver raw_category, prioriza e NÃO combina contexto
            primary_text = raw_category if raw_category else event_name
            context_to_pass = None if raw_category else per_event_context

            cat, conf, meta = self.detect_category(primary_text, source=source_name, context=context_to_pass)

            # Monta saída enriquecida no próprio evento (sem mutar o original in-place)
            out_ev = dict(event)
            out_ev['category'] = cat
            out_ev['category_type'] = meta.get('category_type', self._get_category_type(cat))
            out_ev['category_confidence'] = float(meta.get('confidence', conf)) if isinstance(meta.get('confidence', conf), (int, float)) else conf
            out_ev['raw_category_text'] = raw_category
            category_metadata = dict(meta)
            # Garante presença do nome da fonte
            category_metadata['source'] = source_name
            out_ev['category_metadata'] = category_metadata

            enriched.append(out_ev)

        return enriched
    
    def get_detected_categories_summary(self) -> Dict[str, Any]:
        """
        Get summary of detected categories.
        
        Returns:
            Dictionary with category detection summary
        """
        summary = {}
        
        for source, categories in self.detection_stats.items():
            for category, stats in categories.items():
                if category not in summary:
                    summary[category] = {
                        "type": self._get_category_type(category),
                        "event_count": 0,
                        "sources": [],
                        "confidence": 0.0,
                        "confidence_scores": []
                    }
                
                summary[category]["event_count"] += stats["count"]
                summary[category]["sources"].append(source)
                summary[category]["confidence_scores"].append(stats["avg_confidence"])
        
        # Calculate average confidence across sources
        for category in summary:
            if summary[category]["confidence_scores"]:
                summary[category]["confidence"] = sum(summary[category]["confidence_scores"]) / len(summary[category]["confidence_scores"])
            summary[category]["sources"] = list(set(summary[category]["sources"]))
        
        return summary
    
    def filter_by_confidence(self, events: List[Dict[str, Any]], 
                           min_confidence: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Filter events by category detection confidence.
        
        Args:
            events: List of events
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered list of events
        """
        threshold = min_confidence or self.confidence_threshold
        
        filtered_events = []
        for event in events:
            confidence = event.get('category_confidence', 0.0)
            if confidence >= threshold:
                filtered_events.append(event)
            elif self.logger:
                self.logger.warning(f"⚠️ Event filtered due to low confidence: "
                                  f"'{event.get('name', 'Unknown')}' "
                                  f"(confidence: {confidence:.2f})")
        
        return filtered_events
    
    def save_learned_categories(self, filepath: str = "learned_categories.json") -> None:
        """
        Save learned categories to file.
        
        Args:
            filepath: Path to save learned categories
        """
        try:
            learned_data = {
                "learned_variations": self.learned_variations,
                "detection_stats": self.detection_stats,
                "updated_mappings": {k: v for k, v in self.category_mappings.items() 
                                   if k in self.learned_variations}
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(learned_data, f, indent=2, ensure_ascii=False)
            
            if self.logger:
                self.logger.info(f"💾 Learned categories saved to {filepath}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to save learned categories: {e}")
    
    def load_learned_categories(self, filepath: str = "learned_categories.json") -> None:
        """
        Load previously learned categories from file.
        
        Args:
            filepath: Path to learned categories file
        """
        try:
            if not Path(filepath).exists():
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                learned_data = json.load(f)
            
            # Merge learned variations
            if "learned_variations" in learned_data:
                for category, variations in learned_data["learned_variations"].items():
                    if category not in self.learned_variations:
                        self.learned_variations[category] = []
                    self.learned_variations[category].extend(variations)
            
            # Merge updated mappings
            if "updated_mappings" in learned_data:
                for category, variations in learned_data["updated_mappings"].items():
                    if category in self.category_mappings:
                        self.category_mappings[category].extend(variations)
                    else:
                        self.category_mappings[category] = variations
            
            if self.logger:
                self.logger.info(f"📚 Learned categories loaded from {filepath}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to load learned categories: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detection statistics.
        
        Returns:
            Dictionary with detection statistics
        """
        total_detections = sum(
            sum(stats["count"] for stats in categories.values())
            for categories in self.detection_stats.values()
        )
        
        unique_categories = set()
        for categories in self.detection_stats.values():
            unique_categories.update(categories.keys())
        
        learned_count = sum(len(variations) for variations in self.learned_variations.values())
        
        return {
            "total_detections": total_detections,
            "unique_categories": len(unique_categories),
            "categories_detected": sorted(list(unique_categories)),
            "learned_variations": learned_count,
            "sources_processed": len(self.detection_stats),
            "confidence_threshold": self.confidence_threshold,
            "learning_enabled": self.learning_enabled
        }
    
    def detect_categories_batch(self, events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Detect categories for a batch of events.
        
        Args:
            events: List of event dictionaries
            context: Optional global context to be applied to all items (rarely used)
        
        Returns:
            List of category detection results
        """
        category_results = []

        # Caminho semântico (opt-in)
        if self.ai_enabled:
            # Garante que o serviço e referências estão prontos; caso contrário, cai em heurística
            self._build_semantic_references()
            if self._embeddings_service and self._semantic_ref_vectors:
                # Prepara textos do batch
                batch_texts: List[str] = []
                per_event_payload: List[Dict[str, Any]] = []
                for event in events:
                    raw_category = event.get('raw_category', '') or event.get('category', '')
                    event_name = event.get('name', '') or event.get('display_name', '')

                    per_event_context: Dict[str, Any] = {
                        'name': event_name,
                        'display_name': event.get('display_name', ''),
                        'official_url': event.get('official_url', ''),
                        'timezone': event.get('timezone', ''),
                        'country': event.get('country', ''),
                        'location': event.get('location', ''),
                        'session_type': event.get('session_type', ''),
                        'date': event.get('date', ''),
                    }
                    # Merge optional nested context
                    try:
                        raw_data = event.get('raw_data', {}) or {}
                        category_context = raw_data.get('category_context', {}) if isinstance(raw_data, dict) else {}
                        if isinstance(category_context, dict):
                            for k in [
                                'page_title', 'page_url', 'official_url', 'location', 'country',
                                'session_type'
                            ]:
                                if k in category_context and category_context[k]:
                                    per_event_context[k] = category_context[k]
                    except Exception:
                        pass
                    # Merge global context
                    if context and isinstance(context, dict):
                        per_event_context.update({k: v for k, v in context.items() if v})

                    primary_text = raw_category if raw_category else event_name
                    # Preserva regra: se há raw_category, não combina contexto
                    if raw_category:
                        text_for_semantic = primary_text
                    else:
                        # Evita duplicar o 'name'/'display_name' no contexto e valores idênticos ao primary_text
                        ctx_vals: List[str] = []
                        for k, v in per_event_context.items():
                            if not v:
                                continue
                            s = str(v).strip()
                            if not s:
                                continue
                            if k in ("name", "display_name"):
                                continue
                            if s == primary_text:
                                continue
                            ctx_vals.append(s)
                        text_for_semantic = (primary_text + " " + " ".join(ctx_vals)).strip()
                    norm_text = self.normalize_text(text_for_semantic)
                    batch_texts.append(norm_text)
                    per_event_payload.append({
                        'has_raw': bool(raw_category),
                    })

                # Embeddings do batch
                try:
                    batch_vecs = self._embeddings_service.embed_texts(batch_texts)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"❌ Erro ao gerar embeddings do batch: {e}")
                    batch_vecs = None

                if batch_vecs is not None:
                    # Similaridade vs referências
                    for vec, payload in zip(batch_vecs, per_event_payload):
                        best_cat = 'Unknown'
                        best_score = 0.0
                        # varre todas referências
                        for ref_vec, label in zip(self._semantic_ref_vectors, self._semantic_ref_labels):
                            score = self._cosine_sim(vec, ref_vec)
                            if score > best_score:
                                best_score = score
                                best_cat = self._semantic_label_to_category.get(label, 'Unknown')
                        if best_score >= self.ai_category_threshold and best_cat != 'Unknown':
                            if self.logger:
                                try:
                                    self.logger.debug(f"🧠 Semantic match: '{best_cat}' (score={best_score:.3f} ≥ thr={self.ai_category_threshold:.2f})")
                                except Exception:
                                    pass
                            category_results.append({'category': best_cat, 'confidence': float(best_score), 'source': 'semantic'})
                        else:
                            # Fallback para heurística padrão
                            use_source = 'pattern_matching' if payload.get('has_raw') else 'pattern_matching+context'
                            category_results.append({'category': 'Unknown', 'confidence': 0.0, 'source': use_source})
                    # Após preencher resultados, executa uma segunda passada de fallback para desconhecidos
                    # Chamando detect_category apenas nos que ficaram Unknown
                    for idx, res in enumerate(category_results):
                        if res['category'] == 'Unknown':
                            event = events[idx]
                            raw_category = event.get('raw_category', '') or event.get('category', '')
                            event_name = event.get('name', '') or event.get('display_name', '')
                            source_name = event.get('source', 'unknown')

                            per_event_context: Dict[str, Any] = {
                                'name': event_name,
                                'display_name': event.get('display_name', ''),
                                'official_url': event.get('official_url', ''),
                                'timezone': event.get('timezone', ''),
                                'country': event.get('country', ''),
                                'location': event.get('location', ''),
                                'session_type': event.get('session_type', ''),
                                'date': event.get('date', ''),
                            }
                            try:
                                raw_data = event.get('raw_data', {}) or {}
                                category_context = raw_data.get('category_context', {}) if isinstance(raw_data, dict) else {}
                                if isinstance(category_context, dict):
                                    for k in [
                                        'page_title', 'page_url', 'official_url', 'location', 'country',
                                        'session_type'
                                    ]:
                                        if k in category_context and k not in per_event_context and category_context[k]:
                                            per_event_context[k] = category_context[k]
                            except Exception:
                                pass
                            if context and isinstance(context, dict):
                                per_event_context.update({k: v for k, v in context.items() if v})
                            primary_text = raw_category if raw_category else event_name
                            context_to_pass = None if raw_category else per_event_context
                            cat, conf, _meta = self.detect_category(primary_text, source=source_name, context=context_to_pass)
                            res['category'] = cat
                            res['confidence'] = conf
                            res['source'] = 'pattern_matching' if raw_category else 'pattern_matching+context'

                    return category_results

        # Caminho heurístico padrão (AI desativado ou indisponível)
        for event in events:
            # Build per-event context and detect using context-aware API
            raw_category = event.get('raw_category', '') or event.get('category', '')
            event_name = event.get('name', '') or event.get('display_name', '')
            source_name = event.get('source', 'unknown')

            per_event_context: Dict[str, Any] = {
                'name': event_name,
                'display_name': event.get('display_name', ''),
                'official_url': event.get('official_url', ''),
                'timezone': event.get('timezone', ''),
                'country': event.get('country', ''),
                'location': event.get('location', ''),
                'session_type': event.get('session_type', ''),
                'date': event.get('date', ''),
            }
            # Merge optional nested context from raw_data.category_context if provided
            try:
                raw_data = event.get('raw_data', {}) or {}
                category_context = raw_data.get('category_context', {}) if isinstance(raw_data, dict) else {}
                if isinstance(category_context, dict):
                    for k in [
                        'page_title', 'page_url', 'official_url', 'location', 'country',
                        'session_type'
                    ]:
                        if k in category_context and category_context[k]:
                            per_event_context[k] = category_context[k]
            except Exception:
                pass

            # Merge any global context provided (rare)
            if context and isinstance(context, dict):
                per_event_context.update({k: v for k, v in context.items() if v})

            # Choose the primary text to detect from
            primary_text = raw_category if raw_category else event_name
            # Important: if we have a raw_category, avoid combining context to preserve exact matches
            context_to_pass = None if raw_category else per_event_context
            cat, conf, _meta = self.detect_category(primary_text, source=source_name, context=context_to_pass)

            # Fonte deve refletir se contexto foi utilizado ou não
            use_source = 'pattern_matching' if raw_category else 'pattern_matching+context'
            category_results.append({
                'category': cat,
                'confidence': conf,
                'source': use_source
            })

        return category_results
