# Xiaoshan Wu — 2027 Internship CVs

13 份针对不同岗位准备的独立 LaTeX 简历：NVIDIA 10 份，ByteDance Seed、Google、Amazon 各 1 份。

本目录的 `.tex` 与 2026-10-10 对话中交付的版本逐字节一致。导入时已逐份核对 SHA-256，没有重新改写研究内容或署名。

## 选择对应版本

| 编号 | 公司 / 岗位 | 岗位编号 | 独立 TeX |
|---|---|---|---|
| 01 | NVIDIA — Spatial Intelligence | JR2027305 | [打开 TeX](01_Xiaoshan_Wu_NVIDIA_Spatial_Intelligence_JR2027305.tex) |
| 02 | NVIDIA — Robotics | JR2025647 | [打开 TeX](02_Xiaoshan_Wu_NVIDIA_Robotics_JR2025647.tex) |
| 03 | NVIDIA — Generalist Embodied Agents Research (GEAR) | JR2025103 | [打开 TeX](03_Xiaoshan_Wu_NVIDIA_GEAR_JR2025103.tex) |
| 04 | NVIDIA — Physical AI / Foundation Models | JR2025025 | [打开 TeX](04_Xiaoshan_Wu_NVIDIA_Physical_AI_Foundation_Models_JR2025025.tex) |
| 05 | NVIDIA — Embodied and Agentic AI | JR2025792 | [打开 TeX](05_Xiaoshan_Wu_NVIDIA_Embodied_Agentic_AI_JR2025792.tex) |
| 06 | NVIDIA — Learning Embodied Skills from Human Data | JR2025405 | [打开 TeX](06_Xiaoshan_Wu_NVIDIA_Human_Data_Embodied_Skills_JR2025405.tex) |
| 07 | NVIDIA — Fundamental Generative AI | JR2025406 | [打开 TeX](07_Xiaoshan_Wu_NVIDIA_Fundamental_Generative_AI_JR2025406.tex) |
| 08 | NVIDIA — Autonomous Systems and Physical AI Research (ASPIRE) | JR2024171 | [打开 TeX](08_Xiaoshan_Wu_NVIDIA_ASPIRE_JR2024171.tex) |
| 09 | NVIDIA — AI-Mediated Reality and Interaction (AMRI) | Research-group version | [打开 TeX](09_Xiaoshan_Wu_NVIDIA_AMRI_Research_Intern_2027.tex) |
| 10 | NVIDIA — Isaac Loco-Manipulation | JR2025542 | [打开 TeX](10_Xiaoshan_Wu_NVIDIA_Isaac_Loco_Manipulation_JR2025542.tex) |
| 11 | ByteDance Seed — Multimodal Interaction & World Model | A105384 | [打开 TeX](11_Xiaoshan_Wu_ByteDance_Seed_World_Model_A105384.tex) |
| 12 | Google — Student Researcher, PhD | 134313315235963590 | [打开 TeX](12_Xiaoshan_Wu_Google_Student_Researcher_PhD_2027.tex) |
| 13 | Amazon — Frontier AI & Robotics | 10564600 | [打开 TeX](13_Xiaoshan_Wu_Amazon_Frontier_AI_Robotics_10564600.tex) |

岗位名称和编号用于区分定制版本，不代表职位当前仍开放，也不代表已经提交申请。

## 编译

每份 `.tex` 都包含完整的文档结构、格式、研究简介和论文条目。使用 **pdfLaTeX**，无需本仓库的其他文件、图片或 `.bib`；所用宏包与 `glyphtounicode.tex` 由标准 TeX 发行版提供。

可将单个 `.tex` 上传到一个独立 LaTeX 项目，也可以在同一项目内选择相应 `.tex` 为编译主文件。切换主文件即可切换岗位版本。

本地批量编译（需要已安装 pdfLaTeX）：

```bash
bash cv/2027-internships/build_all.sh
```

每份运行两次 pdfLaTeX，PDF 和日志写入本目录的 `build/`，不会覆盖网站的主 CV PDF。

## 修改与维护

每份源文件都保留以下设置：

```latex
\newcommand{\InternshipAvailability}{}
\newcommand{\ExpectedGraduation}{Aug.\ 2027}
```

确认实习起止时间后再填写 `InternshipAvailability`；留空时不显示这一行。修改任何内容或填入日期后，重新编译并检查是否仍为单页。

这 13 份是独立副本，修改其中一份不会改变其他版本。根目录 [`cv.tex`](../../cv.tex) 仍是主 CV；修改主 CV 不会自动同步至这些定制版，基础信息和论文状态的统一变更需同步维护。

本次仅新增本目录。主页、完整论文页、根目录主 CV 及原有 PDF 构建配置均不改变。
