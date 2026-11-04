import os, sys, math
os.chdir(r'C:\Users\jun99\OneDrive - 계명대학교\바탕 화면\Analysis\toy_agent_project\advertisement_apple')
sys.path.insert(0, '.venv-report')
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio.v2 as imageio

W, H, FPS = 1080, 1920, 30
BOLD = r'C:\Windows\Fonts\malgunbd.ttf'
REG = r'C:\Windows\Fonts\malgun.ttf'
pouch = Image.open('result/juice_original_product_2026-10-28.webp').convert('RGB')          # 750x1000
label = Image.open('result/juice_pouch_label_roll_2026-11-04.jpg').convert('RGB')          # 1080x1475

def cover(img, w, h):
    iw, ih = img.size; s = max(w / iw, h / ih)
    im = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
    x = (im.size[0] - w) // 2; y = (im.size[1] - h) // 2
    return im.crop((x, y, x + w, y + h))

def kenburns(img, t, z0, z1, cx0, cy0, cx1, cy1):
    """t in [0,1]; zoom z (1=cover), center (cx,cy) in 0..1 of image."""
    z = z0 + (z1 - z0) * t; cx = cx0 + (cx1 - cx0) * t; cy = cy0 + (cy1 - cy0) * t
    iw, ih = img.size; s = max(W / iw, H / ih) * z
    sw, sh = int(iw * s) + 1, int(ih * s) + 1
    im = img.resize((sw, sh), Image.BILINEAR)
    x = int(cx * sw - W / 2); y = int(cy * sh - H / 2)
    x = max(0, min(sw - W, x)); y = max(0, min(sh - H, y))
    return im.crop((x, y, x + W, y + H))

def caption(frame, text, sub=None, alpha=1.0):
    im = frame.copy(); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(BOLD, 84); fs = ImageFont.truetype(REG, 44)
    y = int(H * 0.72)
    # soft dark band
    band = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.rectangle((0, 0, W, 420), fill=(0, 0, 0, int(110 * alpha)))
    band = band.filter(ImageFilter.GaussianBlur(40))
    im.paste(band, (0, y - 120), band)
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=f); x = (W - tw) / 2
    for dx in (-4, 4):
        for dy in (-4, 4):
            d.text((x + dx, y + dy), text, font=f, fill=(0, 0, 0, int(255 * alpha)))
    d.text((x, y), text, font=f, fill=(255, 255, 255, int(255 * alpha)))
    if sub:
        sw = d.textlength(sub, font=fs); d.text(((W - sw) / 2, y + 120), sub, font=fs, fill=(255, 240, 220))
    return im

def endcard(t):
    im = Image.new('RGB', (W, H), (250, 246, 240)); d = ImageDraw.Draw(im)
    ph = cover(pouch, 760, 760); im.paste(ph, ((W - 760) // 2, 300))
    f1 = ImageFont.truetype(BOLD, 110); f2 = ImageFont.truetype(BOLD, 64); f3 = ImageFont.truetype(REG, 46)
    for txt, fnt, yy, col in [('청송사과즙', f1, 1150, (29, 29, 31)), ('120ml × 50포', f2, 1300, (60, 60, 60)),
                               ('29,900원 · 무료배송', f2, 1400, (178, 58, 42)), ('삼형제농원 · 경북 청송군', f3, 1520, (90, 90, 90))]:
        tw = d.textlength(txt, font=fnt); d.text(((W - tw) / 2, yy), txt, font=fnt, fill=col)
    return im

def scene_img(idx, fallback):
    """Use a generated/real lifestyle still if result/juice_scene_0N_*.png|jpg exists, else fallback."""
    import glob
    hits = sorted(glob.glob(f'result/juice_scene_{idx:02d}_*.png') + glob.glob(f'result/juice_scene_{idx:02d}_*.jpg'))
    if hits:
        print('scene', idx, '->', hits[0]); return Image.open(hits[0]).convert('RGB')
    return fallback

S1, S2, S3, S4 = scene_img(1, pouch), scene_img(2, label), scene_img(3, pouch), scene_img(4, pouch)
scenes = [
    # (duration s, image, zoom0, zoom1, c0, c1, caption, sub)
    (3.5, S1, 1.00, 1.18, (0.5, 0.45), (0.52, 0.40), '출근 가방에 쏙', '납작한 파우치, 한 포씩'),
    (4.0, S2, 1.15, 1.30, (0.42, 0.45), (0.46, 0.52), '청송사과즙 120ml 한 포', '사과 100% · 첨가물 없음 (라벨 표기)'),
    (3.5, S3, 1.25, 1.10, (0.55, 0.60), (0.45, 0.55), '개봉해 바로, 또는 컵에 따라', '하루 한 포, 간식으로'),
    (3.0, S4, 1.05, 1.22, (0.5, 0.5), (0.5, 0.35), '50포 한 박스 · 삼형제농원', '낮 12시 전 주문 당일 발송'),
]
frames = []
XF = int(0.4 * FPS)
for i, (dur, img, z0, z1, c0, c1, cap, sub) in enumerate(scenes):
    n = int(dur * FPS)
    for k in range(n):
        t = k / max(n - 1, 1)
        fr = kenburns(img, t, z0, z1, c0[0], c0[1], c1[0], c1[1])
        a = min(1.0, k / (0.5 * FPS), (n - 1 - k) / XF if i < len(scenes) - 1 else 1.0)  # caption fade-in/out
        fr = caption(fr, cap, sub, a)
        if i > 0 and k < XF:  # crossfade from previous last frame
            prev = frames[-1 - (XF - 1 - k)] if False else last
            w = k / XF
            fr = Image.blend(prev, fr, w)
        frames.append(fr)
    last = frames[-1]
nE = int(1.5 * FPS); ec = endcard(0)
for k in range(nE):
    w = min(1.0, k / XF); frames.append(Image.blend(last, ec, w))

out = 'result/juice_video_15s_9x16_2026-11-04.mp4'
wr = imageio.get_writer(out, fps=FPS, codec='libx264', quality=8, pixelformat='yuv420p', macro_block_size=None)
for fr in frames: wr.append_data(np.asarray(fr))
wr.close()
# 1:1 version: center crop 1080x1080
out2 = 'result/juice_video_15s_1x1_2026-11-04.mp4'
wr = imageio.get_writer(out2, fps=FPS, codec='libx264', quality=8, pixelformat='yuv420p', macro_block_size=None)
for fr in frames: wr.append_data(np.asarray(fr.crop((0, 420, W, 420 + 1080))))
wr.close()
# contact sheet for review
sheet = Image.new('RGB', (6 * 270, 480), 'white')
for i, t in enumerate([0, 3.6, 7.6, 11.2, 13.5, 14.9]):
    f = frames[min(len(frames) - 1, int(t * FPS))].resize((270, 480)); sheet.paste(f, (i * 270, 0))
sheet.save('result/juice_video_15s_contact_2026-11-04.png')
print('frames', len(frames), 'sec', len(frames) / FPS, out, os.path.getsize(out) // 1024, 'KB')
