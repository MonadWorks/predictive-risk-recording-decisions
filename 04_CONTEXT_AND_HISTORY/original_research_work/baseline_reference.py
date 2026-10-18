"""Independent mathematical reference; no upstream implementation is copied.

Sources: Beiran & Litwin-Kumar (2025), DOI 10.1038/s41593-025-02080-4.
The block finite-time extension is our adaptation of the local noiseless geometry.
Run this module directly for small algebraic checks only.
"""
import json
import numpy as np


def block_svd_greedy(blocks, target, budget, rtol=1e-8, atol=1e-12):
    """Select neuron blocks from a local, noiseless Euclidean geometry.

    blocks[i]: observations-by-parameters sensitivity for candidate neuron i.
    target: full target/activity-by-parameters sensitivity in the same coordinates.
    Optional prior whitening MUST be done consistently by the caller on BOTH.
    No noise, prior-precision update or soft information weighting is implied.
    rtol is relative to each original block's largest singular value, so it
    does not amplify projected numerical residue into new information.
    """
    blocks = [np.asarray(b, float) for b in blocks]
    target = np.asarray(target, float)
    p = target.shape[1]
    if not 0 <= budget <= len(blocks):
        raise ValueError("Invalid recording budget")
    scale = [np.linalg.norm(b, 2) if b.size else 0.0 for b in blocks]
    P = np.eye(p)
    selected, history = [], []
    target_energy = np.sum(target ** 2)
    denominator = max(target_energy, np.finfo(float).tiny)
    for _ in range(budget):
        candidates = []
        for i, b in enumerate(blocks):
            if i in selected:
                continue
            _, singular, vh = np.linalg.svd(b @ P, full_matrices=False)
            rank = int(np.sum(singular > max(atol, rtol * scale[i])))
            V = vh[:rank].T
            score = np.sum((target @ V) ** 2) / denominator
            candidates.append((float(score), -i, V, rank))
        score, negative_i, V, rank = max(candidates, key=lambda x: (x[0], x[1]))
        i = -negative_i
        selected.append(i)
        P -= V @ V.T
        P = (P + P.T) / 2
        history.append({"candidate": i, "incremental_rank": rank,
                        "score": score,
                        "residual_risk": float(np.sum((target @ P) ** 2) / denominator),
                        "projector_defect": float(np.linalg.norm(P @ P-P))})
    return selected, history


def make_rank_two(seed=0, n=100):
    """Published Fig.3 family distribution; our RNG, not bitwise reproduction.

    Uses N(1,.9^2) gains (negative allowed), zero biases, rank-two J.
    Returns factors so callers can avoid dense J in simulation/sensitivities.
    The source's extra 1.1 diagonal inflation on the first PSD iteration is
    represented explicitly here; this is distribution specification, not code reuse.
    """
    rng = np.random.default_rng(seed)
    C = np.eye(4)
    C[:2, 2:] = np.array([[1.5, 3.0], [-3.0, 1.5]])
    C[2:, :2] = C[:2, 2:].T
    count = 0
    while np.linalg.eigvalsh(C).min() < 0:
        C[2:, 2:] *= 1.1
        count += 1
        if count > 100:
            raise RuntimeError("Covariance inflation did not reach PSD")
    C[2:, 2:] *= 1.1
    draw = rng.multivariate_normal(np.zeros(4), C, size=n)
    M, H = draw[:, :2], draw[:, 2:]
    gains = 1 + .9 * rng.normal(size=n)
    return M, H, gains, C


def rank_two_step(x, M, H, gains, u=0.0, dt=.05, tau=.5):
    return x + dt / tau * (-x + M @ (H.T @ (gains * np.tanh(x))) / len(x) + u)


def checks():
    rng = np.random.default_rng(20261016)
    # Scalar F=G=A must agree with the normalized-row SVD expression.
    A = rng.normal(size=(8, 5))
    _, s, vh = np.linalg.svd(A, full_matrices=False)
    normalized = A / np.linalg.norm(A, axis=1, keepdims=True)
    published_scores = np.sum(((normalized @ vh.T) * s) ** 2, axis=1) / np.sum(s*s)
    order, hist = block_svd_greedy([r[None, :] for r in A], A, 5)
    assert order[0] == int(np.argmax(published_scores))
    assert np.isclose(hist[0]["score"], published_scores.max())
    assert max(h["projector_defect"] for h in hist) < 1e-10
    assert hist[-1]["residual_risk"] < 1e-20
    # Scores must equal the measured reduction in ||G P||_F^2.
    previous = 1.0
    for h in hist:
        assert np.isclose(previous-h["residual_risk"], h["score"])
        previous = h["residual_risk"]
    # One full-rank time block exhausts noiseless information: expected caveat.
    blocks = [rng.normal(size=(9, 5)) for _ in range(4)]
    _, full = block_svd_greedy(blocks, A, 2)
    assert full[0]["incremental_rank"] == 5
    assert full[0]["residual_risk"] < 1e-20
    assert full[1]["incremental_rank"] == 0
    # Factorized rank-two recurrence equals its explicitly dense counterpart.
    M, H, gain, C = make_rank_two(8)
    x = rng.normal(size=100)
    fast = rank_two_step(x, M, H, gain)
    J = M @ H.T / 100
    dense = x + .1 * (-x + J @ (gain*np.tanh(x)))
    err = float(np.max(np.abs(fast-dense)))
    assert err < 1e-12
    return {"scalar_svd_first_choice": order[0],
            "scalar_first_score": hist[0]["score"],
            "max_projection_defect": max(h["projector_defect"] for h in hist),
            "full_rank_block_residual": full[0]["residual_risk"],
            "rank_two_dense_factor_max_abs_error": err,
            "rank_two_covariance_min_eigenvalue": float(np.linalg.eigvalsh(C).min()),
            "negative_gains": int(np.sum(gain < 0))}


if __name__ == "__main__":
    print(json.dumps(checks(), indent=2))
