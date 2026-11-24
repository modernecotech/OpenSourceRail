"""Render the staged CAD films with NumPy, Pillow and FFmpeg."""

import argparse
from functools import lru_cache
from hashlib import file_digest
import importlib
import json
from math import cos, radians, sin
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
WIDTH, HEIGHT = 1280, 720
FPS = 20
LIMIT_BYTES = 20_000_000
FILMS = ("viaduct", "train")
INK = "#eaf4fa"
SECONDARY = "#a9c2d2"
ACCENT = "#63e1cc"
LIGHT = np.array((0.35, -0.45, 0.82))


@lru_cache(maxsize=None)
def font(size, bold=False):
    return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


@lru_cache(maxsize=None)
def rgb(color):
    return np.asarray(ImageColor.getrgb(color), dtype=float)


def make_backdrop():
    background = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(background)
    for y in range(HEIGHT):
        gradient = max(0, 1 - abs(y - 338) / 380)
        draw.line(((0, y), (WIDTH, y)),
                  fill=(int(11 + gradient * 6), int(23 + gradient * 10), int(36 + gradient * 13)))
    for x in range(27, WIDTH, 26):
        for y in range(159, 600, 26):
            draw.point((x, y), fill="#274155")
    return background


BACKDROP = make_backdrop()
STAGE_TOP, STAGE_HEIGHT = 149, 454
SUPERSAMPLE = 2
STAGE_BACKDROP = BACKDROP.crop((0, STAGE_TOP, WIDTH, STAGE_TOP + STAGE_HEIGHT)).resize(
    (WIDTH * SUPERSAMPLE, STAGE_HEIGHT * SUPERSAMPLE), Image.Resampling.BICUBIC)


def camera_basis(camera):
    azimuth, height = map(radians, (camera.yaw, camera.elevation))
    view = np.array((cos(azimuth) * cos(height), sin(azimuth) * cos(height), sin(height)))
    horizontal = np.array((-sin(azimuth), cos(azimuth), 0))
    vertical = np.cross(view, horizontal)
    return np.column_stack((horizontal, -vertical, view))


def world_vertices(item):
    points = item.mesh.vertices
    if item.scale != (1, 1, 1) or item.yaw:
        points = (points - item.pivot) * item.scale
        if item.yaw:
            angle = radians(item.yaw)
            rotation = np.array(((cos(angle), sin(angle), 0), (-sin(angle), cos(angle), 0), (0, 0, 1)))
            points = points @ rotation
        points = points + item.pivot
    return points + item.offset


def draw_scene(image, shot):
    # Orthographic projection maintains readable relative sizes throughout each shot.
    # Keep the scene on its own canvas so close views cannot overwrite the titles.
    stage = STAGE_BACKDROP.copy()
    draw = ImageDraw.Draw(stage)
    basis = camera_basis(shot.camera)
    zoom = (WIDTH - 100) / shot.camera.width
    faces = []
    for item in shot.items:
        points = world_vertices(item)
        projected = (points - shot.camera.target) @ basis
        xy = np.rint((projected[:, :2] * zoom + (WIDTH / 2, STAGE_HEIGHT / 2)) * SUPERSAMPLE).astype(int)
        for indices in item.mesh.face_groups:
            facet = points[indices]
            normal = np.cross(facet[:, 1] - facet[:, 0], facet[:, 2] - facet[:, 0])
            lengths = np.linalg.norm(normal, axis=1)
            dot = np.divide(normal @ LIGHT, lengths, out=np.zeros_like(lengths), where=lengths > 0)
            colors = np.clip(rgb(item.color) * (0.70 + 0.34 * np.abs(dot[:, None])), 0, 255).astype(int)
            depth = projected[:, 2][indices].mean(axis=1)
            for z, polygon, color in zip(depth, xy[indices], colors, strict=True):
                faces.append((item.layer, z, polygon, tuple(color), item.outline))
    for _, _, polygon, color, outline in sorted(faces, key=lambda face: face[:2]):
        strokes = tuple(max(0, int(channel * .69)) for channel in color) if outline else None
        draw.polygon([tuple(point) for point in polygon], fill=color, outline=strokes, width=SUPERSAMPLE)
    image.paste(stage.resize((WIDTH, STAGE_HEIGHT), Image.Resampling.BOX), (0, STAGE_TOP))


def lines_that_fit(draw, copy, used_font, available):
    lines, current = [], ""
    for word in copy.split():
        line = f"{current} {word}".strip()
        if current and draw.textlength(line, font=used_font) > available:
            lines.append(current)
            current = word
        else:
            current = line
    return [*lines, current]


