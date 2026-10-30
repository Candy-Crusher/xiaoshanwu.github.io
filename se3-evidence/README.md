# Rigid SE(3) Evidence Atlas

Public companion website: [SE(3) Evidence Atlas](https://candy-crusher.github.io/xiaoshanwu.github.io/se3-evidence/).

This independent folder contains an exploratory **evidence-based feasibility study** of RGB-D rigid-body pseudo-labeling, starting from an actual YCBInEOAT / cracker_box_reorient 40-frame evaluation.

## Reproducibility and scope

- **Predictor:** Point2Pose ModularPipeline with an adapted RealSense configuration, SAM2-small, TAPIR, UniformFPS and robust SVD registration. This is **not** the official paper's ECCV-final benchmark configuration.
- **Inference observations:** RGB, metric depth, camera intrinsics, initial object mask only. No ground-truth pose or future masks.
- **Scoring:** Canonical object frame aligned using the initial GT pose **after** inference; the remaining 39 frames measured against independently annotated YCBInEOAT object poses.
- **Translation:** Euclidean distance between predicted and true camera-frame object origins in millimeters.
- **Rotation:** geodesic SO(3) angle in degrees.
- **Threshold success:** jointly below 20 mm and 10 degrees (reported on all eligible frames).
- **Limitations:** only one 40-frame excerpt; no generalization claim, confidence calibration, automatic discovery or unseen-object validity guarantee.

### Pilot results (verified on Harvard Slurm job 56438635)

| Metric | Translation | Rotation |
| --- | ---: | ---: |
| Mean | 4.217 mm | 2.389° |
| Median | 3.949 mm | 2.079° |
| P90 | 6.468 mm | 3.710° |
| Max | 11.896 mm | 5.547° |
| Coverage | 39/39 | 39/39 |

Real source arrays and experiment logs:
- `/n/netscratch/kempner_rcai_lab/Lab/xswu/action_conditioned_wm/outputs/ycbineoat_gt_eval_20261031_v1/metrics.json`
- `.../outputs/ycbineoat_point2pose_vis_20261031_v1/`
- `.../scripts/se3_ycb_gt_eval_v1_20261031.py`

Data: [YCBInEOAT](https://github.com/wenbowen123/iros20-6d-pose-tracking). Method: [Point2Pose](https://github.com/tzuyuan/point-to-pose).

## Site implementation

Static HTML/CSS/JavaScript, zero frontend build dependencies. `assets/data.js` contains measured per-frame numbers; `assets/media-*.js` contain base64-embedded material generated directly from measured GT/predictions. Website runs on GitHub Pages, including when opened locally from `index.html`.

To add new sequences:
1. Validate matching RGB/depth/mask/pose timestamps and coordinate system.
2. Run an existing **frozen configuration** on each sequence and report every attempted future frame.
3. Use only initial GT pose for post-hoc gauge alignment, never model initialization unless separately disclosed.
4. Add per-sequence metrics and failure examples to `assets/data.js` and website scoreboard **only after** the actual scorer has completed.
5. Always distinguish tracker loss flags from calibrated confidence/reject thresholds.

## GT benchmark work in progress

- YCBInEOAT mustard_easy_00_02 (Slurm 56441821, download/run)
- YCBInEOAT sugar_box1 (Slurm 56441849, download/run)
- DexYCB (not yet downloaded; source archives are large and subject to Google Drive access limits)
- RBO articulated per-link pose benchmark is a separate task, **not** evidence that an entire articulated object has a single SE(3).

This project reports negative results and failed coverage as first-class evidence and will not impute unmeasured scores.
