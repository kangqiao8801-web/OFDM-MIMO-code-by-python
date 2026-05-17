# MATLAB 到 Python 转译清单

更新时间：2026-05-17

状态定义：`是` = 已有 Python 等价实现并通过当前测试或示例运行；`部分` = 公共能力已覆盖但还没有一对一完整验收；`否` = 尚未转译。

## 汇总

- MATLAB `.m` 文件总数：153
- 已转译成功：32
- 部分覆盖：0
- 未转译：121


## 批次方案

每完成一个批次后，需要同步更新下方主清单中的 `批次完成` 列；当一个批次内所有条目都完成并通过验收时，将该批次相关条目的 `批次完成` 更新为 `是`。

| 批次 | 范围 | 数量 | 主要交付 | 验收方式 | 批次完成 |
|---|---|---:|---|---|---|
| 1 | 调制/编码/判决/误码 | 23 | 补齐 QPSK/QAM16/mapper/Viterbi/卷积编码/BER 等公共函数与必要示例 | 单元测试覆盖 MATLAB 等价输入输出；相关示例跑通 | 是 |
| 2 | 工具/数值辅助 | 27 | `Q`、`dB2w`、补零、插值、范数、排序、MMSE 前处理等基础工具 | 单元测试为主；无图脚本保存 `.dat` 或数值摘要 | 否 |
| 3 | OFDM/同步/信道估计 | 15 | CFO/STO、pilot、OFDM signal、削波滤波 CCDF/PDF 相关脚本 | 每个 example 跑通，保存图或 `.dat` | 否 |
| 4 | PAPR/CCDF/削波 | 13 | PAPR、PTS、DFT spreading、oversampling、clipping 相关脚本 | 每个脚本生成 CCDF/PAPR/SQNR 图或数据 | 否 |
| 5 | 信道模型/衰落/路径损耗 | 24 | FWGN、Jakes、Ray/Ric、SUI、UWB、路径损耗模型 | 模型函数单测；绘图/仿真脚本生成图 | 否 |
| 6 | MIMO/STBC/检测/预编码/容量 | 27 | Alamouti 扩展、MRC、MMSE/OSIC/SD/QRM、容量、预编码、STTC | 仿真脚本 quick 模式跑通，保存 BER/容量曲线或数据 | 否 |
| 7 | 可视化/绘图脚本 | 15 | `plot_*` 脚本一对一转成 Python examples | 每个脚本生成对应 PNG | 否 |

