"""
sparse_backend — drop-in extension for rplc_sheaf

Usage:
  import rplc_sheaf as m
  import sparse_backend
  sparse_backend.install(m)
  # m.sheaf_lambda1 now accepts backend="auto"|"dense"|"sparse"
  # auto selects sparse when n*d > 200
"""
from __future__ import annotations
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.linalg import eigh

def install(mod):
    """Patch mod.sheaf_lambda1 with backend-aware implementation."""
    knn_edges = mod.knn_edges
    add_cycles = mod.add_cycles
    sheaf_laplacian = mod.sheaf_laplacian

    def _build_d0_sparse(X, edges, D, twist=0.0):
        n, d = X.shape
        m = len(edges)
        if m < 1:
            return sparse.eye(n * d, format="csr")
        fin = D[np.isfinite(D)]
        med = (np.median(fin) if len(fin) else 1.0) + 1e-9
        rows, cols, data = [], [], []
        for ei, (u, v) in enumerate(edges):
            dist = D[u, v] if np.isfinite(D[u, v]) else med
            k = float(np.exp(-dist / med))
            delta = X[v, : min(2, d)] - X[u, : min(2, d)]
            if len(delta) < 2:
                delta = np.array([1.0, 0.0])
            th = np.arctan2(delta[1], delta[0]) + twist * (ei % 3 == 0)
            c, s = np.cos(th), np.sin(th)
            R = np.eye(d)
            if d >= 2:
                R[0, 0] = c; R[0, 1] = -s; R[1, 0] = s; R[1, 1] = c
            for a in range(d):
                for b in range(d):
                    val = k * R[a, b]
                    if abs(val) > 1e-15:
                        rows.append(ei * d + a); cols.append(u * d + b); data.append(val)
                rows.append(ei * d + a); cols.append(v * d + a); data.append(-k)
        return sparse.coo_matrix((data, (rows, cols)), shape=(m * d, n * d)).tocsr()

    def sheaf_lambda1(X, k_nn=4, n_cycles=0, twist=0.0, backend="auto"):
        n, d = X.shape
        if n < 6:
            return 0.0, 1
        use_sparse = backend == "sparse" or (backend == "auto" and n * d > 200)
        edges, D = knn_edges(X, k_nn)
        if n_cycles:
            edges = add_cycles(edges, X, n_cycles=n_cycles)
        edges = list(edges)
        if not use_sparse:
            L = sheaf_laplacian(X, edges, D, twist=twist)
            ev = np.sort(np.real(eigh(L, eigvals_only=True)))
            ev[ev < 1e-10] = 0
            h0 = int(np.sum(ev < 1e-8))
            return float(ev[h0]) if h0 < len(ev) else 0.0, h0
        d0 = _build_d0_sparse(X, edges, D, twist=twist)
        L = (d0.T @ d0).tocsr()
        k_req = min(8, max(L.shape[0] - 2, 2))
        try:
            ev = eigsh(L, k=k_req, which="SM", return_eigenvectors=False, tol=1e-7, maxiter=4000)
        except Exception:
            L2 = L + sparse.eye(L.shape[0]) * 1e-10
            ev = eigsh(L2, k=k_req, sigma=1e-8, which="LM", return_eigenvectors=False, tol=1e-7, maxiter=4000)
        ev = np.sort(np.real(ev)); ev[ev < 1e-10] = 0
        h0 = int(np.sum(ev < 1e-8))
        pos = ev[ev > 1e-8]
        return float(pos[0]) if len(pos) else 0.0, h0

    mod.sheaf_lambda1 = sheaf_lambda1
    mod.__version__ = getattr(mod, "__version__", "1.0.0") + "+sparse"
    return mod
