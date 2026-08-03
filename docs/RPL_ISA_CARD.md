# RPL-ISA Program Card

## Default program
```
CORE
loop:
  RESTRICT → STRATUM
  COVER (optional knn/cycles)
  SHEAF → AUDIT
  if pass: OPEN
  else: ROTATE → SHEAF → AUDIT → OPEN or HALT
```

## Instruction meanings
| Op | ALU effect |
|----|------------|
| CORE | load generative atlas |
| RESTRICT | affinity living→core |
| STRATUM | high-aff cut |
| COVER | refine graph (knn, cycles) |
| SHEAF | L=δ0ᵀδ0 → λ1,h0 |
| AUDIT | λ1 vs random controls |
| OPEN | commit slice, shrink living |
| ROTATE | delay-embed / low-rec stratum |
| FILT | multi-cover λ1 vector |
| PERSIST | nested-cover soft modes |
| HOLONOMY | twist maps, remeasure |
| HALT | define residue |

## Abstraction
Hardware = feature matrix X
Software = ISA words
ALU = sheaf obstruction under audit
Domains = payloads only
