import math
from src.ai.embeddings_service import EmbeddingsService


def test_embeddings_service_determinism_and_shape():
    svc = EmbeddingsService(config=None, logger=None)
    texts = [
        "Formula 1 Grand Prix",
        "IMSA WeatherTech",
        "",
        None,
        "Formula 1 Grand Prix",  # repetido para checar cache/determinismo
    ]
    vecs = svc.embed_texts(texts)

    # Tamanho consistente
    assert isinstance(vecs, list)
    assert len(vecs) == len(texts)
    assert all(isinstance(v, list) for v in vecs)
    assert all(len(v) == svc.dim for v in vecs)

    # Normalização L2
    for v in vecs:
        norm = math.sqrt(sum(x * x for x in v))
        # vazio pode gerar vetor zero (norm 0), demais devem ser ~1.0
        if any(x != 0.0 for x in v):
            assert 0.99 <= norm <= 1.01

    # Determinismo (mesmo texto → mesmo vetor)
    assert vecs[0] == vecs[4]


def test_embeddings_service_similarity_reasonable():
    svc = EmbeddingsService(config=None, logger=None)
    a = "Formula 1 Grand Prix"
    b = "F1 Grand Prix"
    c = "World Rally Championship"
    va, vb, vc = svc.embed_texts([a, b, c])

    def cos(u, v):
        dot = sum(x*y for x, y in zip(u, v))
        nu = math.sqrt(sum(x*x for x in u))
        nv = math.sqrt(sum(y*y for y in v))
        return dot / (nu * nv) if nu > 0 and nv > 0 else 0.0

    sim_ab = cos(va, vb)
    sim_ac = cos(va, vc)

    assert sim_ab > sim_ac, (sim_ab, sim_ac)
