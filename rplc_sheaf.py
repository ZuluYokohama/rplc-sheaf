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

# See full module in local artifacts; truncated push will be completed.
# PLACEHOLDER_REPLACE
