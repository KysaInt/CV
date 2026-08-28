"""Batch-capture video thumbnails from loaded video pages.

Usage:
    python download_video_thumbnails.py

Requires Playwright once:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import re
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

from PIL import Image, ImageStat

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError as error:
    raise SystemExit(
        "Playwright is required. Run: pip install playwright && playwright install chromium"
    ) from error


ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "assets" / "video-thumbs"
MANIFEST_PATH = ROOT / "guide-videos.js"
BVID_PATTERN = re.compile(r"bvid=([A-Za-z0-9]+)", re.IGNORECASE)
IFRAME_PATTERN = re.compile(r"<iframe\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)

PAGE_META = {
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


@dataclass
class VideoAsset:
    source: str
    page: str
    bvid: str
    name: str
    thumb: str
    kind: str = "video"


def page_title(page_name: str) -> str:
    return Path(page_name).stem


def iter_video_assets() -> Iterable[VideoAsset]:
    seen: set[str] = set()
    for page_name, (source, page) in PAGE_META.items():
        page_path = ROOT / page_name
        if not page_path.exists():
            continue
        content = page_path.read_text(encoding="utf-8")
        index = 0
        for iframe_src in IFRAME_PATTERN.findall(content):
            match = BVID_PATTERN.search(html.unescape(iframe_src))
            if not match:
                continue
            bvid = match.group(1)
            if bvid == "BV号替换" or bvid in seen:
                continue
            seen.add(bvid)
            index += 1
            filename = f"{page_title(page_name)}__video-{index:03d}__{bvid}.jpg"
            yield VideoAsset(
                source=source,
                page=page,
                bvid=bvid,
                name=f"{page_title(page_name)} 视频 {index:03d}",
                thumb=f"assets/video-thumbs/{filename}",
            )


async def capture_video(page, asset: VideoAsset, force: bool) -> bool:
    output_path = ROOT / asset.thumb
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force and is_usable_thumbnail(output_path):
        return True
    if output_path.exists() and not is_usable_thumbnail(output_path):
        output_path.unlink()

    urls = [
        f"https://player.bilibili.com/player.html?isOutside=true&bvid={quote(asset.bvid)}&p=1",
        f"https://www.bilibili.com/video/{quote(asset.bvid)}",
    ]
    try:
        for url in urls:
            try:
                await page.goto(url, wait_until="commit", timeout=8_000)
                await page.wait_for_timeout(500)
                await close_video_overlays(page)
                await page.wait_for_timeout(700)
                if download_cover_fallback(asset, output_path):
                    return True
                if await save_page_cover(page, output_path) and is_usable_thumbnail(output_path):
                    return True
                targets = [
                    page.locator("video").first,
                    page.locator(".bpx-player-container").first,
                    page.locator(".bpx-player-video-wrap").first,
                ]
                captured = False
                for target in targets:
                    try:
                        await target.wait_for(state="visible", timeout=3_000)
                        await target.screenshot(path=str(output_path), type="jpeg", quality=88)
                        captured = True
                        break
                    except PlaywrightTimeoutError:
                        continue
                if not captured:
                    await page.evaluate("""
                        () => document.querySelectorAll('[class*="ctrl"], [class*="control"], [class*="toast"]').forEach((node) => node.style.display = 'none')
                    """)
                    await page.screenshot(path=str(output_path), type="jpeg", quality=88)
                normalize_thumbnail(output_path)
                if output_path.exists() and is_usable_thumbnail(output_path):
                    return True
            except Exception:
                continue
        return download_cover_fallback(asset, output_path)
    except Exception as error:
        print(f"[失败] {asset.bvid}: {error}")
        return download_cover_fallback(asset, output_path)


async def save_page_cover(page, output_path: Path) -> bool:
    """读取已加载视频页的官方封面元数据并保存到本地。"""
    try:
        cover = await page.locator(
            "meta[property='og:image'], meta[itemprop='image'], meta[name='twitter:image']"
        ).first.get_attribute("content")
        if not cover:
            return False
        if cover.startswith("//"):
            cover = "https:" + cover
        request = urllib.request.Request(cover, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            output_path.write_bytes(response.read())
        normalize_thumbnail(output_path)
        return is_usable_thumbnail(output_path)
    except Exception:
        return False


async def close_video_overlays(page) -> None:
    """关闭播放器中的登录、提示和浮动弹窗，避免遮罩进入截图。"""
    selectors = [
        ".bili-mini-mask-close",
        ".bili-mini-login-close",
        ".login-close",
        ".close",
        ".close-btn",
        ".modal-close",
        ".popup-close",
        "[aria-label*='关闭']",
        "[aria-label*='close' i]",
        "[title*='关闭']",
        "[title*='close' i]",
    ]
    for _ in range(3):
        for selector in selectors:
            try:
                locators = page.locator(selector)
                count = min(await locators.count(), 20)
                for index in range(count):
                    button = locators.nth(index)
                    if await button.is_visible():
                        await button.click(timeout=800, force=True)
            except Exception:
                continue

    try:
        await page.evaluate("""
            () => {
                const visible = (element) => {
                    const style = getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return style.display !== 'none' && style.visibility !== 'hidden' &&
                        rect.width > 0 && rect.height > 0;
                };
                const textOf = (element) => (element.innerText || element.textContent || '').trim();
                const closeWords = /^(x|×|关闭|close|取消|cancel)$/i;
                const all = [...document.querySelectorAll('button, a, [role="button"], div, span')];

                for (const element of all) {
                    if (!visible(element)) continue;
                    const label = [element.getAttribute('aria-label'), element.getAttribute('title'), textOf(element)]
                        .filter(Boolean).join(' ').trim();
                    if (closeWords.test(label)) {
                        element.click();
                    }
                }

                for (const element of all) {
                    if (!visible(element)) continue;
                    const text = textOf(element);
                    if (!/登录|高清画质|立即登录/.test(text)) continue;
                    const style = getComputedStyle(element);
                    if (style.position === 'fixed' || style.position === 'absolute' || Number(style.zIndex) > 10) {
                        const close = [...element.querySelectorAll('button, a, span, div')]
                            .find((child) => closeWords.test(textOf(child)));
                        if (close) close.click();
                        else element.style.display = 'none';
                    }
                }
            }
        """)
    except Exception:
        pass

    try:
        candidates = page.locator("button, [role='button'], a")
        for index in range(min(await candidates.count(), 120)):
            candidate = candidates.nth(index)
            if not await candidate.is_visible():
                continue
            label = " ".join(filter(None, [
                await candidate.get_attribute("aria-label"),
                await candidate.get_attribute("title"),
                await candidate.inner_text(),
            ])).strip().lower()
            if label in {"x", "×", "关闭", "close", "取消", "cancel"} or "关闭弹窗" in label:
                await candidate.click(timeout=800, force=True)
    except Exception:
        pass


def normalize_thumbnail(path: Path) -> None:
    """裁掉四周黑边，并将缩略图统一为 16:9，避免比例异常。"""
    try:
        with Image.open(path) as source:
            image = source.convert("RGB")
            gray = image.convert("L")
            width, height = image.size
            pixels = gray.load()

            left, top, right, bottom = 0, 0, width, height
            sample_x = range(0, width, max(1, width // 96))
            sample_y = range(0, height, max(1, height // 96))
            dark_limit = 12
            dark_ratio = 0.88

            while top < bottom - 1 and sum(pixels[x, top] <= dark_limit for x in sample_x) / len(sample_x) >= dark_ratio:
                top += 1
            while bottom > top + 1 and sum(pixels[x, bottom - 1] <= dark_limit for x in sample_x) / len(sample_x) >= dark_ratio:
                bottom -= 1
            while left < right - 1 and sum(pixels[left, y] <= dark_limit for y in sample_y) / len(sample_y) >= dark_ratio:
                left += 1
            while right > left + 1 and sum(pixels[right - 1, y] <= dark_limit for y in sample_y) / len(sample_y) >= dark_ratio:
                right -= 1

            image = image.crop((left, top, right, bottom))
            image.save(path, "JPEG", quality=90, optimize=True)
    except Exception:
        return

def is_usable_thumbnail(path: Path) -> bool:
    """Reject empty, nearly black, or almost uniform screenshots."""
    try:
        with Image.open(path) as image:
            sample = image.convert("L").resize((32, 32))
            statistics = ImageStat.Stat(sample)
            return path.stat().st_size > 2048 and statistics.mean[0] >= 4 and statistics.var[0] >= 1
    except Exception:
        return False


def download_cover_fallback(asset: VideoAsset, output_path: Path) -> bool:
    """使用视频网页公开的真实封面作为截图失败时的本地兜底。"""
    try:
        api_url = "https://api.bilibili.com/x/web-interface/view?bvid=" + quote(asset.bvid)
        request = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        cover = payload["data"]["pic"]
        if cover.startswith("//"):
            cover = "https:" + cover
        image_request = urllib.request.Request(cover, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(image_request, timeout=30) as response:
            output_path.write_bytes(response.read())
        normalize_thumbnail(output_path)
        return is_usable_thumbnail(output_path)
    except Exception as error:
        print(f"[封面失败] {asset.bvid}: {error}")
        return False


async def main(force: bool, only: str | None = None) -> None:
    assets = list(iter_video_assets())
    if only:
        assets = [asset for asset in assets if asset.bvid == only]
    print(f"发现 {len(assets)} 个唯一视频")
    completed: list[VideoAsset] = []
    failed: list[str] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        semaphore = asyncio.Semaphore(6)

        async def process(number: int, asset: VideoAsset) -> VideoAsset | None:
            async with semaphore:
                page = await context.new_page()
                print(f"[{number}/{len(assets)}] {asset.name} ({asset.bvid})")
                try:
                    return asset if await capture_video(page, asset, force) else None
                finally:
                    await page.close()

        results = await asyncio.gather(*[
            process(number, asset) for number, asset in enumerate(assets, 1)
        ])
        completed.extend(asset for asset in results if asset is not None)
        failed.extend(asset.bvid for asset, result in zip(assets, results) if result is None)
        await browser.close()

    manifest = "window.GUIDE_VIDEOS = " + json.dumps(
        [asdict(asset) for asset in completed], ensure_ascii=False, indent=2
    ) + ";\n"
    MANIFEST_PATH.write_text(manifest, encoding="utf-8")
    print(f"完成：{len(completed)}/{len(assets)} 个视频已保存")
    print(f"清单：{MANIFEST_PATH}")
    if failed:
        (ROOT / "video-thumbnail-failures.txt").write_text("\n".join(failed) + "\n", encoding="utf-8")
        print(f"失败清单：{ROOT / 'video-thumbnail-failures.txt'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="重新截图已存在的缩略图")
    parser.add_argument("--only", help="只处理一个 bvid，用于验证截图")
    args = parser.parse_args()
    asyncio.run(main(args.force, args.only))
