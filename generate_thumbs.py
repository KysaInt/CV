"""
批量生成多档位缩略图脚本
在每个图片所在目录生成 thumbs/320/, thumbs/640/, thumbs/1280/ 三个子目录，
保持文件名和格式不变，仅缩小宽度（等比缩放）。
如果原图宽度 <= 目标宽度，则直接复制原图（不放大）。
"""

import os
import shutil
from pathlib import Path
from PIL import Image

# 缩略图宽度档位
WIDTHS = [320, 640, 1280]

# 需要处理的图片目录及其扩展名
IMAGE_DIRS = [
    "works/DHZS",
    "works/MLMW",
    "works/SHWD/ENS",
    "works/SHWD/ZX",
    "works/SHWD/BSBP",
    "works/OTHER",
    "works/python",
    "head",
]

BASE_DIR = Path(__file__).parent
SUPPORTED_EXTS = {".webp", ".png", ".jpg", ".jpeg", ".gif"}


def generate_thumbnails(src_path: Path, dest_dir: Path, width: int):
    """为单张图片生成指定宽度缩略图"""
    dest_path = dest_dir / src_path.name

    if dest_path.exists():
        # 跳过已存在的缩略图
        return "skipped"

    try:
        with Image.open(src_path) as img:
            orig_w, orig_h = img.size

            if orig_w <= width:
                # 原图宽度更小，直接复制
                shutil.copy2(src_path, dest_path)
                return "copied"

            # 等比缩放
            ratio = width / orig_w
            new_h = int(orig_h * ratio)
            resized = img.resize((width, new_h), Image.LANCZOS)

            # 保存，保持原格式
            ext = src_path.suffix.lower()
            if ext == ".webp":
                resized.save(dest_path, "WEBP", quality=80, method=4)
            elif ext == ".png":
                resized.save(dest_path, "PNG", optimize=True)
            elif ext in (".jpg", ".jpeg"):
                resized.save(dest_path, "JPEG", quality=85, optimize=True)
            elif ext == ".gif":
                resized.save(dest_path, "GIF")
            else:
                resized.save(dest_path)

            return "resized"
    except Exception as e:
        print(f"  [ERROR] {src_path}: {e}")
        return "error"


def process_directory(rel_dir: str):
    """处理一个图片目录"""
    abs_dir = BASE_DIR / rel_dir
    if not abs_dir.is_dir():
        print(f"[SKIP] 目录不存在: {rel_dir}")
        return

    # 收集图片文件
    images = sorted([
        f for f in abs_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ])

    if not images:
        print(f"[SKIP] 无图片: {rel_dir}")
        return

    print(f"\n[处理] {rel_dir} ({len(images)} 张图片)")

    for width in WIDTHS:
        thumb_dir = abs_dir / "thumbs" / str(width)
        thumb_dir.mkdir(parents=True, exist_ok=True)

        stats = {"resized": 0, "copied": 0, "skipped": 0, "error": 0}
        for img_path in images:
            result = generate_thumbnails(img_path, thumb_dir, width)
            stats[result] += 1

        print(f"  {width}w: {stats['resized']} resized, {stats['copied']} copied, "
              f"{stats['skipped']} skipped, {stats['error']} errors")


def main():
    print("=" * 60)
    print("批量缩略图生成")
    print(f"档位: {WIDTHS}")
    print(f"基础目录: {BASE_DIR}")
    print("=" * 60)

    for rel_dir in IMAGE_DIRS:
        process_directory(rel_dir)

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
