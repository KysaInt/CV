from pathlib import Path
from PIL import Image, ImageStat

root = Path('.')
files = sorted((root / 'assets' / 'video-thumbs').glob('*.jpg'))
bad = []
ratios = []
for path in files:
    with Image.open(path) as image:
        sample = image.convert('L').resize((32, 32))
        stats = ImageStat.Stat(sample)
        ratios.append(round(image.width / image.height, 3))
        if stats.mean[0] < 4 or stats.var[0] < 1:
            bad.append((path.name, round(stats.mean[0], 2), round(stats.var[0], 2)))
manifest = (root / 'guide-videos.js').read_text(encoding='utf-8')
print('JPG_COUNT=', len(files))
print('MANIFEST_COUNT=', manifest.count('bvid'))
print('BAD_COUNT=', len(bad))
print('BAD=', bad[:10])
print('RATIO_MIN_MAX=', min(ratios), max(ratios))
print('MIN_BYTES=', min(path.stat().st_size for path in files))
