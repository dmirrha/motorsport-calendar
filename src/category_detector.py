"""
Dynamic Category Detection System for Motorsport Calendar

Intelligent system that automatically detects and classifies motorsport
categories from various data sources using fuzzy matching and machine learning.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any, Set
from pathlib import Path
from fuzzywuzzy import fuzz, process
from unidecode import unidecode
import jellyfish
import logging


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
        self.learned_variations = {}
        self.detection_stats = {}
        
        # Load custom mappings from config
        self._load_custom_mappings()
        
        self.logger.info("🎯 Category Detector initialized with dynamic learning")
    
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
            "NASCAR": [
                "nascar cup", "nascar xfinity", "nascar truck", "nascar series",
                "cup series", "xfinity series", "truck series"
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
                "campeonato mundial de endurance", "resistência"
            ],
            "IMSA": [
                "imsa", "imsa sportscar", "weathertech sportscar",
                "american endurance"
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
                "rallycross", "world rallycross", "rx", "mundial de rallycross"
            ],
            
            # Other Categories
            "Karting": [
                "karting", "kart", "go-kart", "kartismo"
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
                "F1", "F2", "F3", "F4", "FormulaE", "StockCar", "NASCAR",
                "IndyCar", "SuperFormula", "WEC", "IMSA", "LeMans", "DTM",
                "WTCR", "BTCC", "GTWorldChallenge", "SuperGT"
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
    
    def detect_category(self, raw_text: str, source: str = "unknown") -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect motorsport category from raw text.
        
        Args:
            raw_text: Raw category text from source
            source: Source name for tracking
            
        Returns:
            Tuple of (detected_category, confidence_score, metadata)
        """
        if not raw_text:
            return "Unknown", 0.0, {"raw_text": raw_text, "source": source}
        
        normalized_text = self.normalize_text(raw_text)
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
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "source": source,
            "best_match": best_match,
            "category_type": category_type,
            "confidence": best_score
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
    
    def batch_detect_categories(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect categories for a batch of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of events with detected categories
        """
        processed_events = []
        
        for event in events:
            raw_category = event.get('raw_category', event.get('category', ''))
            source = event.get('source', 'unknown')
            
            detected_category, confidence, metadata = self.detect_category(raw_category, source)
            
            # Update event with detected information
            updated_event = event.copy()
            updated_event.update({
                'category': detected_category,
                'category_type': metadata['category_type'],
                'category_confidence': confidence,
                'raw_category_text': raw_category,
                'category_metadata': metadata
            })
            
            processed_events.append(updated_event)
        
        return processed_events
    
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
    
    def detect_categories_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect categories for a batch of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of category detection results
        """
        category_results = []
        
        for event in events:
            # Use existing detect_category with a two-step approach:
            # 1) Tentar somente raw_category (prioriza match exato)
            # 2) Se vazio/baixo, tentar combinar com nome para melhorar sinal
            raw_category = event.get('raw_category', '') or event.get('category', '')
            event_name = event.get('name', '')

            detected_category = 'Unknown'
            confidence = 0.0

            if raw_category:
                cat1, conf1, _meta1 = self.detect_category(raw_category)
                detected_category, confidence = cat1, conf1

            # Se não atingiu threshold (ou vazio), tenta combinar com nome
            if (not raw_category or confidence < self.confidence_threshold) and (raw_category or event_name):
                combined = f"{raw_category} {event_name}".strip()
                if combined:
                    cat2, conf2, _meta2 = self.detect_category(combined)
                    # Escolhe o melhor por confiança
                    if conf2 > confidence:
                        detected_category, confidence = cat2, conf2
            
            # Return category information dictionary
            category_results.append({
                'category': detected_category,
                'confidence': confidence,
                'source': 'pattern_matching'
            })
        
        return category_results
