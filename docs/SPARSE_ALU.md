# Sparse ALU (v1.1.0-sparse-auto)

## Change
- Planned (review-branch-only) API: `sheaf_lambda1(..., backend)` with `backend ∈ {"auto", "dense", "sparse"}`
- auto selects sparse when `n * d > 200`
- sparse path: COO coboundary → CSR `L = δ0ᵀδ0` → `eigsh` (SM, shift-invert fallback)
- dense path retained for small n and exact parity checks

## Real-data re-run (n=500, verify=true)

| Domain | Opened | Remainder | Time |
|--------|--------|-----------|------|
| FRB | 0 | 500/500 | 1.6s |
| SuperCon | 1 | 375/500 | 9.4s |
| ClinVar | 1 | 351/500 | 2.2s |

H1 (dense O((nd)³) envelope) addressed for catalog-scale runs.
