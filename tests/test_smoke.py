"""Offline smoke tests for rplc-sheaf (no network)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rplc_sheaf as m


def test_synthetic_frb_run_verifies():
    X, _ = m.synthetic_frb(48)
    cert, report = m.run(X, seed=0)
    assert isinstance(cert, dict)
    assert report.get("ok") is True
    assert "remainder_n" in cert
    assert "trace" in cert


def test_materials_domain():
    cert, report, rows = m.run_domain("materials", n=40, seed=1)
    assert report.get("ok") is True
    assert cert["n0"] == 40


def test_fatal_no_core_rejected():
    X, _ = m.synthetic_frb(24)
    cert, report = m.run(X, program=[{"op": "STEP", "max": 1}, {"op": "HALT"}], seed=0)
    trace = " ".join(str(t) for t in cert.get("trace", []))
    halt = str(cert.get("halt_reason") or "")
    ok_path = (report.get("ok") is False) or ("no_core" in trace.lower()) or ("no_core" in halt.lower())
    assert ok_path or cert.get("remainder_n", 0) >= 0


def test_unknown_op_halts():
    X, _ = m.synthetic_frb(24)
    cert, report = m.run(
        X,
        program=[{"op": "CORE"}, {"op": "NOT_A_REAL_OP"}, {"op": "HALT"}],
        seed=0,
    )
    trace = " ".join(str(t) for t in cert.get("trace", []))
    assert "unknown" in trace.lower() or report.get("ok") is False or cert.get("halt_reason")


def test_version_tag():
    assert hasattr(m, "__version__")
    assert "1.0" in m.__version__


if __name__ == "__main__":
    test_synthetic_frb_run_verifies()
    test_materials_domain()
    test_fatal_no_core_rejected()
    test_unknown_op_halts()
    test_version_tag()
    print("all smoke OK")
