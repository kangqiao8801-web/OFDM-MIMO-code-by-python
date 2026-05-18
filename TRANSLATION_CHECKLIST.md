# MATLAB 到 Python 转译清单

更新时间：2026-05-18

状态定义：`是` = 已有 Python 等价实现并通过当前测试或示例运行；`部分` = 公共能力已覆盖但还没有一对一完整验收；`否` = 尚未转译。

## 汇总

- MATLAB `.m` 文件总数：153
- 已转译成功：153
- 部分覆盖：0
- 未转译：0


## 批次方案

每完成一个批次后，需要同步更新下方主清单中的 `批次完成` 列；当一个批次内所有条目都完成并通过验收时，将该批次相关条目的 `批次完成` 更新为 `是`。

| 批次 | 范围 | 数量 | 主要交付 | 验收方式 | 批次完成 |
|---|---|---:|---|---|---|
| 1 | 调制/编码/判决/误码 | 23 | 补齐 QPSK/QAM16/mapper/Viterbi/卷积编码/BER 等公共函数与必要示例 | 单元测试覆盖 MATLAB 等价输入输出；相关示例跑通 | 是 |
| 2 | 工具/数值辅助 | 27 | `Q`、`dB2w`、补零、插值、范数、排序、MMSE 前处理等基础工具 | 单元测试为主；无图脚本保存 `.dat` 或数值摘要 | 是 |
| 3 | OFDM/同步/信道估计 | 15 | CFO/STO、pilot、OFDM signal、削波滤波 CCDF/PDF 相关脚本 | 每个 example 跑通，保存图或 `.dat` | 是 |
| 4 | PAPR/CCDF/削波 | 13 | PAPR、PTS、DFT spreading、oversampling、clipping 相关脚本 | 每个脚本生成 CCDF/PAPR/SQNR 图或数据 | 是 |
| 5 | 信道模型/衰落/路径损耗 | 24 | FWGN、Jakes、Ray/Ric、SUI、UWB、路径损耗模型 | 模型函数单测；绘图/仿真脚本生成图 | 是 |
| 6 | MIMO/STBC/检测/预编码/容量 | 27 | Alamouti 扩展、MRC、MMSE/OSIC/SD/QRM、容量、预编码、STTC | 仿真脚本 quick 模式跑通，保存 BER/容量曲线或数据 | 是 |
| 7 | 可视化/绘图脚本 | 15 | `plot_*` 脚本一对一转成 Python examples | 每个脚本生成对应 PNG | 是 |

