# rplc-sheaf

**RPL-C / CycleSheaf / RPL-ISA** — restriction-projection under audit with sheaf obstruction.

Standalone operational issuance of the framework developed for layered residual structure (FRB-style, materials, clinical VUS, and any feature matrix domain).

## Design law

```
restrict → measure obstruction → audit vs controls → OPEN or STOP
if STOP: refine cover / rotate → remeasure
```

Residue is defined by failure to open — never forced.

## Abstraction

| Layer | Role |
|-------|------|
| Hardware | Feature matrix X |
| Software | RPL-ISA instruction words |
| ALU | Sheaf Laplacian under matched controls |
| Domains | Payloads only |

## Install

```bash
pip install numpy scipy
# place rplc_sheaf.py on PYTHONPATH or in your project
```

## Front-end (full functionality)

### One-call API

```python
import importlib.util
spec = importlib.util.spec_from_file_location("rplc_sheaf", "rplc_sheaf.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

X, rows = m.synthetic_frb(200)
cert, report = m.run(X, seed=0)
# cert  — ladder, trace, remainder_n, program (JSON-stable)
# report — verify_certificate (schema + replay)

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

### CSV pipeline

```python
X, labels, raw = m.load_csv_features("data.csv", ["f1", "f2", "f3"], label_col="y")
cert, report = m.run(X, seed=0)
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
| 2 | True sheaf Laplacian L = δ0ᵀ δ0 |
| 3 | Holonomy / twist audit |
| 4 | Sheaf-audited OPEN |
| 5 | ROTATE branch (delay embed / low-recurrence) |
| 6 | CycleSheaf-style (k, θ) maps |
| 7 | Multi-cover filtration + nested persistence |
| 8 | RPL-ISA vocabulary + bytecode isa_exec |
| 9 | Serializable certificates + verify/replay |
| 10 | Domain loaders (FRB / materials / CSV) |
| 11 | Front-end: run / run_domain / CLI |

## Mathematics (short)

- Stalks — feature vectors at vertices
- Restriction maps F_v	o e — stiffness k from edge length, rotation θ from local displacement
- Coboundary δ0; sheaf Laplacian L = δ0ᵀ δ0
- λ1 — first positive eigenvalue (obstruction energy)
- Audit — compare stratum λ1 to random subsets of equal size
- OPEN only if obstruction survives controls

## Certificate schema

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

## What this is not

Not a domain decoder for FRB, SuperCon, or ClinVar specifically.
Those were test payloads. The product is the **operator series** and its front-end.

## License

Research code for the Jones / IsoZ / RPL-C line. Extend under your terms.
