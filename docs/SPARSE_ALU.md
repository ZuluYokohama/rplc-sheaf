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

## Implementation notes

- Builds sparse COO coboundary → CSR Laplacian L = δ₀ᵀδ₀
- Uses `eigsh` (SM) with shift-invert fallback
- Dense path retained for small n and numerical parity checks
- Design law unchanged: OPEN only under audit; residue never forced

## Status

OPEN for catalog-scale capability under the install pattern.  
RESIDUE remains on full in-tree default integration and exhaustive parity characterization.
