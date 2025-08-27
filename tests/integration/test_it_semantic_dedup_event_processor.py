import sys
import types
from datetime import datetime, timedelta

import numpy as np
import pytest


def _ensure_stubs():
    # fuzzywuzzy stub: ratio=100 only if strings are equal, else 0
    if 'fuzzywuzzy' not in sys.modules:
        mod = types.ModuleType('fuzzywuzzy')

        class _Fuzz:
            @staticmethod
            def ratio(a, b):
                return 100 if a == b else 0

        mod.fuzz = _Fuzz()

        class _Process:
            @staticmethod
            def extract(query, choices, *args, **kwargs):
                return []

            @staticmethod
            def extractOne(query, choices=None, *args, **kwargs):
                return None

        mod.process = _Process()
        sys.modules['fuzzywuzzy'] = mod

    # unidecode stub
    if 'unidecode' not in sys.modules:
        mod = types.ModuleType('unidecode')
        import unicodedata as _ud

        def _unidecode(s):
            try:
                return _ud.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
            except Exception:
                return str(s)

        mod.unidecode = _unidecode
        sys.modules['unidecode'] = mod


class StubEmbeddings:
    """Stub de Embeddings para controlar similaridades semânticas nos testes.

    O EventProcessor irá chamar embed_texts(texts) e calcular similaridade coseno.
    Aqui retornamos vetores unitários pré-definidos para garantir resultados previsíveis.
    """

    def __init__(self, mapping=None):
        # mapping: texto -> vetor numpy já normalizado
        if mapping is None:
            mapping = {}
        self.mapping = mapping

    def embed_texts(self, texts, batch_size=16):
        out = []
        for t in texts:
            v = self.mapping.get(str(t), None)
            if v is None:
                # padrão: vetor ortogonal para evitar similaridade incidental
                v = np.array([1.0, 0.0]) if len(out) % 2 == 0 else np.array([0.0, 1.0])
            # garantir normalização L2
            norm = np.linalg.norm(v) or 1.0
            out.append(v / norm)
        return np.vstack(out)


@pytest.mark.integration
class TestSemanticDedupIntegration:
    def setup_method(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        self.ep = EventProcessor()
        # garantir defaults estáveis
        self.ep.time_tolerance_minutes = 30
        self.now = datetime(2025, 8, 9, 12, 0, 0)

    def test_ai_disabled_does_not_use_semantic_similarity(self):
        # Nomes diferentes -> fuzzy=0 pelo stub
        a = {
            "name": "GP Brasil",
            "datetime": self.now,
            "detected_category": "Race",
            "location": "Interlagos",
        }
        b = {
            "name": "Grande Premio do Brasil",
            "datetime": self.now + timedelta(minutes=5),
            "detected_category": "Race",
            "location": "Interlagos",
        }

        # IA desabilitada: exigir threshold de nome alto para impedir dedupe
        self.ep.ai_enabled = False
        self.ep.similarity_threshold = 0.9
        assert self.ep._are_events_similar(a, b) is False

        # Pipeline de dedup não deve agrupar
        out = self.ep._deduplicate_events([a, b])
        assert len(out) == 2

    def test_ai_enabled_semantic_high_enables_dedup_even_with_low_fuzzy(self):
        # Names diferentes (fuzzy=0), mas semântica alta via stub
        a = {
            "name": "GP Brasil",
            "datetime": self.now,
            "detected_category": "Race",
            "streaming_links": ["http://a"],
            "source_priority": 10,
            "location": "Interlagos",
        }
        b = {
            "name": "Grande Premio do Brasil",
            "datetime": self.now + timedelta(minutes=10),
            "detected_category": "Race",
            "streaming_links": ["http://b"],
            "source_priority": 20,
            "official_url": "http://official",
            "location": "Interlagos",
        }

        # Mapear ambos os nomes para o MESMO vetor => similaridade coseno 1.0
        same_vec = np.array([0.6, 0.8])  # já normalizado (norm=1)
        stub = StubEmbeddings(
            mapping={
                "gp brasil": same_vec,
                "grande premio do brasil": same_vec,
                "interlagos": np.array([1.0, 0.0]),
            }
        )

        self.ep.ai_enabled = True
        self.ep.ai_dedup_threshold = 0.5  # permitir score composto
        self.ep.similarity_threshold = 0.9  # fuzzy exigente (0 com nomes diferentes)
        # Injetar stub de embeddings
        self.ep._embeddings_service = stub

        # Agora deve considerar similaridade semântica alta e agrupar
        assert self.ep._are_events_similar(a, b) is True

        out = self.ep._deduplicate_events([a, b])
        assert len(out) == 1
        merged = out[0]
        # Verificar merge básico
        assert set(merged.get("streaming_links", [])) == {"http://a", "http://b"}
        assert merged.get("official_url", "") in {"http://official", ""}
        # Best deve vir do maior source_priority (20)
        assert merged.get("source_priority") == 20

    def test_deterministic_selection_with_ai_enabled(self):
        # Três candidatos iguais no nome/tempo; prioridade decide e merge mantém links
        e1 = {
            "name": "Same",
            "datetime": self.now,
            "detected_category": "Race",
            "streaming_links": ["http://x"],
            "source_priority": 5,
            "location": "",
        }
        e2 = {
            "name": "Same",
            "datetime": self.now + timedelta(minutes=5),
            "detected_category": "Race",
            "streaming_links": [],
            "official_url": "http://mid",
            "source_priority": 50,
            "location": "",
        }
        e3 = {
            "name": "Same",
            "datetime": self.now + timedelta(minutes=10),
            "detected_category": "Race",
            "streaming_links": ["http://y"],
            "source_priority": 99,
            "location": "",
        }

        # IA ligada, mas nomes iguais já bastam; manter comportamento determinístico
        self.ep.ai_enabled = True
        # Com IA ligada e pesos 50/50, fuzzy=1.0 e semântico não garantido -> score=0.5.
        # Ajustamos o threshold para 0.5 para aceitar nomes idênticos de forma determinística.
        self.ep.ai_dedup_threshold = 0.5
        self.ep.similarity_threshold = 0.85
        self.ep._embeddings_service = StubEmbeddings()

        out1 = self.ep._deduplicate_events([e1, e2, e3])
        out2 = self.ep._deduplicate_events([e3, e1, e2])  # ordem diferente

        assert len(out1) == 1 and len(out2) == 1
        m1, m2 = out1[0], out2[0]
        # Maior prioridade vence
        assert m1.get("source_priority") == 99
        assert m2.get("source_priority") == 99
        # Links mesclados de forma estável
        assert set(m1.get("streaming_links", [])) == {"http://x", "http://y"}
        assert set(m2.get("streaming_links", [])) == {"http://x", "http://y"}
