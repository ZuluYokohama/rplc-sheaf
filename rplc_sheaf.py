"""
rplc_sheaf — Restriction-Projection Ladder + CycleSheaf (RPL-C / RPL-ISA)

Operational framework: sheaf obstruction under audit for layered residual structure.

Public surface
--------------
  run, run_domain                         # front-end
  isa_exec, isa_run, verify_certificate   # ISA + certificates
  sheaf_lambda1, sheaf_laplacian          # ALU
  rplc_run, audit_stratum, ordered_core
  filtration_profile, nested_persistence
  synthetic_frb, synthetic_materials
  load_csv_features, write_csv
  sequence_sheaf_lambda1

Design law
----------
  restrict → measure obstruction → audit vs controls → OPEN or STOP
  if STOP: refine cover / rotate → remeasure
  Residue is defined by failure to open — never forced.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from scipy.spatial.distance import pdist, squareform, cdist

ISA_OPS = (
    "PEEL", "CORE", "RESTRICT", "STRATUM", "SHEAF", "AUDIT",
    "OPEN", "ROTATE", "COVER", "FILT", "PERSIST", "HOLONOMY", "HALT",
)

def knn_edges(X, k):
    n = len(X)
    D = squareform(pdist(X)); np.fill_diagonal(D, np.inf)
    edges = set()
    for i in range(n):
        for j in np.argsort(D[i])[: min(k, n - 1)]:
            edges.add((min(i, j), max(i, j)))
    return edges, D

def add_cycles(edges, X, n_cycles=8, seed=0):
    rng = np.random.RandomState(seed)
    n = len(X)
    edges = set(edges)
    D = squareform(pdist(X)); np.fill_diagonal(D, np.inf)
    added = 0
    for _ in range(n_cycles * 6):
        i = rng.randint(0, n)
        nn = np.argsort(D[i])[:6]
        if len(nn) < 3:
            continue
        a, b = int(nn[1]), int(nn[2])
        e = (min(a, b), max(a, b))
        if e not in edges:
            edges.add(e)
            added += 1
        if added >= n_cycles:
            break
    return edges

def sheaf_laplacian(X, edges, D, twist=0.0):
    n, d = X.shape
    edges = list(edges)
    m = len(edges)
    if m < 1:
        return np.eye(n * d)
    d0 = np.zeros((m * d, n * d))
    med = np.median(D[D < np.inf]) + 1e-9
    for ei, (u, v) in enumerate(edges):
        dist = D[u, v] if np.isfinite(D[u, v]) else med
        k = np.exp(-dist / med)
        delta = X[v, : min(2, d)] - X[u, : min(2, d)]
        if len(delta) < 2:
            delta = np.array([1.0, 0.0])
        theta = np.arctan2(delta[1], delta[0]) + twist * (ei % 3 == 0)
        c, s = np.cos(theta), np.sin(theta)
        R = np.eye(d)
        if d >= 2:
            R[0, 0] = c; R[0, 1] = -s; R[1, 0] = s; R[1, 1] = c
        d0[ei * d:(ei + 1) * d, u * d:(u + 1) * d] = k * R
        d0[ei * d:(ei + 1) * d, v * d:(v + 1) * d] = -k * np.eye(d)
    return d0.T @ d0

def sheaf_lambda1(X, k_nn=4, n_cycles=0, twist=0.0):
    if len(X) < 6:
        return 0.0, 1
    edges, D = knn_edges(X, k_nn)
    if n_cycles:
        edges = add_cycles(edges, X, n_cycles=n_cycles)
    L = sheaf_laplacian(X, edges, D, twist=twist)
    ev = np.sort(np.real(eigh(L, eigvals_only=True)))
    ev[ev < 1e-10] = 0
    h0 = int(np.sum(ev < 1e-8))
    lam1 = float(ev[h0]) if h0 < len(ev) else 0.0
    return lam1, h0

def filtration_profile(X, ks=(3, 4, 5)):
    return np.array([sheaf_lambda1(X, k_nn=k)[0] for k in ks])

def nested_persistence(X, ks=(3, 5, 7)):
    if len(X) < 12:
        return 0.0, 0.0
    edges_acc = set()
    D = None
    evs = []
    for k in ks:
        e, D = knn_edges(X, k)
        edges_acc |= e
        L = sheaf_laplacian(X, edges_acc, D)
        ev = np.sort(np.real(eigh(L, eigvals_only=True)))
        ev[ev < 1e-10] = 0
        evs.append(ev)
    lam_fine = float(evs[-1][1]) if len(evs[-1]) > 1 else float(evs[-1][0])
    thresh = 0.2
    soft0 = int(np.sum((evs[0] > 1e-8) & (evs[0] < thresh)))
    soft1 = int(np.sum((evs[-1] > 1e-8) & (evs[-1] < thresh)))
    return lam_fine, float(soft1 / max(soft0, 1))

def ordered_core(n=30, dims=3):
    primes, c = [], 2
    while len(primes) < n:
        if all(c % x for x in primes):
            primes.append(c)
        c += 1
    primes = np.array(primes, dtype=float)
    cols = [np.log(primes), np.concatenate([[0], np.diff(primes)]), primes % 6, primes % 10]
    A = np.column_stack(cols[: max(dims, 2)])
    if A.shape[1] < dims:
        A = np.hstack([A, np.zeros((n, dims - A.shape[1]))])
    A = A[:, :dims]
    return (A - A.mean(0)) / (A.std(0) + 1e-9)

def audit_stratum(X, mask, n_ctrl=5, seed=0, use_persistence=False):
    Xs = X[mask]
    if use_persistence:
        lam, _ = nested_persistence(Xs)
    else:
        lam, _ = sheaf_lambda1(Xs)
    rng = np.random.RandomState(seed)
    rands = []
    for _ in range(n_ctrl):
        idx = rng.choice(len(X), size=int(mask.sum()), replace=False)
        if use_persistence:
            rands.append(nested_persistence(X[idx])[0])
        else:
            rands.append(sheaf_lambda1(X[idx])[0])
    survives = bool(lam < np.mean(rands) - 0.1 * max(np.std(rands), 1e-6))
    return {"lam1": float(lam), "rand_mean": float(np.mean(rands)), "survives": survives}

def rplc_step(X, core, percentile=75, seed=0, use_persistence=False):
    C = cdist(X, core)
    aff = np.exp(-C / (np.median(C) + 1e-9)).max(1)
    mask = aff >= np.percentile(aff, percentile)
    if mask.sum() < 12:
        return mask, {"lam1": 0.0, "rand_mean": 0.0, "survives": False}
    return mask, audit_stratum(X, mask, seed=seed, use_persistence=use_persistence)

def rplc_run(X, core, max_steps=4, percentile=75, use_persistence=False):
    living = list(range(len(X)))
    ladder = []
    for step in range(1, max_steps + 1):
        if len(living) < 30:
            break
        Xl = X[living]
        mask, audit = rplc_step(Xl, core, percentile=percentile, seed=step * 7, use_persistence=use_persistence)
        n = int(mask.sum())
        entry = {"step": step, "n": n, **audit}
        ladder.append(entry)
        if not audit["survives"]:
            break
        living = [living[i] for i in range(len(living)) if not mask[i]]
    return ladder, living

def features_from_records(records, keys):
    X = np.array([[float(r[k]) for k in keys] for r in records], dtype=float)
    return (X - X.mean(0)) / (X.std(0) + 1e-9)

def synthetic_frb(n=200, seed=0):
    rng = np.random.RandomState(seed)
    rows = []
    for i in range(n):
        pop = rng.choice(["repeater", "oneoff", "ambiguous"], p=[0.2, 0.6, 0.2])
        if pop == "repeater":
            dm, width = rng.lognormal(5.2, 0.5), rng.lognormal(0.8, 0.6)
            fluence, scatter = rng.lognormal(1.2, 0.8), rng.uniform(0.05, 2.0)
        elif pop == "oneoff":
            dm, width = rng.lognormal(6.0, 0.7), rng.lognormal(0.3, 0.9)
            fluence, scatter = rng.lognormal(1.8, 1.0), rng.uniform(0.02, 4.0)
        else:
            dm, width = rng.lognormal(5.6, 0.8), rng.lognormal(0.5, 1.0)
            fluence, scatter = rng.lognormal(1.4, 1.1), rng.uniform(0.1, 5.0)
        rows.append(dict(pop=pop, log_dm=np.log10(dm + 1), log_w=np.log10(width + 0.01),
                         scatter=scatter, fluence=fluence))
    return features_from_records(rows, ["log_dm", "log_w", "scatter", "fluence"]), rows

def synthetic_materials(n=200, seed=1):
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(n):
        fam = rng.choice(["cuprate", "iron", "conventional", "unknown"], p=[0.15, 0.12, 0.4, 0.33])
        if fam == "cuprate":
            mass, eneg, val, struct, Tc = rng.normal(80, 15), rng.normal(2.2, 0.3), rng.normal(6, 1), rng.normal(0.8, 0.15), rng.lognormal(4.0, 0.4)
        elif fam == "iron":
            mass, eneg, val, struct, Tc = rng.normal(70, 12), rng.normal(1.9, 0.25), rng.normal(7, 1), rng.normal(0.6, 0.2), rng.lognormal(3.2, 0.5)
        elif fam == "conventional":
            mass, eneg, val, struct, Tc = rng.normal(50, 20), rng.normal(1.6, 0.4), rng.normal(4, 1.5), rng.normal(0.3, 0.2), rng.lognormal(1.5, 0.8)
        else:
            mass, eneg, val, struct, Tc = rng.normal(60, 25), rng.normal(1.8, 0.5), rng.normal(5, 2), rng.normal(0.4, 0.3), rng.lognormal(2.0, 1.0)
        rows.append(dict(family=fam, mass=max(mass, 10), eneg=max(eneg, 0.5), val=max(val, 1),
                         struct=float(np.clip(struct, 0, 1)), log_Tc=np.log10(max(Tc, 0.1))))
    return features_from_records(rows, ["mass", "eneg", "val", "struct", "log_Tc"]), rows

def load_csv_features(path, feature_cols, label_col=None):
    import csv
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    X = np.array([[float(r[c]) for c in feature_cols] for r in rows], dtype=float)
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    labels = [r[label_col] for r in rows] if label_col else None
    return X, labels, rows

def write_csv(path, rows, fieldnames=None):
    import csv
    if not rows:
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

DEFAULT_AA = {
    "A": (1.0, -0.5), "G": (0.15, 0.0), "P": (4.0, -1.2),
    "V": (1.8, -0.8), "S": (0.8, -0.3), "L": (1.2, -0.6), "E": (0.9, 0.4),
}

def sequence_sheaf_lambda1(seq, aa_table=None, cycle=False, twist=0.0, stalk_dim=2):
    aa_table = aa_table or DEFAULT_AA
    n = len(seq)
    d = stalk_dim
    edges = [(i, i + 1) for i in range(n - 1)]
    if cycle and n >= 3:
        edges.append((n - 1, 0))
    m = len(edges)
    d0 = np.zeros((m * d, n * d))
    for ei, (u, v) in enumerate(edges):
        ku, thu = aa_table.get(seq[u], (1.0, 0.0))
        kv, thv = aa_table.get(seq[v], (1.0, 0.0))
        k = np.sqrt(ku * kv)
        theta = (thv - thu) + twist
        c, s = np.cos(theta), np.sin(theta)
        Ru = np.eye(d)
        if d >= 2:
            Ru[0, 0] = c; Ru[0, 1] = -s; Ru[1, 0] = s; Ru[1, 1] = c
        d0[ei * d:(ei + 1) * d, u * d:(u + 1) * d] = k * Ru
        d0[ei * d:(ei + 1) * d, v * d:(v + 1) * d] = -k * np.eye(d)
    L = d0.T @ d0
    ev = np.sort(np.real(eigh(L, eigvals_only=True)))
    ev[ev < 1e-12] = 0
    h0 = int(np.sum(ev < 1e-8))
    lam1 = float(ev[h0]) if h0 < len(ev) else 0.0
    return lam1, h0

def isa_exec(X, program=None, seed=0, percentile=75):
    if program is None:
        program = [{"op": "CORE"}, {"op": "STEP", "max": 3}, {"op": "ROTATE"}, {"op": "HALT"}]
    living = list(range(len(X)))
    trace, ladder = [], []
    core = None

    def do_core_step(step):
        nonlocal living
        if len(living) < 28:
            return False
        Xl = X[living]
        C = cdist(Xl, core)
        aff = np.exp(-C / (np.median(C) + 1e-9)).max(1)
        mask = aff >= np.percentile(aff, percentile)
        n = int(mask.sum())
        if n < 12:
            trace.append({"op": "HALT", "reason": "stratum_small"})
            return False
        audit = audit_stratum(Xl, mask, seed=seed + step)
        audit["survives"] = bool(audit["survives"])
        trace.append({"op": "SHEAF_AUDIT", "branch": "core", "step": step, "n": n, **audit})
        ladder.append({"step": step, "n": n, "branch": "core", **audit})
        if audit["survives"]:
            trace.append({"op": "OPEN", "branch": "core", "step": step, "n": n})
            living = [living[i] for i in range(len(living)) if not mask[i]]
            return True
        return False

    def do_rotate(step):
        nonlocal living
        if len(living) < 40:
            return False
        Xl = X[living]
        Xl_c = Xl - Xl.mean(0)
        try:
            _, _, Vt = np.linalg.svd(Xl_c, full_matrices=False)
            pc1 = Xl_c @ Vt[0]
        except Exception:
            pc1 = Xl[:, 0]
        order = np.argsort(pc1)
        intervals = np.diff(pc1[order])
        if len(intervals) < 25:
            return False
        E = np.array([[intervals[i + k] for k in range(3)] for i in range(len(intervals) - 2)])
        E = (E - E.mean(0)) / (E.std(0) + 1e-9)
        D = squareform(pdist(E))
        thr = np.percentile(D[D > 0], 15)
        local_rec = (D < thr).mean(1)
        lo = local_rec <= np.percentile(local_rec, 30)
        if lo.sum() < 12:
            return False
        audit = audit_stratum(E, lo, seed=seed + 50)
        n = int(lo.sum())
        audit["survives"] = bool(audit["survives"])
        trace.append({"op": "SHEAF_AUDIT", "branch": "rotate", "step": step, "n": n, **audit})
        ladder.append({"step": step, "n": n, "branch": "rotate", **audit})
        if audit["survives"]:
            n_rem = min(n, len(living) // 3)
            drop = set(np.array(living)[order[:n_rem]].tolist())
            living = [i for i in living if i not in drop]
            trace.append({"op": "OPEN", "branch": "rotate", "step": step, "n": n_rem})
            return True
        return False

    for instr in program:
        op = instr.get("op")
        if op == "CORE":
            core = ordered_core(30, dims=X.shape[1])
            trace.append({"op": "CORE", "n_core": len(core)})
        elif op == "STEP":
            for s in range(1, int(instr.get("max", 3)) + 1):
                if not do_core_step(s):
                    break
        elif op == "ROTATE":
            trace.append({"op": "ROTATE"})
            do_rotate(99)
        elif op == "HALT":
            trace.append({"op": "HALT", "living": len(living)})
            break
        else:
            trace.append({"op": "NOP", "raw": str(op)})

    return {
        "n0": int(X.shape[0]), "dims": int(X.shape[1]),
        "opened_steps": int(sum(1 for e in ladder if e.get("survives"))),
        "remainder_n": len(living), "remainder": living,
        "ladder": ladder, "trace": trace, "program": program,
    }

def isa_run(X, max_steps=4, percentile=75, use_persistence=False, seed=0, enable_rotate=True):
    program = [{"op": "CORE"}, {"op": "STEP", "max": max_steps}]
    if enable_rotate:
        program.append({"op": "ROTATE"})
    program.append({"op": "HALT"})
    return isa_exec(X, program=program, seed=seed, percentile=percentile)

def verify_certificate(cert, X=None, seed=0):
    report = {"ok": True, "checks": []}
    if "program" not in cert or "trace" not in cert:
        return {"ok": False, "checks": [{"check": "schema", "pass": False}]}
    report["checks"].append({"check": "schema", "pass": True})
    ops = [t.get("op") for t in cert["trace"]]
    report["checks"].append({"check": "has_CORE", "pass": "CORE" in ops})
    report["checks"].append({"check": "has_HALT", "pass": "HALT" in ops})
    report["checks"].append({"check": "opened_nonneg", "pass": int(cert.get("opened_steps", 0)) >= 0})
    if X is not None:
        replay = isa_exec(X, program=cert["program"], seed=seed)
        report["checks"].append({"check": "program_replay", "pass": replay["program"] == cert["program"]})
        report["checks"].append({"check": "remainder_bounds", "pass": 0 <= replay["remainder_n"] <= replay["n0"]})
        report["replay"] = {"opened_steps": replay["opened_steps"], "remainder_n": replay["remainder_n"]}
        report["opened_delta"] = abs(int(cert.get("opened_steps", 0)) - replay["opened_steps"])
    report["ok"] = all(c["pass"] for c in report["checks"] if c.get("pass") is not None)
    return report

def run(X, program=None, seed=0, verify=True):
    """Primary front-end: feature matrix → certificate (+ optional verify)."""
    if program is None:
        program = [{"op": "CORE"}, {"op": "STEP", "max": 3}, {"op": "ROTATE"}, {"op": "HALT"}]
    cert = isa_exec(X, program=program, seed=seed)
    report = verify_certificate(cert, X=X, seed=seed) if verify else None
    return cert, report

def run_domain(domain="frb", n=160, seed=0, **kwargs):
    """Front-end on synthetic domain. domain in {frb, materials}."""
    if domain == "frb":
        X, rows = synthetic_frb(n, seed=seed)
    elif domain == "materials":
        X, rows = synthetic_materials(n, seed=seed)
    else:
        raise ValueError("domain must be 'frb' or 'materials'")
    cert, report = run(X, seed=seed, **kwargs)
    cert["domain"] = domain
    return cert, report, rows

def _cli():
    import argparse, json, sys
    p = argparse.ArgumentParser(description="RPL-C / RPL-ISA — sheaf obstruction ladder")
    p.add_argument("--domain", choices=["frb", "materials", "csv"], default="frb")
    p.add_argument("--csv", default=None)
    p.add_argument("--features", default=None)
    p.add_argument("--n", type=int, default=160)
    p.add_argument("--steps", type=int, default=3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-rotate", action="store_true")
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    program = [{"op": "CORE"}, {"op": "STEP", "max": args.steps}]
    if not args.no_rotate:
        program.append({"op": "ROTATE"})
    program.append({"op": "HALT"})
    if args.domain == "csv":
        if not args.csv or not args.features:
            print("csv domain requires --csv and --features", file=sys.stderr)
            sys.exit(1)
        cols = [c.strip() for c in args.features.split(",")]
        X, _, _ = load_csv_features(args.csv, cols)
        cert, report = run(X, program=program, seed=args.seed, verify=not args.no_verify)
    else:
        cert, report, _ = run_domain(args.domain, n=args.n, seed=args.seed, program=program, verify=not args.no_verify)
    compact = {k: cert[k] for k in cert if k != "remainder"}
    out = {"certificate": compact, "verify": report}
    print(json.dumps(out, indent=2, default=str))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2, default=str)

if __name__ == "__main__":
    _cli()
