import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_example(name: str, tmp_path: Path) -> Path:
    out_dir = tmp_path / name
    script = ROOT / "examples" / f"{name}.py"
    subprocess.run(
        [sys.executable, str(script), "--output-dir", str(out_dir), "--quick"],
        cwd=ROOT,
        check=True,
    )
    return out_dir


def test_alamouti_scheme_example_writes_outputs(tmp_path):
    out_dir = run_example("alamouti_scheme", tmp_path)

    assert (out_dir / "ber.png").stat().st_size > 0
    assert (out_dir / "ber.dat").stat().st_size > 0


def test_channel_estimation_example_writes_outputs(tmp_path):
    out_dir = run_example("channel_estimation", tmp_path)

    assert (out_dir / "channel_estimation.png").stat().st_size > 0
    assert (out_dir / "mse.dat").stat().st_size > 0


def test_ofdm_basic_example_writes_outputs(tmp_path):
    out_dir = run_example("ofdm_basic", tmp_path)

    assert (out_dir / "ber.png").stat().st_size > 0
    assert (out_dir / "OFDM_BER_AWGN_CP_GL16.dat").stat().st_size > 0