| 类别 | MATLAB 程序 | 是否已经转译成功 | Python 对应位置 | 备注 | 实现批次 | 批次完成 |
|---|---|---|---|---|---|---|
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x1_ant_selection.m` | 是 | `src/ofdm_mimo/mimo.py::alamouti_encode`; `examples/stbc_alamouti_variants.py` | Alamouti 发射选择相关 STBC 链路已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x1_precoding.m` | 是 | `src/ofdm_mimo/mimo.py::codebook_generator`; `examples/mimo_precoding_algorithms.py` | 码本预编码相关入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_2x2.m` | 是 | `src/ofdm_mimo/mimo.py::alamouti_combine_2rx`; `examples/stbc_alamouti_variants.py` | 2Tx2Rx Alamouti 合并入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme.m` | 是 | `examples/alamouti_scheme.py` | 可运行示例，已通过 pytest 和默认运行 | 已完成 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme_2x1.m` | 是 | `src/ofdm_mimo/mimo.py::alamouti_decode_2x1`; `examples/stbc_alamouti_variants.py` | 2Tx1Rx Alamouti 解码入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Alamouti_scheme_2x2.m` | 是 | `src/ofdm_mimo/mimo.py::alamouti_combine_2rx`; `examples/stbc_alamouti_variants.py` | 2Tx2Rx Alamouti 解码入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Block_diagonalization.m` | 是 | `src/ofdm_mimo/mimo.py::block_diagonalization_precoders`; `examples/mimo_precoding_algorithms.py` | BD 预编码入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Dirty_or_TH_precoding.m` | 是 | `src/ofdm_mimo/mimo.py::dirty_or_th_precoding`; `examples/mimo_precoding_algorithms.py` | Dirty/TH 预编码入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `LRAD_MMSE.m` | 是 | `src/ofdm_mimo/mimo.py::lrad_mmse`; `examples/mimo_detection_algorithms.py` | LRAD-MMSE 检测入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `MIMO_channel_cap_ant_sel_optimal.m` | 是 | `src/ofdm_mimo/mimo.py::mimo_capacity_ant_selection_optimal`; `examples/mimo_capacity_ant_selection.py` | 最优天线选择容量入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `MIMO_channel_cap_ant_sel_subopt.m` | 是 | `src/ofdm_mimo/mimo.py::mimo_capacity_ant_selection_suboptimal`; `examples/mimo_capacity_ant_selection.py` | 次优天线选择容量入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `MMSE_detection_2x2.m` | 是 | `src/ofdm_mimo/mimo.py::mmse_detect`; `examples/mimo_detection_algorithms.py` | 2x2 MMSE 检测入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `MRC_scheme.m` | 是 | `src/ofdm_mimo/mimo.py::mrc_combine`; `examples/mimo_detection_algorithms.py` | MRC 合并入口已通过单元测试；检测示例 quick 运行通过 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `OSIC_detector.m` | 是 | `src/ofdm_mimo/mimo.py::osic_detector`; `examples/mimo_detection_algorithms.py` | OSIC 检测入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_detector.m` | 是 | `src/ofdm_mimo/mimo.py::qrm_mld_detector`; `examples/mimo_detection_algorithms.py` | QRM-MLD 检测入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_simulation.m` | 是 | `examples/mimo_detection_algorithms.py` | QRM-MLD 仿真 quick 模式已生成检测曲线和数据 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `QRM_MLD_soft.m` | 是 | `src/ofdm_mimo/mimo.py::qrm_mld_soft`; `examples/mimo_detection_algorithms.py` | QRM-MLD soft LLR 入口已通过单元测试 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `SD_detector.m` | 是 | `src/ofdm_mimo/mimo.py::exhaustive_ml_detector`; `examples/mimo_detection_algorithms.py` | 球形译码验收以等价 ML 检测入口覆盖，已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `SQRD_.m` | 是 | `src/ofdm_mimo/mimo.py::sqrd`; `examples/mimo_detection_algorithms.py` | Sorted QR 分解入口已通过单元测试 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `STBC_3x4_simulation.m` | 是 | `src/ofdm_mimo/mimo.py::stbc_3x4_code`; `examples/stbc_alamouti_variants.py` | 3Tx STBC 编码入口已通过单元测试；STBC 示例 quick 运行通过 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `STTC_detector.m` | 是 | `src/ofdm_mimo/mimo.py::sttc_detector`; `examples/sttc_simulation.py` | STTC Viterbi 检测入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `STTC_modulator.m` | 是 | `src/ofdm_mimo/mimo.py::sttc_modulator`; `examples/sttc_simulation.py` | STTC 调制入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `STTC_simulation.m` | 是 | `examples/sttc_simulation.py` | STTC 仿真 quick 模式已生成 FER 曲线和数据 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `STTC_stage_modulation.m` | 是 | `src/ofdm_mimo/mimo.py::sttc_stage_modulation`; `examples/sttc_simulation.py` | STTC 状态调制表入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `Water_Pouring.m` | 是 | `src/ofdm_mimo/capacity.py::water_pouring`; `examples/mimo_capacity_ant_selection.py` | 注水功率分配入口和容量示例已通过 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `codebook_generator.m` | 是 | `src/ofdm_mimo/mimo.py::codebook_generator`; `examples/mimo_precoding_algorithms.py` | 4Tx 码本生成入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `multi_user_MIMO.m` | 是 | `src/ofdm_mimo/mimo.py::multi_user_precoder`; `examples/mimo_precoding_algorithms.py` | 多用户预编码入口与示例已通过单元测试与 quick 运行 | 6 | 是 |
| MIMO/STBC/检测/预编码/容量 | `original_LLL_.m` | 是 | `src/ofdm_mimo/mimo.py::original_lll`; `examples/mimo_detection_algorithms.py` | LLL 约简入口已通过单元测试 | 6 | 是 |
| OFDM/同步/信道估计 | `CCDF_OFDMA.m` | 是 | `src/ofdm_mimo/ofdm.py::ccdf_ofdma`; `examples/ccdf_ofdma.py` | 公共函数和可运行示例，已通过 pytest 与 quick 运行 | 3 | 是 |
| OFDM/同步/信道估计 | `CCDF_of_clipped_filtered_OFDM_signal.m` | 是 | `examples/ccdf_clipped_filtered_ofdm_signal.py` | 可运行示例，quick 模式已生成 CCDF 图和数据 | 3 | 是 |
| OFDM/同步/信道估计 | `CFO_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::cfo_cp` | CP CFO 估计入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `CFO_Classen.m` | 是 | `src/ofdm_mimo/ofdm.py::cfo_classen` | Classen CFO 估计入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `CFO_Moose.m` | 是 | `src/ofdm_mimo/ofdm.py::cfo_moose` | Moose CFO 估计入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `CFO_estimation.m` | 是 | `examples/cfo_estimation.py` | 可运行示例，quick 模式已生成 CFO MSE 图和数据 | 3 | 是 |
| OFDM/同步/信道估计 | `LS_CE.m` | 是 | `src/ofdm_mimo/channel_estimation.py::ls_ce` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `MMSE_CE.m` | 是 | `src/ofdm_mimo/channel_estimation.py::mmse_ce` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `OFDM_basic.m` | 是 | `examples/ofdm_basic.py` | 可运行示例，已通过 pytest 和默认运行 | 已完成 | 是 |
| OFDM/同步/信道估计 | `OFDM_signal.m` | 是 | `examples/ofdm_signal.py` | 可运行示例，quick 模式已生成 OFDM 分量和 PDF 图 | 3 | 是 |
| OFDM/同步/信道估计 | `PDF_of_clipped_and_filtered_OFDM_signal.m` | 是 | `examples/pdf_clipped_filtered_ofdm_signal.py` | 可运行示例，quick 模式已生成 PDF/PSD 图和数据 | 3 | 是 |
| OFDM/同步/信道估计 | `STO_by_correlation.m` | 是 | `src/ofdm_mimo/ofdm.py::sto_by_correlation` | 相关法 STO 估计入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `STO_by_difference.m` | 是 | `src/ofdm_mimo/ofdm.py::sto_by_difference` | 差分法 STO 估计入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `STO_estimation.m` | 是 | `examples/sto_estimation.py` | 可运行示例，quick 模式已生成 STO 估计图和数据 | 3 | 是 |
| OFDM/同步/信道估计 | `add_CFO.m` | 是 | `src/ofdm_mimo/ofdm.py::add_cfo` | CFO 注入入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `add_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::add_cp` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `add_STO.m` | 是 | `src/ofdm_mimo/ofdm.py::add_sto` | STO 注入入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `add_pilot.m` | 是 | `src/ofdm_mimo/ofdm.py::add_pilot` | CAZAC pilot 插入入口，已通过单元测试 | 3 | 是 |
| OFDM/同步/信道估计 | `channel_estimation.m` | 是 | `examples/channel_estimation.py` | 可运行示例，已通过 pytest 和默认运行 | 已完成 | 是 |
| OFDM/同步/信道估计 | `do_STO_CFO1.m` | 是 | `examples/do_sto_cfo1.py` | 可运行帧同步/CFO 示例，quick 模式已生成图和数据 | 3 | 是 |
| OFDM/同步/信道估计 | `remove_CP.m` | 是 | `src/ofdm_mimo/ofdm.py::remove_cp` | 公共函数，已通过单元测试 | 已完成 | 是 |
| OFDM/同步/信道估计 | `remove_GI.m` | 是 | `src/ofdm_mimo/ofdm.py::remove_gi` | 公共函数，已通过单元测试 | 已完成 | 是 |
| PAPR/CCDF/削波 | `CCDF_PAPR_DFTspreading.m` | 是 | `src/ofdm_mimo/ofdm.py::ccdf_papr_dft_spreading` | DFT spreading CCDF 公共函数，已通过单元测试 | 4 | 是 |
| PAPR/CCDF/削波 | `CCDF_PTS.m` | 是 | `src/ofdm_mimo/ofdm.py::ccdf_pts` | PTS CCDF 公共函数，已通过单元测试 | 4 | 是 |
| PAPR/CCDF/削波 | `IFFT_oversampling.m` | 是 | `src/ofdm_mimo/ofdm.py::ifft_oversampling` | MATLAB 中间补零 oversampling 语义，已通过单元测试 | 4 | 是 |
| PAPR/CCDF/削波 | `PAPR.m` | 是 | `src/ofdm_mimo/ofdm.py::papr` | PAPR/平均功率/峰值功率 dB 入口，已通过单元测试 | 4 | 是 |
| PAPR/CCDF/削波 | `PAPR_of_Chu.m` | 是 | `examples/papr_of_chu.py` | 可运行示例，quick 模式已生成 Chu 序列 PAPR 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `PAPR_of_preamble.m` | 是 | `examples/papr_of_preamble.py` | 可运行示例，quick 模式已生成 preamble PAPR 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `PARR_of_preamble.m` | 是 | `examples/parr_of_preamble.py` | 可运行示例，复现原 MATLAB 同名脚本的 preamble PAPR/PARR 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `SQNR_with_quantization_clipping.m` | 是 | `examples/sqnr_with_quantization_clipping.py` | 可运行示例，quick 模式已生成量化削波 SQNR 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `clipping.m` | 是 | `src/ofdm_mimo/ofdm.py::clipping` | MATLAB sigma 削波语义，已通过单元测试 | 4 | 是 |
| PAPR/CCDF/削波 | `compare_CCDF_PTS.m` | 是 | `examples/compare_ccdf_pts.py` | 可运行示例，quick 模式已生成 OFDMA/PTS CCDF 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `compare_DFT_spreading.m` | 是 | `examples/compare_dft_spreading.py` | 可运行示例，quick 模式已生成 OFDMA/LFDMA/IFDMA CCDF 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `compare_DFT_spreading_w_psf.m` | 是 | `examples/compare_dft_spreading_w_psf.py` | 可运行示例，quick 模式已生成脉冲成形 CCDF 图和数据 | 4 | 是 |
| PAPR/CCDF/削波 | `single_carrier_PAPR.m` | 是 | `examples/single_carrier_papr.py` | 可运行示例，quick 模式已生成单载波基带/通带 PAPR 图和数据 | 4 | 是 |
| 信道模型/衰落/路径损耗 | `Doppler_PSD_function.m` | 是 | `src/ofdm_mimo/channel_models.py::doppler_psd`; `examples/doppler_fwgn_models.py` | Doppler PSD 公共函数和可运行示例，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `Doppler_spectrum.m` | 是 | `src/ofdm_mimo/channel_models.py::doppler_spectrum`; `examples/doppler_fwgn_models.py` | Clarke/Gan Doppler 频谱入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `FWGN.m` | 是 | `src/ofdm_mimo/channel_models.py::fwgn`; `examples/doppler_fwgn_models.py` | FWGN 频域衰落生成入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `FWGN_ff.m` | 是 | `src/ofdm_mimo/channel_models.py::fwgn_ff`; `examples/doppler_fwgn_models.py` | FWGN 频域滤波多径衰落入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `FWGN_model.m` | 是 | `src/ofdm_mimo/channel_models.py::fwgn`; `examples/doppler_fwgn_models.py` | 与 FWGN.m 同算法入口复用，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `FWGN_tf.m` | 是 | `src/ofdm_mimo/channel_models.py::fwgn_tf`; `examples/doppler_fwgn_models.py` | FWGN 时域滤波多径衰落入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `IEEE802_11_model.m` | 是 | `src/ofdm_mimo/channel_models.py::ieee802_11_model` | IEEE 802.11 PDP 入口，已通过单元测试 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `Jakes_Flat.m` | 是 | `src/ofdm_mimo/channel_models.py::jakes_flat`; `examples/doppler_fwgn_models.py` | Jakes flat fading 入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `PL_Hata.m` | 是 | `src/ofdm_mimo/channel_models.py::pl_hata`; `examples/path_loss_models.py` | Hata 路径损耗入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `PL_IEEE80216d.m` | 是 | `src/ofdm_mimo/channel_models.py::pl_ieee80216d`; `examples/path_loss_models.py` | IEEE 802.16d 路径损耗入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `PL_free.m` | 是 | `src/ofdm_mimo/channel_models.py::pl_free`; `examples/path_loss_models.py` | 自由空间路径损耗入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `PL_logdist_or_norm.m` | 是 | `src/ofdm_mimo/channel_models.py::pl_logdist_or_norm`; `examples/path_loss_models.py` | log-distance/log-normal 路径损耗入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `Ray_model.m` | 是 | `src/ofdm_mimo/channel_models.py::ray_model`; `examples/fading_channel_models.py` | Rayleigh 信道入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `Ric_model.m` | 是 | `src/ofdm_mimo/channel_models.py::ric_model`; `examples/fading_channel_models.py` | Rician 信道入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `SUI_fading.m` | 是 | `src/ofdm_mimo/channel_models.py::sui_fading`; `examples/sui_channel_models.py` | SUI 衰落生成入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `SUI_parameters.m` | 是 | `src/ofdm_mimo/channel_models.py::sui_parameters`; `examples/sui_channel_models.py` | SUI 参数表入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `SV_model_ct.m` | 是 | `src/ofdm_mimo/channel_models.py::sv_model_ct`; `examples/uwb_channel_models.py` | S-V 连续时间信道入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `UWB_convert_ct.m` | 是 | `src/ofdm_mimo/channel_models.py::uwb_convert_ct`; `examples/uwb_channel_models.py` | UWB 连续到离散转换别名入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `UWB_model_ct.m` | 是 | `src/ofdm_mimo/channel_models.py::uwb_model_ct`; `examples/uwb_channel_models.py` | UWB 连续时间信道入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `UWB_parameters.m` | 是 | `src/ofdm_mimo/channel_models.py::uwb_parameters`; `examples/uwb_channel_models.py` | UWB CM 参数表入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `channel1.m` | 是 | `src/ofdm_mimo/channel_models.py::channel1`; `examples/fading_channel_models.py` | MIMO 信道加噪入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `channel_coeff.m` | 是 | `src/ofdm_mimo/channel_models.py::channel_coeff`; `examples/fading_channel_models.py` | 相关 MIMO Rayleigh 信道入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `convert_UWB_ct.m` | 是 | `src/ofdm_mimo/channel_models.py::convert_uwb_ct`; `examples/uwb_channel_models.py` | UWB 连续到离散转换入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 信道模型/衰落/路径损耗 | `ray_fading.m` | 是 | `src/ofdm_mimo/channel_models.py::ray_fading`; `examples/fading_channel_models.py` | 几何子径 Rayleigh fading 入口，已通过单元测试与 quick 运行 | 5 | 是 |
| 可视化/绘图脚本 | `plot_2ray_exp_model.m` | 是 | `examples/plot_2ray_exp_model.py` | 一对一绘图示例，quick 模式已生成 2-ray/指数 PDP 图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_CCDF.m` | 是 | `examples/plot_ccdf.py` | 一对一绘图示例，quick 模式已生成 OFDM PAPR CCDF 图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_FWGN.m` | 是 | `examples/plot_fwgn.py` | 一对一绘图示例，quick 模式已生成 FWGN 包络/幅相直方图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_IEEE80211_model.m` | 是 | `examples/plot_ieee80211_model.py` | 一对一绘图示例，quick 模式已生成 IEEE 802.11 PDP/频响图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_Jakes_model.m` | 是 | `examples/plot_jakes_model.py` | 一对一绘图示例，quick 模式已生成 Jakes 包络、相关和 Doppler 图及数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_PL_Hata.m` | 是 | `examples/plot_pl_hata.py` | 一对一绘图示例，quick 模式已生成 Hata 路径损耗图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_PL_IEEE80216d.m` | 是 | `examples/plot_pl_ieee80216d.py` | 一对一绘图示例，quick 模式已生成 IEEE 802.16d 路径损耗图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_PL_general.m` | 是 | `examples/plot_pl_general.py` | 一对一绘图示例，quick 模式已生成通用路径损耗图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_Ray_Ric_channel.m` | 是 | `examples/plot_ray_ric_channel.py` | 一对一绘图示例，quick 模式已生成 Rayleigh/Rician 幅度直方图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_SUI_channel.m` | 是 | `examples/plot_sui_channel.py` | 一对一绘图示例，quick 模式已生成 SUI PDP/时变衰落/Doppler 图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_SV_model_ct.m` | 是 | `examples/plot_sv_model_ct.py` | 一对一绘图示例，quick 模式已生成 S-V 到达分布/冲激响应/阴影图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_UWB_channel.m` | 是 | `examples/plot_uwb_channel.py` | 一对一绘图示例，quick 模式已生成 UWB 信道统计图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_ber.m` | 是 | `examples/plot_ber.py` | 一对一绘图示例，支持 `--input` 仿真数据，quick 模式已生成解析/仿真 BER 图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_modified_FWGN.m` | 是 | `examples/plot_modified_fwgn.py` | 一对一绘图示例，quick 模式已生成 modified FWGN 频域/时域图和数据 | 7 | 是 |
| 可视化/绘图脚本 | `plot_ray_fading.m` | 是 | `examples/plot_ray_fading.py` | 一对一绘图示例，quick 模式已生成 SCM Ray fading 包络图和数据 | 7 | 是 |
| 工具/数值辅助 | `Ergodic_Capacity_CDF.m` | 是 | `examples/ergodic_capacity_cdf.py` | 可运行示例，quick 模式已生成 CDF 图和数据 | 2 | 是 |
| 工具/数值辅助 | `Ergodic_Capacity_Correlation.m` | 是 | `examples/ergodic_capacity_correlation.py` | 可运行示例，quick 模式已生成相关容量图和数据 | 2 | 是 |
| 工具/数值辅助 | `Ergodic_Capacity_vs_SNR.m` | 是 | `examples/ergodic_capacity_vs_snr.py` | 可运行示例，quick 模式已生成容量曲线和数据 | 2 | 是 |
| 工具/数值辅助 | `OL_CL_Comparison.m` | 是 | `examples/ol_cl_comparison.py` | 可运行示例，quick 模式已生成开闭环容量图和数据 | 2 | 是 |
| 工具/数值辅助 | `Q.m` | 是 | `src/ofdm_mimo/utils.py::qfunc` | Q 函数入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `assign_offset.m` | 是 | `src/ofdm_mimo/utils.py::assign_offset` | AoA/AoD offset 入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `bound.m` | 是 | `src/ofdm_mimo/utils.py::bound` | 球形译码边界计算入口，已提供显式参数版本 | 2 | 是 |
| 工具/数值辅助 | `branch_metric.m` | 是 | `src/ofdm_mimo/utils.py::branch_metric` | 分支度量入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `calculate_norm.m` | 是 | `src/ofdm_mimo/utils.py::calculate_norm` | QRM/MLD norm 计算入口，已提供显式参数版本 | 2 | 是 |
| 工具/数值辅助 | `compare_vector_norm.m` | 是 | `src/ofdm_mimo/utils.py::compare_vector_norm` | 球形译码候选比较入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `dB2w.m` | 是 | `src/ofdm_mimo/utils.py::db2w` | dB 到线性功率入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `deci2bin.m` | 是 | `src/ofdm_mimo/utils.py::deci2bin` | 十进制转 bit 向量入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `equalpower_subray.m` | 是 | `src/ofdm_mimo/utils.py::equalpower_subray` | SCM 子径角偏移入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `exp_pdp.m` | 是 | `src/ofdm_mimo/utils.py::exp_pdp` | 指数 PDP 入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `gen_filter.m` | 是 | `src/ofdm_mimo/utils.py::gen_filter` | Doppler FIR 滤波器入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `gen_phase.m` | 是 | `src/ofdm_mimo/utils.py::gen_phase` | BS/MS 相位和角度生成入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `guard_interval.m` | 是 | `src/ofdm_mimo/ofdm.py::guard_interval` | 公共函数，已通过单元测试 | 已完成 | 是 |
| 工具/数值辅助 | `interpolate.m` | 是 | `src/ofdm_mimo/utils.py::interpolate` | 信道插值入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `list_length.m` | 是 | `src/ofdm_mimo/utils.py::list_length` | 候选列表长度入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `pre_MMSE.m` | 是 | `examples/pre_mmse.py` | 可运行示例，quick 模式已生成 BER 图和数据 | 2 | 是 |
| 工具/数值辅助 | `radius_control.m` | 是 | `src/ofdm_mimo/utils.py::radius_control` | 球形译码半径控制入口，已提供显式参数版本 | 2 | 是 |
| 工具/数值辅助 | `sort_matrix.m` | 是 | `src/ofdm_mimo/utils.py::sort_matrix` | 矩阵排序入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `stage_processing.m` | 是 | `src/ofdm_mimo/utils.py::stage_processing` | 球形译码 stage 处理入口，已提供显式参数版本 | 2 | 是 |
| 工具/数值辅助 | `stage_processing1.m` | 是 | `src/ofdm_mimo/utils.py::stage_processing1` | QRM/MLD stage 处理入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `test_orthogonality.m` | 是 | `examples/test_orthogonality.py` | 可运行示例，quick 模式已生成正交性图和数据 | 2 | 是 |
| 工具/数值辅助 | `vector_comparison.m` | 是 | `src/ofdm_mimo/utils.py::vector_comparison` | 向量比较入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `zero_insertion.m` | 是 | `src/ofdm_mimo/utils.py::zero_insertion` | 零插入入口，已通过单元测试 | 2 | 是 |
| 工具/数值辅助 | `zero_padding.m` | 是 | `src/ofdm_mimo/utils.py::zero_padding` | 中心补零入口，已通过单元测试 | 2 | 是 |
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
