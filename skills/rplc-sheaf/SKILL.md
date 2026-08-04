---
name: rplc-sheaf
description: >
  Use when working with rplc-sheaf / RPL-C / CycleSheaf / RPL-ISA: restriction-projection
  under audit, sheaf Laplacian λ₁, certificates, sparse ALU backend, claims ledger, or
  design-law OPEN/STOP decisions. Triggers on sheaf obstruction, run_domain, verify_certificate,
  sparse_backend.install, or residue/OPEN claims for this repo.
---

# rplc-sheaf skill

## Design law (non-negotiable)

```
restrict → measure obstruction → audit vs controls → OPEN or STOP
```

Residue is **never forced**. OPEN only survives size-matched controls.

## Layout

Plugin root (`${GROK_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_ROOT}`):

| Path | Role |
|------|------|
| `rplc_sheaf.py` | Core ALU + ISA + `run` / `run_domain` / CLI |
| `sparse_backend.py` | Optional drop-in sparse `sheaf_lambda1` (`backend=auto\|dense\|sparse`) |
| `docs/CLAIMS.md` | OPEN vs RESIDUE ledger |
| `docs/SPARSE_ALU.md` | Sparse path usage + parity notes |
| `tests/test_smoke.py` | Offline smoke |

## Usage

```python
import sys
from pathlib import Path
root = Path("${GROK_PLUGIN_ROOT}")  # or CLAUDE_PLUGIN_ROOT / repo root
sys.path.insert(0, str(root))

import rplc_sheaf as m
X, _ = m.synthetic_frb(48)
cert, report = m.run(X, seed=0)
assert report.get("ok") is True

# optional catalog-scale ALU
import sparse_backend
sparse_backend.install(m)
lam, h0 = m.sheaf_lambda1(X, backend="auto")
```

CLI from plugin root:

```bash
python rplc_sheaf.py --domain frb --n 160 --steps 3
python tests/test_smoke.py
```

## Agent rules

1. Do not weaken CSV guards, halt semantics, or `verify_certificate` when editing core.
2. Prefer drop-in `sparse_backend` over rewriting dense `sheaf_lambda1` on main.
3. Claims: distinguish OPEN vs RESIDUE; sparse is install-pattern OPEN, not silent in-tree default.
4. Pair with `specialized-agents:sheaf-guardian` when synthesis needs Laplacian gating.
