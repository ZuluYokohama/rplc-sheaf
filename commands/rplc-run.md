---
name: rplc-run
description: Run rplc-sheaf on a domain (frb/materials/csv) or synthetic matrix and print certificate summary
---

# /rplc-run

Run the RPL-ISA front-end and summarize the certificate.

## Steps

1. Resolve plugin root (`$GROK_PLUGIN_ROOT` / `$CLAUDE_PLUGIN_ROOT` / workspace with `rplc_sheaf.py`).
2. Put that root on `PYTHONPATH` and run one of:

```bash
python rplc_sheaf.py --domain frb --n 80 --steps 3
python rplc_sheaf.py --domain materials --n 80 --seed 1
```

Or in Python:

```python
import rplc_sheaf as m
cert, report = m.run_domain("materials", n=40, seed=1)[0:2]
# or: cert, report = m.run(X, seed=0)
print(report)
print({k: cert.get(k) for k in ("remainder_n", "halt_reason", "n0") if k in cert or True})
```

3. Respect design law: report `ok` / halt / remainder; never force OPEN.
4. For large n, install sparse first: `import sparse_backend; sparse_backend.install(m)`.
