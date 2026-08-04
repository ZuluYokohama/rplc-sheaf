---
name: rplc-smoke
description: Run rplc-sheaf offline smoke tests and optional sparse-backend parity check
---

# /rplc-smoke

Run offline verification of the rplc-sheaf plugin ALU.

## Steps

1. Resolve plugin root: prefer `$GROK_PLUGIN_ROOT` or `$CLAUDE_PLUGIN_ROOT`; else the `rplc-sheaf` install path / workspace root containing `rplc_sheaf.py`.

2. Execute:

```bash
python tests/test_smoke.py
```

from that root (ensure `numpy` and `scipy` are installed).

3. Optional sparse parity:

```python
import rplc_sheaf as m
import sparse_backend
sparse_backend.install(m)
X, _ = m.synthetic_frb(48)
a, _ = m.sheaf_lambda1(X, backend="dense")
b, _ = m.sheaf_lambda1(X, backend="sparse")
print("dense", a, "sparse", b, "close", abs(a - b) < 1e-9)
```

4. Report pass/fail with the exact error text on failure. Do not claim OPEN for domain discovery.
