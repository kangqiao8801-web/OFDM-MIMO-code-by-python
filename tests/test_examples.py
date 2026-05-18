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


def test_soft_hard_siso_example_writes_outputs(tmp_path):
    out_dir = run_example("soft_hard_siso", tmp_path)

    assert (out_dir / "per.png").stat().st_size > 0
    assert (out_dir / "per.dat").stat().st_size > 0


def test_batch2_capacity_examples_write_outputs(tmp_path):
    for name in [
        "ergodic_capacity_cdf",
        "ergodic_capacity_correlation",
        "ergodic_capacity_vs_snr",
        "ol_cl_comparison",
        "pre_mmse",
        "test_orthogonality",
    ]:
        out_dir = run_example(name, tmp_path)
        assert any(path.suffix == ".png" and path.stat().st_size > 0 for path in out_dir.iterdir())
        assert any(path.suffix == ".dat" and path.stat().st_size > 0 for path in out_dir.iterdir())


def test_batch3_ofdm_sync_examples_write_outputs(tmp_path):
    for name in [
        "cfo_estimation",
        "sto_estimation",
        "ofdm_signal",
        "ccdf_ofdma",
        "pdf_clipped_filtered_ofdm_signal",
        "ccdf_clipped_filtered_ofdm_signal",
        "do_sto_cfo1",
    ]:
        out_dir = run_example(name, tmp_path)
        assert any(path.suffix == ".png" and path.stat().st_size > 0 for path in out_dir.iterdir())
        assert any(path.suffix == ".dat" and path.stat().st_size > 0 for path in out_dir.iterdir())


def test_batch4_papr_examples_write_outputs(tmp_path):
    for name in [
        "papr_of_chu",
        "papr_of_preamble",
        "parr_of_preamble",
        "compare_ccdf_pts",
        "compare_dft_spreading",
        "compare_dft_spreading_w_psf",
        "single_carrier_papr",
        "sqnr_with_quantization_clipping",
    ]:
        out_dir = run_example(name, tmp_path)
        assert any(path.suffix == ".png" and path.stat().st_size > 0 for path in out_dir.iterdir())
        assert any(path.suffix == ".dat" and path.stat().st_size > 0 for path in out_dir.iterdir())


def test_batch5_channel_model_examples_write_outputs(tmp_path):
    for name in [
        "path_loss_models",
        "doppler_fwgn_models",
        "sui_channel_models",
        "uwb_channel_models",
        "fading_channel_models",
    ]:
        out_dir = run_example(name, tmp_path)
        assert any(path.suffix == ".png" and path.stat().st_size > 0 for path in out_dir.iterdir())
        assert any(path.suffix == ".dat" and path.stat().st_size > 0 for path in out_dir.iterdir())


def test_batch6_mimo_examples_write_outputs(tmp_path):
    for name in [
        "stbc_alamouti_variants",
        "mimo_detection_algorithms",
        "mimo_precoding_algorithms",
        "mimo_capacity_ant_selection",
        "sttc_simulation",
    ]:
        out_dir = run_example(name, tmp_path)
        assert any(path.suffix == ".png" and path.stat().st_size > 0 for path in out_dir.iterdir())
        assert any(path.suffix == ".dat" and path.stat().st_size > 0 for path in out_dir.iterdir())


def test_batch7_plot_examples_write_outputs(tmp_path):
    for name in [
        "plot_2ray_exp_model",
        "plot_ccdf",
        "plot_fwgn",
        "plot_ieee80211_model",
        "plot_jakes_model",
        "plot_pl_hata",
        "plot_pl_ieee80216d",
        "plot_pl_general",
        "plot_ray_ric_channel",
        "plot_sui_channel",
        "plot_sv_model_ct",
        "plot_uwb_channel",
        "plot_ber",
        "plot_modified_fwgn",
        "plot_ray_fading",
    ]:
        out_dir = run_example(name, tmp_path)
        assert any(path.suffix == ".png" and path.stat().st_size > 0 for path in out_dir.iterdir())
        assert any(path.suffix == ".dat" and path.stat().st_size > 0 for path in out_dir.iterdir())
