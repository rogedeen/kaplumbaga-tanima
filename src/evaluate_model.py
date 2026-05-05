import argparse
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from src.models.arcface import ArcFace
from src.models.turtle_model import TurtleModel


class ImageFolderWithPaths(Dataset):
    def __init__(self, root_dir: str, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = sorted(
            [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
        )
        self.class_to_idx = {name: idx for idx, name in enumerate(self.classes)}

        self.samples: List[Tuple[str, int]] = []
        for class_name in self.classes:
            class_dir = os.path.join(root_dir, class_name)
            for file_name in os.listdir(class_dir):
                if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    self.samples.append((os.path.join(class_dir, file_name), self.class_to_idx[class_name]))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label, img_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate ArcFace model with cosine-similarity gallery matching")
    parser.add_argument("--checkpoint", default="src/models/turtle_arcface_best.pth")
    parser.add_argument("--train-dir", default="datasets/train")
    parser.add_argument("--val-dir", default="datasets/test")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--embedding-dim", type=int, default=512)
    parser.add_argument("--model-name", default="convnext_tiny.fb_in22k_ft_in1k")
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument("--log-file", default="logs/inference_eval.log")
    return parser.parse_args()


def resolve_device(device_arg: str) -> torch.device:
    if device_arg == "cuda":
        return torch.device("cuda")
    if device_arg == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_transform():
    return transforms.Compose(
        [
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def load_checkpoint_components(
    model: TurtleModel,
    metric_fc: ArcFace,
    checkpoint_path: str,
    device: torch.device,
) -> Dict:
    checkpoint = torch.load(checkpoint_path, map_location=device)

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        if "metric_fc_state_dict" in checkpoint:
            metric_fc.load_state_dict(checkpoint["metric_fc_state_dict"], strict=False)
    elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
        model.load_state_dict(state_dict, strict=False)
    elif isinstance(checkpoint, dict):
        model.load_state_dict(checkpoint, strict=False)
    else:
        raise RuntimeError(f"Unsupported checkpoint format: {type(checkpoint)}")

    return checkpoint if isinstance(checkpoint, dict) else {}


def create_loader(root_dir: str, batch_size: int, num_workers: int, transform):
    dataset = ImageFolderWithPaths(root_dir=root_dir, transform=transform)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    return dataset, loader


def extract_embeddings(
    model: TurtleModel,
    loader: DataLoader,
    device: torch.device,
) -> Tuple[torch.Tensor, torch.Tensor, List[str]]:
    model.eval()
    all_embs = []
    all_labels = []
    all_paths: List[str] = []

    with torch.no_grad():
        for images, labels, paths in loader:
            images = images.to(device, non_blocking=True)
            emb = model(images)
            emb = F.normalize(emb, dim=1)

            all_embs.append(emb.cpu())
            all_labels.append(labels.cpu())
            all_paths.extend(paths)

    return torch.cat(all_embs, dim=0), torch.cat(all_labels, dim=0), all_paths


def build_gallery_prototypes(
    embeddings: torch.Tensor,
    labels: torch.Tensor,
    class_names: List[str],
) -> Tuple[torch.Tensor, List[str]]:
    prototypes = []
    proto_ids = []

    for class_idx, class_name in enumerate(class_names):
        mask = labels == class_idx
        class_embs = embeddings[mask]
        if class_embs.numel() == 0:
            continue
        proto = class_embs.mean(dim=0)
        proto = F.normalize(proto, dim=0)
        prototypes.append(proto)
        proto_ids.append(class_name)

    gallery_matrix = torch.stack(prototypes, dim=0)
    return gallery_matrix, proto_ids


def cosine_predict(
    query_embeddings: torch.Tensor,
    gallery_matrix: torch.Tensor,
    gallery_ids: List[str],
) -> Tuple[List[str], torch.Tensor]:
    sims = query_embeddings @ gallery_matrix.T
    conf, pred_idx = sims.max(dim=1)
    preds = [gallery_ids[idx] for idx in pred_idx.tolist()]
    return preds, conf


def append_eval_log(log_file: str, payload: Dict):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main():
    args = parse_args()
    start = time.time()

    if not os.path.exists(args.checkpoint):
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")
    if not os.path.isdir(args.train_dir):
        raise FileNotFoundError(f"Train dir not found: {args.train_dir}")
    if not os.path.isdir(args.val_dir):
        raise FileNotFoundError(f"Val/Test dir not found: {args.val_dir}")

    device = resolve_device(args.device)

    transform = build_transform()
    train_dataset, train_loader = create_loader(args.train_dir, args.batch_size, args.num_workers, transform)
    val_dataset, val_loader = create_loader(args.val_dir, args.batch_size, args.num_workers, transform)

    num_classes = len(train_dataset.classes)
    model = TurtleModel(
        num_classes=num_classes,
        model_name=args.model_name,
        embedding_dim=args.embedding_dim,
        pretrained=False,
    ).to(device)
    metric_fc = ArcFace(args.embedding_dim, num_classes).to(device)

    checkpoint_meta = load_checkpoint_components(model, metric_fc, args.checkpoint, device)

    train_embs, train_labels, _ = extract_embeddings(model, train_loader, device)
    gallery_matrix, gallery_ids = build_gallery_prototypes(train_embs, train_labels, train_dataset.classes)
    gallery_matrix = gallery_matrix.to(device)

    val_embs, val_labels, val_paths = extract_embeddings(model, val_loader, device)
    val_embs = val_embs.to(device)

    pred_ids, conf = cosine_predict(val_embs, gallery_matrix, gallery_ids)

    idx_to_class = {idx: cls_name for cls_name, idx in val_dataset.class_to_idx.items()}
    true_ids = [idx_to_class[idx] for idx in val_labels.tolist()]

    total = len(true_ids)
    correct = sum(1 for p, t in zip(pred_ids, true_ids) if p == t)
    acc = (correct / total * 100.0) if total > 0 else 0.0

    elapsed = time.time() - start

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checkpoint": args.checkpoint,
        "device": str(device),
        "num_classes": num_classes,
        "gallery_size": len(gallery_ids),
        "val_samples": total,
        "correct": correct,
        "accuracy": round(acc, 4),
        "avg_confidence": round(float(conf.mean().item()) if conf.numel() else 0.0, 6),
        "elapsed_seconds": round(elapsed, 2),
        "meta_epoch": checkpoint_meta.get("epoch", None),
        "meta_best_acc": checkpoint_meta.get("acc", None),
    }

    append_eval_log(args.log_file, result)

    print("Evaluation complete")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Optional light trace for debugging wrong predictions
    # Kept small to avoid huge stdout
    for i in range(min(5, total)):
        print(
            f"sample={os.path.basename(val_paths[i])} true={true_ids[i]} pred={pred_ids[i]} conf={float(conf[i]):.4f}"
        )


if __name__ == "__main__":
    main()
