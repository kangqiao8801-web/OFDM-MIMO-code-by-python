# MATLAB 到 Python 转译清单

更新时间：2026-05-17

状态定义：`是` = 已有 Python 等价实现并通过当前测试或示例运行；`部分` = 公共能力已覆盖但还没有一对一完整验收；`否` = 尚未转译。

## 汇总

- MATLAB `.m` 文件总数：153
- 已转译成功：9
- 部分覆盖：6
- 未转译：138

| 类别 | MATLAB 程序 | 是否已经转译成功 | Python 对应位置 | 备注 |
|---|---|---|---|---|
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x1_ant_selection.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x1_precoding.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x2.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme.m` | 是 | `examples/alamouti_scheme.py` | 可运行示例，已通过 pytest 和默认运行 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme_2x1.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme_2x2.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Block_diagonalization.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Dirty_or_TH_precoding.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `LRAD_MMSE.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `MIMO_channel_cap_ant_sel_optimal.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `MIMO_channel_cap_ant_sel_subopt.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `MMSE_detection_2x2.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `MRC_scheme.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `OSIC_detector.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_detector.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_simulation.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_soft.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `SD_detector.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `SQRD_.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `STBC_3x4_simulation.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `STTC_detector.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `STTC_modulator.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `STTC_simulation.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `STTC_stage_modulation.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `Water_Pouring.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `codebook_generator.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `multi_user_MIMO.m` | 否 | - | 待转译 |
| MIMO/STBC/检测/预编码/容量 | `original_LLL_.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `CCDF_OFDMA.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `CCDF_of_clipped_filtered_OFDM_signal.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `CFO_CP.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `CFO_Classen.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `CFO_Moose.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `CFO_estimation.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `LS_CE.m` | 是 | `src/ofdm_mimo/channel_estimation.py::ls_ce` | 公共函数，已通过单元测试 |
| OFDM/同步/信道估计 | `MMSE_CE.m` | 是 | `src/ofdm_mimo/channel_estimation.py::mmse_ce` | 公共函数，已通过单元测试 |
| OFDM/同步/信道估计 | `OFDM_basic.m` | 是 | `examples/ofdm_basic.py` | 可运行示例，已通过 pytest 和默认运行 |
| OFDM/同步/信道估计 | `OFDM_signal.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `PDF_of_clipped_and_filtered_OFDM_signal.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `STO_by_correlation.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `STO_by_difference.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `STO_estimation.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `add_CFO.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `add_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::add_cp` | 公共函数，已通过单元测试 |
| OFDM/同步/信道估计 | `add_STO.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `add_pilot.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `channel_estimation.m` | 是 | `examples/channel_estimation.py` | 可运行示例，已通过 pytest 和默认运行 |
| OFDM/同步/信道估计 | `do_STO_CFO1.m` | 否 | - | 待转译 |
| OFDM/同步/信道估计 | `remove_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::remove_cp` | 公共函数，已通过单元测试 |
| OFDM/同步/信道估计 | `remove_GI.m` | 是 | `src/ofdm_mimo/ofdm.py::remove_gi` | 公共函数，已通过单元测试 |
| PAPR/CCDF/削波 | `CCDF_PAPR_DFTspreading.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `CCDF_PTS.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `IFFT_oversampling.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `PAPR.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `PAPR_of_Chu.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `PAPR_of_preamble.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `PARR_of_preamble.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `SQNR_with_quantization_clipping.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `clipping.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `compare_CCDF_PTS.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `compare_DFT_spreading.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `compare_DFT_spreading_w_psf.m` | 否 | - | 待转译 |
| PAPR/CCDF/削波 | `single_carrier_PAPR.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `Doppler_PSD_function.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `Doppler_spectrum.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `FWGN.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `FWGN_ff.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `FWGN_model.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `FWGN_tf.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `IEEE802_11_model.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `Jakes_Flat.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `PL_Hata.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `PL_IEEE80216d.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `PL_free.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `PL_logdist_or_norm.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `Ray_model.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `Ric_model.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `SUI_fading.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `SUI_parameters.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `SV_model_ct.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `UWB_convert_ct.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `UWB_model_ct.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `UWB_parameters.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `channel1.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `channel_coeff.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `convert_UWB_ct.m` | 否 | - | 待转译 |
| 信道模型/衰落/路径损耗 | `ray_fading.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_2ray_exp_model.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_CCDF.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_FWGN.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_IEEE80211_model.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_Jakes_model.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_PL_Hata.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_PL_IEEE80216d.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_PL_general.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_Ray_Ric_channel.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_SUI_channel.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_SV_model_ct.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_UWB_channel.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_ber.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_modified_FWGN.m` | 否 | - | 待转译 |
| 可视化/绘图脚本 | `plot_ray_fading.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `Ergodic_Capacity_CDF.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `Ergodic_Capacity_Correlation.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `Ergodic_Capacity_vs_SNR.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `OL_CL_Comparison.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `Q.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `assign_offset.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `bound.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `branch_metric.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `calculate_norm.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `compare_vector_norm.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `dB2w.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `deci2bin.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `equalpower_subray.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `exp_pdp.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `gen_filter.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `gen_phase.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `guard_interval.m` | 是 | `src/ofdm_mimo/ofdm.py::guard_interval` | 公共函数，已通过单元测试 |
| 工具/数值辅助 | `interpolate.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `list_length.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `pre_MMSE.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `radius_control.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `sort_matrix.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `stage_processing.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `stage_processing1.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `test_orthogonality.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `vector_comparison.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `zero_insertion.m` | 否 | - | 待转译 |
| 工具/数值辅助 | `zero_padding.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `Conv_encoder.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `QAM16_demapper.m` | 部分 | `src/ofdm_mimo/modulation.py::qam_demod` | 16QAM 能力已覆盖；尚未一对一函数入口 |
| 调制/编码/判决/误码 | `QAM16_mod.m` | 部分 | `src/ofdm_mimo/modulation.py::qam_mod` | 16QAM 能力已覆盖；尚未一对一函数入口 |
| 调制/编码/判决/误码 | `QAM16_real_slicer.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `QAM16_slicer.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `QAM16_slicer_soft.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `QPSK_demapper.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `QPSK_mapper.m` | 部分 | `src/ofdm_mimo/modulation.py::qpsk_mod` | QPSK 能力已覆盖；尚未一对一函数入口 |
| 调制/编码/判决/误码 | `Viterbi_decode.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `Viterbi_decode_soft.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `Viterbi_init.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `ber.m` | 部分 | `src/ofdm_mimo/metrics.py::bit_error_rate` | BER 核心能力已覆盖；尚未按 MATLAB 函数签名一对一验收 |
| 调制/编码/判决/误码 | `ber_QAM.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `convolution_encoder.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `data_generator.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `mapper.m` | 部分 | `src/ofdm_mimo/modulation.py` | 部分调制映射能力已覆盖；尚未覆盖完整 mapper 行为 |
| 调制/编码/判决/误码 | `modulation.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `modulator.m` | 部分 | `src/ofdm_mimo/modulation.py` | 调制核心能力已覆盖；尚未一对一函数入口 |
| 调制/编码/判决/误码 | `modulo.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `soft_decision_sigma.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `soft_hard_SISO.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `soft_output2x2.m` | 否 | - | 待转译 |
| 调制/编码/判决/误码 | `trellis_encoder.m` | 否 | - | 待转译 |
