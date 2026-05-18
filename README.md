# OFDM-MIMO Python 学习代码

本项目将《MIMO-OFDM Wireless Communications with MATLAB》配套 MATLAB 源码转译为 Python，用于学习和复现实验。

项目目标不是重新设计一套通信库，而是尽量保留原 MATLAB 程序的算法含义、变量语义和实验结构，同时使用 NumPy/SciPy/Matplotlib 写成更容易运行、测试和二次学习的 Python 版本。

## 项目完成度

截至 `2026-05-18`：

- MATLAB `.m` 源文件总数：`153`
- 已完成 Python 转译：`153`
- 部分覆盖：`0`
- 未转译：`0`
- 所有批次均已通过当前单元测试或示例运行验收

完整逐文件清单见 [TRANSLATION_CHECKLIST.md](TRANSLATION_CHECKLIST.md)。

## 已完成的转译模块

| 模块 | 数量 | 主要内容 | Python 位置 |
|---|---:|---|---|
| 调制/编码/判决/误码 | 23 | QPSK、16QAM、mapper、调制解调、卷积编码、Viterbi、软判决、BER 曲线 | `src/ofdm_mimo/modulation.py`、`coding.py`、`metrics.py`、`examples/soft_hard_siso.py` |
| 工具/数值辅助 | 27 | `Q` 函数、dB 到功率、补零、插值、排序、范数、球形译码辅助、容量示例 | `src/ofdm_mimo/utils.py`、`examples/ergodic_capacity_*.py` |
| OFDM/同步/信道估计 | 15 | CP/GI、pilot、OFDM 基础链路、CFO/STO 估计、LS/MMSE 信道估计、削波滤波 PDF/CCDF | `src/ofdm_mimo/ofdm.py`、`channel_estimation.py`、`examples/*ofdm*.py` |
| PAPR/CCDF/削波 | 13 | PAPR、OFDMA CCDF、PTS、DFT spreading、oversampling、clipping、SQNR | `src/ofdm_mimo/ofdm.py`、`examples/compare_*.py`、`examples/papr_*.py` |
| 信道模型/衰落/路径损耗 | 24 | Rayleigh/Rician、FWGN、Jakes、Doppler PSD、SUI、UWB、IEEE 802.11、Hata/802.16d/自由空间路径损耗 | `src/ofdm_mimo/channel_models.py`、`examples/*channel*.py` |
| MIMO/STBC/检测/预编码/容量 | 27 | Alamouti、MRC、MMSE、OSIC、QRM-MLD、ML 检测、LLL、STBC、STTC、码本/BD/TH 预编码、MIMO 容量和天线选择 | `src/ofdm_mimo/mimo.py`、`capacity.py`、`examples/mimo_*.py`、`examples/stbc_*.py` |
| 可视化/绘图脚本 | 15 | 原始 `plot_*` MATLAB 脚本的一对一 Python 绘图版本 | `examples/plot_*.py` |

## 目录结构

```text
.
├── MIMO-OFDM无线通信技术及MATLAB实现SourceCode  /  # 原始 MATLAB 参考源码，只读保留
├── src/ofdm_mimo/                                  # 转译后的公共 Python 函数
├── examples/                                       # 可直接运行的转译脚本和绘图脚本
├── tests/                                          # 单元测试和示例运行验收
├── outputs/                                        # 示例运行后生成的图、dat、日志等
└── TRANSLATION_CHECKLIST.md                        # 153 个 MATLAB 文件的转译清单
```

## 快速开始

本项目使用 Python 3.12，推荐用 `uv` 创建环境。

```bash
uv venv --python /opt/homebrew/bin/python3.12
uv sync
```

运行全部测试：

```bash
.venv/bin/python -m pytest
```

运行一个示例：

```bash
.venv/bin/python examples/ofdm_basic.py --quick
```

运行一个绘图脚本：

```bash
.venv/bin/python examples/plot_ccdf.py --quick
```

示例默认会把图像和数据保存到 `outputs/` 下；也可以用 `--output-dir` 指定输出目录。

## 适合如何学习

- 想从 MATLAB 代码迁移到 Python：可以对照原始 `.m` 文件、`src/ofdm_mimo/` 中的函数和 `examples/` 中的可运行脚本。
- 想学习 OFDM/MIMO 基础算法：建议从 `examples/ofdm_basic.py`、`examples/channel_estimation.py`、`examples/alamouti_scheme.py` 开始。
- 想学习 PAPR 和 CCDF：建议看 `examples/ccdf_ofdma.py`、`examples/compare_ccdf_pts.py`、`examples/compare_dft_spreading.py`。
- 想学习信道模型：建议看 `examples/fading_channel_models.py`、`examples/path_loss_models.py`、`examples/uwb_channel_models.py`。
- 想学习 MIMO 检测/预编码：建议看 `examples/mimo_detection_algorithms.py`、`examples/mimo_precoding_algorithms.py`、`examples/mimo_capacity_ant_selection.py`。

## 说明

- 原始 MATLAB 源码目录作为参考资料保留，本项目不修改其中 `.m` 和 `.dat` 文件。
- Python 版本优先保证算法含义和实验可复现性；部分长耗时仿真在 examples 中提供 `--quick` 模式，便于快速验收。
- 当前测试覆盖公共函数的数值行为，以及主要 examples 是否能成功生成图像或数据。
