# Claims ledger — rplc-sheaf

Same honesty bar as protein-rpl-validation and the author’s public verification practice:
pre-register what is claimed, separate OPEN from RESIDUE, retract when audit demands it.

## OPEN

1. **Design law in code** — OPEN only if stratum λ₁ survives size-matched random controls; residue is never forced.
2. **Certificate surface** — `isa_exec` emits JSON-stable ladder/trace; `verify_certificate` validates schema, program replay equality, remainder bounds, and rejects fatal halt reasons (`no_core`, `unknown_op`).
3. **Abstraction** — Hardware = feature matrix; Software = ISA program; ALU = sheaf obstruction; Domains = payloads only.
4. **Front-end completeness** — `run` / `run_domain` / CLI / CSV path.

## RESIDUE

1. **Scale** — dense `eigh` bounds interactive n ≲ 300; sparse shift-invert not yet shipped in this tree.
2. **`audit_margin`** — default 0.1 is a fixed heuristic; per-domain calibration deferred.
3. **ROTATE OPEN** — approximate (PC1 order mapping); flagged `approx: true` in trace.
4. **`use_persistence`** — accepted on `isa_run` but not wired through STEP path.
5. **Legacy RNG** — `RandomState` vs `default_rng` modernization pending.

## NOT CLAIMED

- Domain-specific discovery for FRB / SuperCon / ClinVar / protein folds
- Medical or diagnostic use
- Production threshold lock without further calibration

## Cross-repo

Domain application (protein IDR refuse + structure-conditioned dens authority):  
https://github.com/ZuluYokohama/protein-rpl-validation