def raster(module, seconds):
    shot = module.frame(seconds)
    image = BACKDROP.copy()
    draw_scene(image, shot)
    draw = ImageDraw.Draw(image)
    draw.text((55, 27), "OPENSOURCERAIL", font=font(15, True), fill=ACCENT)
    draw.text((224, 27), module.TITLE, font=font(15), fill=SECONDARY)
    draw.text((55, 53), shot.title, font=font(38, True), fill=INK)
    for index, line in enumerate(lines_that_fit(draw, shot.caption, font(18), WIDTH - 110)):
        draw.text((57, 106 + index * 22), line, font=font(18), fill=SECONDARY)

    # Timed chapter bar and tags identify what is visible in the CAD view.
    start = 55
    for tag in shot.tags:
        end = start + round(draw.textlength(tag, font=font(14))) + 30
        draw.rounded_rectangle((start, 607, end, 636), radius=6, fill="#172f42", outline="#315267")
        draw.text((start + 14, 613), tag, font=font(14), fill=INK)
        start = end + 8
    draw.text((WIDTH - 57, 612), "CAD sequence • illustrative", anchor="ra", fill=SECONDARY, font=font(14))
    left, right = 57, WIDTH - 57
    draw.line((left, 661, right, 661), fill="#315267", width=3)
    mark = lambda time: round(left + (right - left) * time / module.DURATION)
    draw.line((left, 661, mark(seconds), 661), fill=ACCENT, width=3)
    for time, _ in module.CHAPTERS:
        x = mark(time)
        draw.ellipse((x - 4, 657, x + 4, 665), fill=ACCENT if time <= seconds else "#69889a")
    chapter = next(label for time, label in reversed(module.CHAPTERS) if time <= seconds)
    draw.text((left, 675), chapter, fill=SECONDARY, font=font(14))
    draw.text((right, 675), timecode(seconds) + " / " + timecode(module.DURATION),
              anchor="ra", fill=SECONDARY, font=font(14))
    return image


def timecode(seconds):
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes}:{remainder:02d}"


def valid_chapters(module):
    times = [time for time, _ in module.CHAPTERS]
    if not times or times[0] != 0 or times != sorted(set(times)) or times[-1] >= module.DURATION:
        raise ValueError(f"Invalid chapter times for {module.TITLE}")


def encode(module, target):
    partial = target.with_suffix(".tmp.mp4")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-threads", "4", "-preset", "fast", "-crf", "22",
        "-maxrate", "1500k", "-bufsize", "3000k", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(partial),
    ]
    try:
        with subprocess.Popen(cmd, stdin=subprocess.PIPE) as ffmpeg:
            for index in range(round(module.DURATION * FPS)):
                ffmpeg.stdin.write(raster(module, index / FPS).tobytes())
            ffmpeg.stdin.close()
            if ffmpeg.wait():
                raise RuntimeError(f"Encoding failed for {target.name}")
        if partial.stat().st_size >= LIMIT_BYTES:
            raise ValueError(f"Video must be below {LIMIT_BYTES} bytes")
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)


def sha(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/assembly-animations")
    parser.add_argument("--clip", choices=FILMS)
    parser.add_argument("--still", type=float, action="append", help="Render selected frames only")
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True, parents=True)
    videos = {}
    for name in (args.clip,) if args.clip else FILMS:
        module = importlib.import_module(name)
        valid_chapters(module)
        if args.still:
            for seconds in args.still:
                if not 0 <= seconds < module.DURATION:
                    parser.error(f"{name} frame is outside the video")
                raster(module, seconds).save(args.output / f"{name}-{seconds:g}.png")
            continue
        video = args.output / f"{name}.mp4"
        poster = args.output / f"{name}.webp"
        encode(module, video)
        raster(module, module.POSTER_TIME).save(poster, quality=86)
        sources = (*module.SOURCES, *(
            str(Path(__file__).with_name(file).relative_to(ROOT))
            for file in ("scene.py", "render.py", f"{name}.py")))
        videos[name] = dict(
            seconds=module.DURATION, chapters=[{"time_s": time, "label": label}
                                               for time, label in module.CHAPTERS],
            source_sha256={path: sha(ROOT / path) for path in sources},
            mp4_sha256=sha(video), poster_sha256=sha(poster), bytes=video.stat().st_size,
            width_px=WIDTH, height_px=HEIGHT, fps=FPS,
        )
    if videos:
        suffix = f"-{args.clip}" if args.clip else ""
        (args.output / f"receipt{suffix}.json").write_text(json.dumps(videos, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
