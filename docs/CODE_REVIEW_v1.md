# Code Review — rplc-sheaf v1 operational issuance

**Scope:** standalone module `rplc_sheaf.py`, front-end (`run` / `run_domain` / CLI), RPL-ISA, certificates.
**Reviewer:** structural + operational V&V pass prior to Copilot review.
**Date:** 2026-08-03

---

## Verdict

**Ship-ready as research operational core** with known limitations documented below.
Design law is enforced in code: OPEN only under audit; residue is never forced.
Front-end surface is coherent (`run` → `isa_exec` → certificate → `verify_certificate`).

---

## Strengths

1. **Invariant is operational, not aspirational**  
   `audit_stratum` gates OPEN; random controls are matched by size; STOP leaves living set intact.

2. **Clean abstraction layers**  
   Hardware = `X`, Software = ISA program list, ALU = sheaf `L = δ0ᵀδ0`, Domains = payloads only.

3. **Certificate trail**  
   `isa_exec` returns JSON-stable ladder/trace; `verify_certificate` checks schema + optional replay.

4. **Front-end completeness**  
   One-call `run` / `run_domain`, bytecode programs, CSV path, CLI with `--out`.

5. **ROTATE is first-class**  
   Delay-embed + low-recurrence stratum is an ISA op, not a side script.

---

## Issues (severity ordered)

### High

| ID | Issue | Recommendation |
|----|--------|----------------|
| H1 | `eigh` on full dense `n*d × n*d` Laplacian — O((nd)³). Fine for n≲100–300, not for large catalogs. | Document scale; optional sparse path later. |
| H2 | `do_core_step` assumes `core` is set. Program with STEP before CORE raises. | Guard: HALT with reason `no_core` if core is None. |
| H3 | Certificate `remainder` is a full index list — large payloads, not always JSON-friendly for logs. | Compact cert omits it in CLI; API should default to `remainder_n` only unless `include_remainder=True`. |

### Medium

| ID | Issue | Recommendation |
|----|--------|----------------|
| M1 | Audit threshold `lam < mean - 0.1*std` is fixed heuristic, not calibrated. | Expose `audit_margin` parameter; document as research default. |
| M2 | ROTATE maps embed indices back via `order[:n_rem]` — approximate, not exact point correspondence. | Document as approximate OPEN on rotate branch. |
| M3 | `load_csv_features` has no guard for empty file / non-numeric cells. | Raise clear ValueError. |
| M4 | `use_persistence` on `isa_run` is accepted but unused in STEP path. | Wire through or drop kwarg. |
| M5 | No package metadata (`pyproject.toml` / `__version__`). | Add minimal version string for issuance tracking. |

### Low

| ID | Issue | Recommendation |
|----|--------|----------------|
| L1 | `RandomState` vs modern `default_rng`. | Prefer `np.random.default_rng` in next pass. |
| L2 | `ordered_core` trial division for primes — fine for n=30, slow if n large. | OK for current atlas size. |
| L3 | Sequence sheaf AA table is illustrative, not biochemical. | Document as CycleSheaf demo table. |
| L4 | No unit tests in repo. | Add minimal smoke tests post-review. |

---

## Design compliance checklist

| Requirement | Status |
|-------------|--------|
| OPEN only if audit survives | Pass |
| Residue defined by failure | Pass |
| Domains are payloads only | Pass |
| ISA program is data | Pass |
| Certificate verify/replay | Pass |
| Front-end one-call path | Pass |
| Material-only GH tree | Pass |

---

## Copilot review request

Please focus on:
1. Numerical stability of Laplacian / eigenvalue path
2. Edge cases in `isa_exec` program ordering
3. CSV and empty-input robustness
4. API clarity of `run` vs `isa_exec` vs `rplc_run`
5. Any silent failures or swallowed exceptions

---

## Hardening applied on this branch

- CORE-before-STEP guard
- Empty CSV / non-numeric guard
- `include_remainder` flag on certificate path
- `__version__` issuance tag
