# rplc-sheaf

**RPL-C / CycleSheaf / RPL-ISA** — restriction–projection under audit with sheaf obstruction.

> **License: Proprietary source-available.** Evaluation and academic citation only without a written commercial grant. See [`LICENSE`](LICENSE) and [`COMMERCIAL.md`](COMMERCIAL.md). Not open source.

**Author:** Blake A. Jones (JtechAI) · [b.jones@jtech.ai](mailto:b.jones@jtech.ai)  
**Related:** [protein-rpl-validation](https://github.com/ZuluYokohama/protein-rpl-validation) (domain application of the same operator series)

---

## Design law

```
restrict → measure obstruction → audit vs controls → OPEN or STOP
if STOP: refine cover / rotate → remeasure
```

Residue is defined by **failure to open** — never forced.

This posture matches a broader engineering discipline: adversarial verification of computational claims, certificate trails, and refusal to promote structure that does not survive controls.

## Abstraction

| Layer | Role |
|-------|------|
| Hardware | Feature matrix `X` |
| Software | RPL-ISA instruction words |
| ALU | Sheaf Laplacian under matched controls |
| Domains | Payloads only (FRB-style, materials, CSV, …) |

## Install

```bash
pip install -r requirements.txt
# place rplc_sheaf.py on PYTHONPATH, or run from this directory
```

## Quick start

```python
import rplc_sheaf as m

X, rows = m.synthetic_frb(160)
cert, report = m.run(X, seed=0)
assert report["ok"]  # schema + replay verify

cert, report, rows = m.run_domain("materials", n=160, seed=0)
```

### Custom ISA program

```python
cert, report = m.run(X, program=[
    {"op": "CORE"},
    {"op": "STEP", "max": 4},
    {"op": "ROTATE"},
    {"op": "HALT"},
], seed=0)
```

### CLI

```bash
python rplc_sheaf.py --domain frb --n 160 --steps 3
python rplc_sheaf.py --domain materials --seed 1 --out cert.json
python rplc_sheaf.py --domain csv --csv data.csv --features f1,f2,f3 --out cert.json
```

## Core capability map

| # | Capability |
|---|------------|
| 1 | RPL-C loop (restrict → audit → open → rotate) |
| 2 | Sheaf Laplacian L = δ₀ᵀ δ₀ |
| 3 | Holonomy / twist audit |
| 4 | Sheaf-audited OPEN |
| 5 | ROTATE branch (delay embed / low-recurrence; approximate OPEN) |
| 6 | CycleSheaf-style (k, θ) maps |
| 7 | Multi-cover filtration + nested persistence |
| 8 | RPL-ISA vocabulary + `isa_exec` bytecode |
| 9 | Serializable certificates + verify/replay |
| 10 | Domain loaders (FRB / materials / CSV) |
| 11 | Front-end: `run` / `run_domain` / CLI |

## Mathematics (short)

- **Stalks** — feature vectors at vertices
- **Restriction maps** F_v→e — stiffness from edge length, rotation from local displacement
- **Coboundary** δ₀; **sheaf Laplacian** L = δ₀ᵀ δ₀
- **λ₁** — first positive eigenvalue (obstruction energy)
- **Audit** — compare stratum λ₁ to random subsets of equal size
- **OPEN** only if obstruction survives controls

## Certificate schema (illustrative)

```json
{
  "n0": 160,
  "dims": 4,
  "opened_steps": 2,
  "remainder_n": 80,
  "ladder": [{"step": 1, "n": 40, "branch": "core", "lam1": 0.05, "survives": true}],
  "trace": ["CORE", "SHEAF_AUDIT", "OPEN", "...", "HALT"],
  "program": [{"op": "CORE"}, {"op": "STEP", "max": 3}, {"op": "ROTATE"}, {"op": "HALT"}]
}
```

`verify_certificate` checks schema markers, program equality under replay, remainder bounds, optional exact remainder indices, and rejects fatal halt reasons (`no_core`, `unknown_op`).

## Operational envelope

Dense `eigh` on an nd×nd Laplacian is O((nd)³). Prefer **n ≲ 300** for interactive use. Sparse / shift-invert path is a documented follow-on (see `docs/CODE_REVIEW_v1.md`).

## Claims posture

| Status | Claim |
|--------|--------|
| **OPEN** | Design law enforced in code: OPEN only under control-matched audit |
| **OPEN** | Certificates are JSON-stable; verify/replay rejects fatal halt paths |
| **OPEN** | Domains are payloads; operator series is the product |
| **RESIDUE** | Sparse ALU for large n (catalog-scale) |
| **RESIDUE** | Domain-calibrated `audit_margin` (default 0.1 is a fixed heuristic) |
| **RESIDUE** | Exact (non-approximate) ROTATE point correspondence |

## What this is not

Not a domain decoder for FRB, SuperCon, ClinVar, or protein structure. Those are test payloads. Not a medical device or diagnostic.

Domain applications of the same operator series:  
[protein-rpl-validation](https://github.com/ZuluYokohama/protein-rpl-validation)

## Tests

```bash
python tests/test_smoke.py
# → all smoke OK
```

## Docs

- [`docs/RPL_ISA_CARD.md`](docs/RPL_ISA_CARD.md) — instruction card
- [`docs/CODE_REVIEW_v1.md`](docs/CODE_REVIEW_v1.md) — structural V&V prior to external review
- [`docs/CLAIMS.md`](docs/CLAIMS.md) — OPEN / RESIDUE ledger

## License

**Proprietary source-available** — Copyright © 2026 Blake A. Jones (JtechAI / ZuluYokohama).  
Evaluation Use and citation permitted. **Commercial Use requires a written license:** b.jones@jtech.ai  
Full terms: [`LICENSE`](LICENSE) · Summary: [`COMMERCIAL.md`](COMMERCIAL.md)

## Version

**1.0.0-operational** — standalone RPL-C / RPL-ISA core with certificate front-end.
