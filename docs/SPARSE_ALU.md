# Sparse ALU

## Purpose

Close the primary scale RESIDUE of the dense `eigh` path (interactive limit ~n ≲ 300).

## Usage

```python
import rplc_sheaf as m
import sparse_backend
sparse_backend.install(m)

# now accepts backend=
lam, h0 = m.sheaf_lambda1(X, backend="auto")   # sparse when n*d > 200
lam, h0 = m.sheaf_lambda1(X, backend="sparse")
lam, h0 = m.sheaf_lambda1(X, backend="dense")  # original path
```

Note: `n < 6` early-returns `(0.0, 1)` before backend selection (same gate as dense).

## Implementation notes

- Builds sparse COO coboundary → CSR Laplacian L = δ₀ᵀδ₀
- Uses `eigsh` (SM) with shift-invert fallback (fallback eigenvalues de-biased)
- Dense path retained for small n and numerical parity checks
- Design law unchanged: OPEN only under audit; residue never forced

## Parity expectations

- Same edge construction and coboundary semantics as dense
- λ1 may differ slightly (eigh vs eigsh); audit gate is the decision surface
- Recommended: spot-check dense vs sparse on small synthetic matrices before production use

## Status

OPEN for catalog-scale capability under the install pattern.  
RESIDUE remains on full in-tree default integration and exhaustive parity characterization.
