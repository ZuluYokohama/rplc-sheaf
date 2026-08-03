# rplc_sheaf

Operational core of **Jones / CycleSheaf / RPL-C**: restriction-projection under audit with sheaf obstruction.

**Invariant:** only structure that survives matched controls is kept. Residue is defined by failure to open — never forced.

## Install / use

```python
import importlib.util
spec = importlib.util.spec_from_file_location("rplc_sheaf", "rplc_sheaf.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

X, rows = m.synthetic_frb(200)
core = m.ordered_core(30, dims=X.shape[1])
ladder, remainder = m.rplc_run(X, core, max_steps=4)

# or bytecode program
cert = m.isa_exec(X, program=[
    {"op": "CORE"},
    {"op": "STEP", "max": 3},
    {"op": "ROTATE"},
    {"op": "HALT"},
])
report = m.verify_certificate(cert, X=X)
```

CLI:

```bash
python rplc_sheaf.py --domain frb --n 160 --steps 4
python rplc_sheaf.py --domain materials --persistence
python rplc_sheaf.py --domain csv --csv data.csv --features col1,col2,col3
```

## Capability map

| # | Capability |
|---|------------|
| 1 | RPL-C loop (peel → restrict → audit → open → rotate → stack) |
| 2 | True sheaf Laplacian L = δ0ᵀ δ0 |
| 3 | Holonomy audit (map twist) |
| 4 | Sheaf-audited OPEN |
| 5 | Rotate branch under sheaf |
| 6 | CycleSheaf edge maps (k, θ) |
| 7 | Per-node (k, θ) domain atlas |
| 8 | Sequence obstruction ordering |
| 9 | Cycle base (holonomy accumulates) |
| 10 | Multi-cover filtration |
| 11 | Filtration profile as OPEN feature |
| 12 | Persistent Laplacian (nested covers) |
| 13 | Persistent features in OPEN decision |
| 14 | Domain loaders (FRB / materials / CSV) |
| 15 | CLI + JSON report |
| 16 | RPL-ISA + isa_exec certificates |
| 17 | Certificate verify/replay |

## Abstraction law

```
Hardware = feature matrix X
Software = ISA instruction words
ALU      = sheaf obstruction under audit
Domains  = payloads only
```

```
restrict → measure obstruction → audit vs controls → OPEN or STOP
if STOP: refine cover / rotate / stack → remeasure
```

No forced structure. Hard residue is a result.

## Requirements

- numpy>=1.22
- scipy>=1.9

## License

Research code. Use and extend under your own terms for the Jones / IsoZ line.
