
#   Normaliza embeddings usando normalização L2.
#   similaridade de cosseno.

import numpy as np
def normalize_embeddings(embeddings):
    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )
    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True
    )
    # Evita divisão por zero
    norms = np.maximum(norms, 1e-12)
    return embeddings / norms