| 类别 | MATLAB 程序 | 是否已经转译成功 | Python 对应位置 | 备注 | 实现批次 | 批次完成 |
|---|---|---|---|---|---|---|
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x1_ant_selection.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x1_precoding.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x2.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme.m` | 是 | `examples/alamouti_scheme.py` | 可运行示例，已通过 pytest 和默认运行 | 已完成 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme_2x1.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme_2x2.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Block_diagonalization.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Dirty_or_TH_precoding.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `LRAD_MMSE.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `MIMO_channel_cap_ant_sel_optimal.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `MIMO_channel_cap_ant_sel_subopt.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `MMSE_detection_2x2.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `MRC_scheme.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `OSIC_detector.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_detector.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_simulation.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_soft.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `SD_detector.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `SQRD_.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `STBC_3x4_simulation.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `STTC_detector.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `STTC_modulator.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `STTC_simulation.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `STTC_stage_modulation.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `Water_Pouring.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `codebook_generator.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `multi_user_MIMO.m` | 否 | - | 待转译 | 6 | 否 |
| MIMO/STBC/检测/预编码/容量 | `original_LLL_.m` | 否 | - | 待转译 | 6 | 否 |
| OFDM/同步/信道估计 | `CCDF_OFDMA.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `CCDF_of_clipped_filtered_OFDM_signal.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `CFO_CP.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `CFO_Classen.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `CFO_Moose.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `CFO_estimation.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `LS_CE.m` | 是 | `src/ofdm_mimo/channel_estimation.py::ls_ce` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `MMSE_CE.m` | 是 | `src/ofdm_mimo/channel_estimation.py::mmse_ce` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `OFDM_basic.m` | 是 | `examples/ofdm_basic.py` | 可运行示例，已通过 pytest 和默认运行 | 已完成 | 是 |
| OFDM/同步/信道估计 | `OFDM_signal.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `PDF_of_clipped_and_filtered_OFDM_signal.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `STO_by_correlation.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `STO_by_difference.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `STO_estimation.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `add_CFO.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `add_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::add_cp` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `add_STO.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `add_pilot.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `channel_estimation.m` | 是 | `examples/channel_estimation.py` | 可运行示例，已通过 pytest 和默认运行 | 已完成 | 是 |
| OFDM/同步/信道估计 | `do_STO_CFO1.m` | 否 | - | 待转译 | 3 | 否 |
| OFDM/同步/信道估计 | `remove_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::remove_cp` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `remove_GI.m` | 是 | `src/ofdm_mimo/ofdm.py::remove_gi` | 公共函数，已通过单元测试 | 已完成 | 是 |
| PAPR/CCDF/削波 | `CCDF_PAPR_DFTspreading.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `CCDF_PTS.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `IFFT_oversampling.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `PAPR.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `PAPR_of_Chu.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `PAPR_of_preamble.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `PARR_of_preamble.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `SQNR_with_quantization_clipping.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `clipping.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `compare_CCDF_PTS.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `compare_DFT_spreading.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `compare_DFT_spreading_w_psf.m` | 否 | - | 待转译 | 4 | 否 |
| PAPR/CCDF/削波 | `single_carrier_PAPR.m` | 否 | - | 待转译 | 4 | 否 |
| 信道模型/衰落/路径损耗 | `Doppler_PSD_function.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `Doppler_spectrum.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `FWGN.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `FWGN_ff.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `FWGN_model.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `FWGN_tf.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `IEEE802_11_model.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `Jakes_Flat.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `PL_Hata.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `PL_IEEE80216d.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `PL_free.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `PL_logdist_or_norm.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `Ray_model.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `Ric_model.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `SUI_fading.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `SUI_parameters.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `SV_model_ct.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `UWB_convert_ct.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `UWB_model_ct.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `UWB_parameters.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `channel1.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `channel_coeff.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `convert_UWB_ct.m` | 否 | - | 待转译 | 5 | 否 |
| 信道模型/衰落/路径损耗 | `ray_fading.m` | 否 | - | 待转译 | 5 | 否 |
| 可视化/绘图脚本 | `plot_2ray_exp_model.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_CCDF.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_FWGN.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_IEEE80211_model.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_Jakes_model.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_PL_Hata.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_PL_IEEE80216d.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_PL_general.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_Ray_Ric_channel.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_SUI_channel.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_SV_model_ct.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_UWB_channel.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_ber.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_modified_FWGN.m` | 否 | - | 待转译 | 7 | 否 |
| 可视化/绘图脚本 | `plot_ray_fading.m` | 否 | - | 待转译 | 7 | 否 |
| 工具/数值辅助 | `Ergodic_Capacity_CDF.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `Ergodic_Capacity_Correlation.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `Ergodic_Capacity_vs_SNR.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `OL_CL_Comparison.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `Q.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `assign_offset.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `bound.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `branch_metric.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `calculate_norm.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `compare_vector_norm.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `dB2w.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `deci2bin.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `equalpower_subray.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `exp_pdp.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `gen_filter.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `gen_phase.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `guard_interval.m` | 是 | `src/ofdm_mimo/ofdm.py::guard_interval` | 公共函数，已通过单元测试 | 已完成 | 是 |
| 工具/数值辅助 | `interpolate.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `list_length.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `pre_MMSE.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `radius_control.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `sort_matrix.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `stage_processing.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `stage_processing1.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `test_orthogonality.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `vector_comparison.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `zero_insertion.m` | 否 | - | 待转译 | 2 | 否 |
| 工具/数值辅助 | `zero_padding.m` | 否 | - | 待转译 | 2 | 否 |
| 调制/编码/判决/误码 | `Conv_encoder.m` | 是 | `src/ofdm_mimo/coding.py::conv_encoder` | 一对一卷积编码入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QAM16_demapper.m` | 是 | `src/ofdm_mimo/modulation.py::qam16_demapper` | 一对一 16QAM 解映射入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QAM16_mod.m` | 是 | `src/ofdm_mimo/modulation.py::qam16_mod` | 一对一 16QAM 映射入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QAM16_real_slicer.m` | 是 | `src/ofdm_mimo/modulation.py::qam16_real_slicer` | 一对一实部切片入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QAM16_slicer.m` | 是 | `src/ofdm_mimo/modulation.py::qam16_slicer` | 一对一 16QAM 硬切片入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QAM16_slicer_soft.m` | 是 | `src/ofdm_mimo/modulation.py::qam16_slicer_soft` | 一对一软判决比特入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QPSK_demapper.m` | 是 | `src/ofdm_mimo/modulation.py::qpsk_demapper` | 一对一 QPSK 解映射入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `QPSK_mapper.m` | 是 | `src/ofdm_mimo/modulation.py::qpsk_mapper` | 一对一 QPSK 映射入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `Viterbi_decode.m` | 是 | `src/ofdm_mimo/coding.py::viterbi_decode` | 硬判决 Viterbi 解码入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `Viterbi_decode_soft.m` | 是 | `src/ofdm_mimo/coding.py::viterbi_decode_soft` | 软判决 Viterbi 解码入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `Viterbi_init.m` | 是 | `src/ofdm_mimo/coding.py::viterbi_init` | Viterbi trellis 初始化入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `ber.m` | 是 | `src/ofdm_mimo/metrics.py::ber` | MATLAB persistent BER 语义入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `ber_QAM.m` | 是 | `src/ofdm_mimo/metrics.py::ber_qam` | 解析 BER 曲线入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `convolution_encoder.m` | 是 | `src/ofdm_mimo/coding.py::convolution_encoder` | 矩阵形式卷积编码入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `data_generator.m` | 是 | `src/ofdm_mimo/modulation.py::data_generator` | 随机数据和零尾生成入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `mapper.m` | 是 | `src/ofdm_mimo/modulation.py::mapper` | PSK/QAM 随机或完整星座生成入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `modulation.m` | 是 | `src/ofdm_mimo/modulation.py::modulate_carrier` | 载波调制波形生成入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `modulator.m` | 是 | `src/ofdm_mimo/modulation.py::modulator` | 按比特宽度调制入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `modulo.m` | 是 | `src/ofdm_mimo/modulation.py::modulo` | Tomlinson-Harashima modulo 入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `soft_decision_sigma.m` | 是 | `src/ofdm_mimo/modulation.py::soft_decision_sigma` | 软度量生成入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `soft_hard_SISO.m` | 是 | `examples/soft_hard_siso.py` | 可运行示例，quick 模式已生成 PER 图和数据 | 1 | 是 |
| 调制/编码/判决/误码 | `soft_output2x2.m` | 是 | `src/ofdm_mimo/modulation.py::soft_output2x2` | 2x2 软输出入口，已通过单元测试 | 1 | 是 |
| 调制/编码/判决/误码 | `trellis_encoder.m` | 是 | `src/ofdm_mimo/coding.py::trellis_encoder` | STTC trellis 编码入口，已通过单元测试 | 1 | 是 |
