"""
批量生成多档位缩略图脚本
在每个图片所在目录生成 thumbs/320/, thumbs/640/, thumbs/1280/ 三个子目录，
保持文件名和格式不变，仅缩小宽度（等比缩放）。
如果原图宽度 <= 目标宽度，则直接复制原图（不放大）。
"""

import os
import shutil
import json
import re
import urllib.parse
import urllib.request
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
    "works/UTY",
    "works/20260522香水瓶/COMFYUIOUTPUT",
    "head",
]

WORK_PAGES = {
    "20260522香水瓶": "香水瓶作品.html",
    "DHZS": "杭州顺颂尚祺时期作品.html",
    "MLMW": "上海木里木外时期作品.html",
    "OTHER": "近期其他内容.html",
    "python": "音乐程序-python.html",
    "SHWD/ENS": "音乐程序-ue-racing.html",
    "SHWD/ZX": "音乐程序-web3d.html",
    "SHWD/BSBP": "音乐程序-ue-puzzle.html",
    "UTY": "UE相关作品.html",
    "QTZN": "杭州青缇智能时期作品.html",
}

BASE_DIR = Path(__file__).parent
SUPPORTED_EXTS = {".webp", ".png", ".jpg", ".jpeg", ".gif"}

VIDEO_PAGE_MAP = {
    "杭州青缇智能时期作品.html": ("QTZN", "杭州青缇智能时期作品.html"),
    "杭州顺颂尚祺时期作品.html": ("SHUNSONG", "杭州顺颂尚祺时期作品.html"),
    "上海伍鼎景观时期作品.html": ("ENS", "上海伍鼎景观时期作品.html"),
    "武汉理理线科技时期作品.html": ("UTY", "武汉理理线科技时期作品.html"),
    "香水瓶作品.html": ("XS", "香水瓶作品.html"),
    "音乐程序-python.html": ("python", "音乐程序-python.html"),
    "音乐程序-ue-fft.html": ("OTHER", "音乐程序-ue-fft.html"),
    "音乐程序-ue-puzzle.html": ("BSBP", "音乐程序-ue-puzzle.html"),
    "音乐程序-ue-racing.html": ("ENS", "音乐程序-ue-racing.html"),
    "音乐程序-unity.html": ("UTY", "音乐程序-unity.html"),
    "音乐程序-web3d.html": ("OTHER", "音乐程序-web3d.html"),
    "C4D业余作品.html": ("C4D", "C4D业余作品.html"),
    "UE&web3d作品.html": ("OTHER", "UE&web3d作品.html"),
    "UE相关作品.html": ("OTHER", "UE相关作品.html"),
}


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


def page_for_asset(asset_path: Path):
    relative = asset_path.relative_to(BASE_DIR / "works").as_posix()
    for source_dir, page in sorted(WORK_PAGES.items(), key=lambda item: len(item[0]), reverse=True):
        if relative.startswith(source_dir + "/"):
            return page
    return "index.html"


def write_guide_manifest():
    """输出入口页使用的完整缩略图清单，每张图片只出现一次。"""
    assets = []
    for thumb_path in sorted((BASE_DIR / "works").rglob("thumbs/640/*")):
        if not thumb_path.is_file() or thumb_path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        relative = thumb_path.relative_to(BASE_DIR).as_posix()
        source = thumb_path.parent.parent.parent.relative_to(BASE_DIR / "works").as_posix()
        assets.append({
            "title": thumb_path.stem,
            "group": source,
            "page": page_for_asset(thumb_path),
            "thumb": relative,
        })

    manifest = "window.GUIDE_WORKS = " + repr(assets).replace("'", '"') + ";\n"
    (BASE_DIR / "guide-works.js").write_text(manifest, encoding="utf-8")
    print(f"\n[入口页清单] guide-works.js ({len(assets)} 张缩略图)")


def collect_video_candidates():
    """从所有作品页收集唯一 B 站视频，并保留所属页面。"""
    pattern = re.compile(r"bvid=([A-Za-z0-9]+)")
    candidates = {}
    for page_name, (source, page) in VIDEO_PAGE_MAP.items():
        page_path = BASE_DIR / page_name
        if not page_path.exists():
            continue
        content = page_path.read_text(encoding="utf-8")
        for bvid in pattern.findall(content):
            if bvid == "BV号替换":
                continue
            candidates.setdefault(bvid, {
                "source": source,
                "page": page,
                "bvid": bvid,
                "name": f"视频作品 {bvid}",
                "thumb": f"assets/video-thumbs/{bvid}.jpg",
                "kind": "video",
            })
    return list(candidates.values())


def download_video_thumbnails():
    """下载 B 站视频封面到本地，入口页运行时不再依赖第三方接口。"""
    output_dir = BASE_DIR / "assets" / "video-thumbs"
    output_dir.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    candidates = collect_video_candidates()
    success = 0

    for video in candidates:
        bvid = video["bvid"]
        output_path = output_dir / f"{bvid}.jpg"
        if output_path.exists():
            success += 1
            continue

        try:
            api_url = "https://api.bilibili.com/x/web-interface/view?bvid=" + urllib.parse.quote(bvid)
            request = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            cover = payload["data"]["pic"].replace("//", "https://", 1)
            image_request = urllib.request.Request(cover, headers=headers)
            with urllib.request.urlopen(image_request, timeout=20) as response:
                output_path.write_bytes(response.read())
            success += 1
            print(f"  [视频封面] {bvid}")
        except Exception as error:
            print(f"  [视频封面失败] {bvid}: {error}")

    manifest = "window.GUIDE_VIDEOS = " + json.dumps(candidates, ensure_ascii=False) + ";\n"
    (BASE_DIR / "guide-videos.js").write_text(manifest, encoding="utf-8")
    print(f"\n[视频封面] 本地可用 {success}/{len(candidates)} 张")


def main():
    print("=" * 60)
    print("批量缩略图生成")
    print(f"档位: {WIDTHS}")
    print(f"基础目录: {BASE_DIR}")
    print("=" * 60)

    for rel_dir in IMAGE_DIRS:
        process_directory(rel_dir)

    write_guide_manifest()
    download_video_thumbnails()

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
