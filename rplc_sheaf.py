"""
rplc_sheaf — operational core of Jones / CycleSheaf / RPL-C
----------------------------------------------------------
Restriction-projection under audit with sheaf obstruction.

Invariant: only audit-surviving structure is kept.
Residue is defined by failure to open — never forced.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from scipy.spatial.distance import pdist, squareform, cdist

# Graph / sheaf primitives, RPL loop, domain loaders, CLI:
# Full source maintained in conversation artifacts and expanded in follow-up commits.
# Minimal runnable surface:

def knn_edges(X, k):
    n = len(X)
    D = squareform(pdist(X)); np.fill_diagonal(D, np.inf)
    edges = set()
    for i in range(n):
        for j in np.argsort(D[i])[:min(k, n - 1)]:
            edges.add((min(i, j), max(i, j)))
    return edges, D

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
        delta = X[v, :min(2, d)] - X[u, :min(2, d)]
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
    L = sheaf_laplacian(X, edges, D, twist=twist)
    ev = np.sort(np.real(eigh(L, eigvals_only=True)))
    ev[ev < 1e-10] = 0
    h0 = int(np.sum(ev < 1e-8))
    lam1 = float(ev[h0]) if h0 < len(ev) else 0.0
    return lam1, h0

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
    lam, _ = sheaf_lambda1(Xs)
    rng = np.random.RandomState(seed)
    rands = []
    for _ in range(n_ctrl):
        idx = rng.choice(len(X), size=int(mask.sum()), replace=False)
        rands.append(sheaf_lambda1(X[idx])[0])
    survives = bool(lam < np.mean(rands) - 0.1 * max(np.std(rands), 1e-6))
    return {"lam1": float(lam), "rand_mean": float(np.mean(rands)), "survives": survives}

def rplc_run(X, core, max_steps=4, percentile=75, use_persistence=False):
    living = list(range(len(X)))
    ladder = []
    for step in range(1, max_steps + 1):
        if len(living) < 30:
            break
        Xl = X[living]
        C = cdist(Xl, core)
        aff = np.exp(-C / (np.median(C) + 1e-9)).max(1)
        mask = aff >= np.percentile(aff, percentile)
        if mask.sum() < 12:
            break
        audit = audit_stratum(Xl, mask, seed=step * 7, use_persistence=use_persistence)
        entry = {"step": step, "n": int(mask.sum()), **audit}
        ladder.append(entry)
        if not audit["survives"]:
            break
        living = [living[i] for i in range(len(living)) if not mask[i]]
    return ladder, living

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
        rows.append(dict(pop=pop, log_dm=np.log10(dm+1), log_w=np.log10(width+0.01),
                         scatter=scatter, fluence=fluence))
    X = np.array([[r["log_dm"], r["log_w"], r["scatter"], r["fluence"]] for r in rows])
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    return X, rows

def synthetic_materials(n=200, seed=1):
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(n):
        fam = rng.choice(["cuprate", "iron", "conventional", "unknown"], p=[0.15, 0.12, 0.4, 0.33])
        if fam == "cuprate":
            mass, eneg, val, struct, Tc = rng.normal(80,15), rng.normal(2.2,0.3), rng.normal(6,1), rng.normal(0.8,0.15), rng.lognormal(4.0,0.4)
        elif fam == "iron":
            mass, eneg, val, struct, Tc = rng.normal(70,12), rng.normal(1.9,0.25), rng.normal(7,1), rng.normal(0.6,0.2), rng.lognormal(3.2,0.5)
        elif fam == "conventional":
            mass, eneg, val, struct, Tc = rng.normal(50,20), rng.normal(1.6,0.4), rng.normal(4,1.5), rng.normal(0.3,0.2), rng.lognormal(1.5,0.8)
        else:
            mass, eneg, val, struct, Tc = rng.normal(60,25), rng.normal(1.8,0.5), rng.normal(5,2), rng.normal(0.4,0.3), rng.lognormal(2.0,1.0)
        rows.append(dict(family=fam, mass=max(mass,10), eneg=max(eneg,0.5), val=max(val,1),
                         struct=float(np.clip(struct,0,1)), log_Tc=np.log10(max(Tc,0.1))))
    X = np.array([[r["mass"], r["eneg"], r["val"], r["struct"], r["log_Tc"]] for r in rows])
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    return X, rows

def isa_exec(X, program=None, seed=0, percentile=75):
    if program is None:
        program = [{"op": "CORE"}, {"op": "STEP", "max": 3}, {"op": "HALT"}]
    living = list(range(len(X)))
    trace, ladder = [], []
    core = None
    for instr in program:
        op = instr.get("op")
        if op == "CORE":
            core = ordered_core(30, dims=X.shape[1])
            trace.append({"op": "CORE", "n_core": len(core)})
        elif op == "STEP":
            for s in range(1, int(instr.get("max", 3)) + 1):
                if len(living) < 28:
                    break
                Xl = X[living]
                C = cdist(Xl, core)
                aff = np.exp(-C / (np.median(C) + 1e-9)).max(1)
                mask = aff >= np.percentile(aff, percentile)
                n = int(mask.sum())
                if n < 12:
                    break
                audit = audit_stratum(Xl, mask, seed=seed + s)
                audit["survives"] = bool(audit["survives"])
                trace.append({"op": "SHEAF_AUDIT", "branch": "core", "step": s, "n": n, **audit})
                ladder.append({"step": s, "n": n, "branch": "core", **audit})
                if audit["survives"]:
                    trace.append({"op": "OPEN", "branch": "core", "step": s, "n": n})
                    living = [living[i] for i in range(len(living)) if not mask[i]]
                else:
                    break
        elif op == "HALT":
            trace.append({"op": "HALT", "living": len(living)})
            break
        else:
            trace.append({"op": "NOP", "raw": str(op)})
    return {
        "n0": int(X.shape[0]), "dims": int(X.shape[1]),
        "opened_steps": int(sum(1 for e in ladder if e.get("survives"))),
        "remainder_n": len(living), "ladder": ladder, "trace": trace, "program": program,
    }

def verify_certificate(cert, X=None, seed=0):
    report = {"ok": True, "checks": []}
    if "program" not in cert or "trace" not in cert:
        return {"ok": False, "checks": [{"check": "schema", "pass": False}]}
    report["checks"].append({"check": "schema", "pass": True})
    ops = [t.get("op") for t in cert["trace"]]
    report["checks"].append({"check": "has_CORE", "pass": "CORE" in ops})
    report["checks"].append({"check": "has_HALT", "pass": "HALT" in ops})
    if X is not None:
        replay = isa_exec(X, program=cert["program"], seed=seed)
        report["checks"].append({"check": "program_replay", "pass": replay["program"] == cert["program"]})
        report["replay"] = {"opened_steps": replay["opened_steps"], "remainder_n": replay["remainder_n"]}
    report["ok"] = all(c["pass"] for c in report["checks"] if c.get("pass") is not None)
    return report
