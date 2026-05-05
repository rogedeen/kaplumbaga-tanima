import sys
import os
import json
from PIL import Image

# Minimal stub for single-image inference
# Usage: python src/evaluate_single_image.py /path/to/image.jpg

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "no_input_path"}))
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(json.dumps({"error": "file_not_found", "path": path}))
        sys.exit(1)
    try:
        img = Image.open(path).convert('RGB')
        # Minimal validation/log message
        w, h = img.size
        # For MVP stub, we return a dummy prediction.
        # Real pipeline should load `best_384.pth` and run model inference.
        result = {
            "pred": "t001",
            "conf": 0.6115,
            "info": f"Loaded image {os.path.basename(path)} size=({w}x{h}); stub inference returned fixed result"
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": "processing_error", "msg": str(e)}))
        sys.exit(2)

if __name__ == '__main__':
    main()
