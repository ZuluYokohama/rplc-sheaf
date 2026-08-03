# Code Review — rplc-sheaf v1 operational issuance

**Scope:** standalone module `rplc_sheaf.py`, front-end (`run` / `run_domain` / CLI), RPL-ISA, certificates.
**Reviewer:** structural + operational V&V pass prior to Copilot / CodeRabbit review.
**Date:** 2026-08-03

---

## Verdict

**Ship-ready as research operational core** with known limitations documented below.
Design law is enforced in code: OPEN only under audit; residue is never forced.
Front-end surface is coherent (`run` → `isa_exec` → certificate → `verify_certificate`).

**Operational envelope:** dense `eigh` on `n*d` Laplacian is O((nd)³). Prefer **n ≲ 300** for interactive use.

---

## Strengths

1. **Invariant is operational, not aspirational**  
   `audit_stratum` gates OPEN; random controls are matched by size; STOP leaves living set intact.

2. **Clean abstraction layers**  
   Hardware = `X`, Software = ISA program list, ALU = sheaf `L = δ0ᵀδ0`, Domains = payloads only.

3. **Certificate trail**  
   `isa_exec` returns JSON-stable ladder/trace. `verify_certificate` validates schema markers, program equality under replay, remainder bounds, optional exact remainder indices, and rejects fatal halt reasons (`no_core`, `unknown_op`). It does **not** deep-compare full trace/ladder payloads or require `opened_delta == 0`.

4. **Front-end completeness**  
   One-call `run` / `run_domain`, bytecode programs, CSV path, CLI with `--out`.

5. **ROTATE is first-class**  
   Delay-embed + low-recurrence stratum is an ISA op, not a side script. OPEN on rotate is **approximate** (PC1 order mapping).

---

## Issues (severity ordered)

### Open (post-v1 track)

| ID | Issue | Recommendation | Status |
|----|--------|----------------|--------|
| H1 | `eigh` on full dense `n*d × n*d` Laplacian — O((nd)³). Fine for n≲100–300, not for large catalogs. | Document scale; optional sparse path later. | **Open** |
| M2 | ROTATE maps embed indices back via `order[:n_rem]` — approximate, not exact point correspondence. | Documented as approximate OPEN (`approx: true` in trace). | **Open** (documented) |
| M4 | `use_persistence` on `isa_run` is accepted but unused in STEP path. | Wire through or drop kwarg. | **Open** |
| L1 | `RandomState` vs modern `default_rng`. | Prefer `np.random.default_rng` in next pass. | **Open** |
| L2 | `ordered_core` trial division for primes — fine for n=30, slow if n large. | OK for current atlas size. | **Open** |
| L3 | Sequence sheaf AA table is illustrative, not biochemical. | Document as CycleSheaf demo table. | **Open** |
| L4 | No unit tests in repo. | Add minimal smoke tests post-review. | **Open** |

### Resolved on this branch

| ID | Issue | Resolution |
|----|--------|------------|
| H2 | STEP before CORE raised / continued after HALT | Terminal HALT `reason=no_core`; outer program loop stops. Verifier rejects fatal halt. |
| H3 | Full remainder index list always large | Opt-in via `include_remainder=True`; default is `remainder_n` only. |
| M1 | Audit threshold default `audit_margin=0.1` is a fixed heuristic, not calibrated per domain | Parameter exposed on `audit_stratum` (default 0.1); per-domain calibration deferred. |
| M3 | CSV empty / non-numeric unguarded | Clear `ValueError`s; path in messages; missing columns; non-finite reject. |
| M5 | No package metadata / version | `__version__ = "1.0.0-operational"` on certs. |
| — | Unknown opcodes silent NOP | Now terminal HALT `reason=unknown_op`. |
| — | ROTATE broad `except Exception` | Catch `np.linalg.LinAlgError` only; emit `ROTATE_FALLBACK` trace. |
| — | Remainder not verified | Shape/bounds/uniqueness offline; exact match under replay when field present. |

---

## Design compliance checklist

| Requirement | Status |
|-------------|--------|
| OPEN only if audit survives | Pass |
| Residue defined by failure | Pass |
| Domains are payloads only | Pass |
| ISA program is data | Pass |
| Certificate verify/replay (schema + program + remainder bounds/match) | Pass |
| Front-end one-call path | Pass |
| Material-only GH tree | Pass |

---

## Copilot / CodeRabbit review request

Please focus on:
1. Numerical stability of Laplacian / eigenvalue path
2. Edge cases in `isa_exec` program ordering (fatal HALT must stop execution)
3. CSV and empty-input robustness
4. API clarity of `run` vs `isa_exec` vs `rplc_run`
5. Any silent failures or swallowed exceptions

---

## Hardening applied on this branch

- CORE-before-STEP guard (terminal `no_core` HALT)
- Empty CSV / non-numeric / missing column / non-finite guards (path in errors)
- `include_remainder` flag on certificate path + remainder verify
- `__version__` issuance tag
- `audit_margin` parameter on `audit_stratum`
- Unknown opcode → terminal HALT (no silent NOP)
- ROTATE SVD failure: narrow `LinAlgError` + `ROTATE_FALLBACK` trace
- `verify_certificate` rejects fatal halt reasons; documents actual guarantee surface
