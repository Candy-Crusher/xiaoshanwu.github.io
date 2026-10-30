# Rigid SE(3) Evidence Atlas

Public shareable research page: **https://candy-crusher.github.io/xiaoshanwu.github.io/se3-evidence/**

This is a candid real-GT evaluation of whether Point2Pose-style rigid-object tracking is accurate enough for SE(3) pseudo-labels on real interaction videos. The site deliberately includes both accurate trajectories and long-horizon failures.

## Protocol

- **Method**: Point2Pose ModularPipeline, adapted configuration (SAM2 small, TAPIR, UniformFPS, SVD residual registration). **Not** the official ECCV YCBInEOAT final benchmark configuration.
- **Observation during inference**: RGB, metric Depth, camera intrinsics, **first-frame object mask only**. No future object mask, pose GT, or PointWorld tracks.
- **Evaluation only**: Align arbitrary initial predicted object coordinate gauge using the frame-zero object GT pose; evaluate all future RGB-D frames against annotated 4×4 object pose GT.
- **Translation Error**: camera-frame object-origin Euclidean error in mm, after first-pose gauge alignment.
- **Rotation Error**: SO(3) geodesic in degrees.
- **Coverage**: fraction of future frames without tracker-reported loss; not equivalent to an accuracy-calibrated confidence score.
- **Joint pass rate**: fraction of **all** future frames both under 20 mm and 10°; lost frames count as failures.
- **Source**: YCBInEOAT, `cracker_box_reorient`, `mustard_easy_00_02`, `sugar_box1` real sequences.

## Verified real-GT results

| Sequence | Frames total / future | Median Translation | Median Rotation | Tracker Coverage | Joint Pass @ 20 mm, 10° |
|---|---:|---:|---:|---:|---:|
| Cracker Box centered excerpt | 40 / 39 | 3.95 mm | 2.08° | 100% | 100% |
| Cracker Box full sequence | 375 / 374 | **2.81 mm** | **3.49°** | 100% | 100% |
| Mustard Bottle centered excerpt | 40 / 39 | 1.57 mm | 1.69° | 100% | 100% |
| Mustard Bottle full sequence | 689 / 688 | **5.20 mm** | **14.52°** | 100% | **19.2%** |
| Sugar Box centered excerpt | 40 / 39 | 1.75 mm | 1.24° | 100% | 100% |
| Sugar Box full sequence | 907 / 906 | **9.29 mm** | **6.47°** | **96.5%** | **92.1%** |

**Important counterexample:** Sugar Box 40-frame centered excerpt barely moves. A static-pose baseline has just 0.24 mm mean translation error whereas Point2Pose has 1.76 mm. Low error on this clip is NOT evidence of successful motion tracking.

**Mustard full sequence**: Q1 median rotation 3.25°, Q2 18.70°, Q3 14.88°, Q4 12.57°. The tracker reports all frames valid while the true joint pass rate collapses to 19.2%. This is evidence of **silent pose drift**. Late translation also deteriorates (Q4 median 18.44 mm). Do not equate valid 4×4 matrices or tracker loss flag with reliable pseudo-labels.

**Sugar full sequence**: 874/906 tracked, median translation 9.29 mm and rotation 6.47° on accepted frames; 92.05% all-frame joint success. The end of the sequence has lost frames and extreme rotation errors (max accepted error ~80.68°).

## Implementation

Static HTML, CSS, JavaScript; no bundler. `assets/data.js` stores measured 40-frame results; `data-full.js`, `data-mustard-full.js`, and `data-sugar-full.js` store actual full-sequence errors. The `media-*.js` modules embed original GT-versus-prediction visual comparison videos for 40-frame excerpts. Charts use real measurements, not synthetic values.

Harvard source directory:
`/n/netscratch/kempner_rcai_lab/Lab/xswu/action_conditioned_wm/`

Relevant source outputs:
- `outputs/ycbineoat_gt_eval_20261031_v1/metrics.json`
- `outputs/ycbineoat_gt_eval_full_v2/metrics.json`
- `outputs/ycbineoat_gt_eval_mustard_easy_00_02_v3/metrics.json`
- `outputs/ycbineoat_gt_eval_mustard_easy_00_02_full_v4/metrics.json`
- `outputs/ycbineoat_gt_eval_sugar_box1_v3/metrics.json`
- `outputs/ycbineoat_gt_eval_sugar_box1_full_v4/metrics.json`
- `scripts/se3_ycb_indexed_v3_launcher.py` and `scripts/se3_ycb_indexed_full_v4_launcher.py`
- `outputs/ycbineoat_point2pose_vis_20261031_v1/` and other per-sequence visualization directories.

Source data naming:
- Cracker Box poses have matching RGB/depth filename timestamps.
- Mustard and Sugar have GT files numbered `0000000.txt` … with RGB frames named as timestamps. These are aligned **by validated sorted frame indices** following the official Point2Pose YcbineoatReader convention; the index mapping and exact sequence lengths are logged. No fallback to arbitrary nearest-neighbor timestamp matching.

## Research takeaways

This **supports** rigid-object pseudo-labeling for selected real RGB-D sequences with a first-frame object mask and post-hoc gauge alignment. It **does not establish** that labels are reliable in arbitrary long interactions, that automatic object discovery works, or that tracking confidence is calibrated. The next crucial experiment is **accuracy-aware validity/rejection based on model-available observables** (tracking uncertainty, geometry, independent RGB-D reprojection), validated against pose GT but not using GT at inference.

DexYCB (https://dex-ycb.github.io/) is an external human-hand / occlusion test candidate. Its official per-subject data archives are about 12 GB with Google Drive delivery, and it has **not** yet been downloaded or evaluated here. RBO articulated data is separate per-link evaluation, not whole-object SE(3) evidence. No paid coding-agent optimization has been run; the prior API budget guard remains disabled.

Official method: https://github.com/tzuyuan/point-to-pose
Official dataset: https://github.com/wenbowen123/iros20-6d-pose-tracking
