# 模型训练与优化指南

本项目默认使用 `facenet-pytorch` 提取人脸 embedding。  
为了提升当前业务场景下的识别分离度，新增了两步“轻量训练”：

- 投影头训练（PCA + LDA）
- 匹配阈值校准（genuine/impostor pair）

输出文件：

- `models/facenet/projection_head.npz`
- `models/facenet/threshold.json`

启用方式（`.env`）：

```env
FACE_PROJECTION_PATH=../models/facenet/projection_head.npz
FACE_THRESHOLD_PATH=../models/facenet/threshold.json
```

## 一键流程

```bash
cd scripts/model
python train_pipeline.py
```

注意：如果环境里没有 `facenet-pytorch`，脚本会自动退回 `fallback` 特征提取器，仅用于流程验证，精度不代表生产效果。

## 分步执行

1. 下载 LFW 子集并导出为 ImageFolder

```bash
python download_lfw.py --output ../../datasets/lfw_people --min-faces 20 --max-per-class 30
```

2. 训练投影头

```bash
python train_projection.py --dataset ../../datasets/lfw_people --backend facenet
```

3. 标定阈值

```bash
python calibrate_threshold.py --dataset ../../datasets/lfw_people --backend facenet
```

## 运行时自动加载

后端会自动读取：

- `FACE_PROJECTION_PATH`
- `FACE_THRESHOLD_PATH`

未找到文件时自动回退到默认阈值与原始 embedding。
