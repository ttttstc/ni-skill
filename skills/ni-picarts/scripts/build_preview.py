"""Package registered relief textures and the bundled renderer into a new directory."""

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import numpy as np
from PIL import Image


SKILL = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--normal", required=True, type=Path)
    parser.add_argument("--mask", required=True, type=Path)
    parser.add_argument("--mask-channel", choices=["gray", "alpha"], default="gray")
    parser.add_argument("--resize-normal", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--background", default="#DDDCD7")
    parser.add_argument("--brush", type=float, default=0.20)
    parser.add_argument("--title", default="金属浮雕样片")
    args = parser.parse_args()

    if not re.fullmatch(r"#[0-9a-fA-F]{6}", args.background):
        parser.error("--background must be a six-digit RGB hex color")
    if not 0.01 <= args.brush <= 1:
        parser.error("--brush must be between 0.01 and 1")
    output = args.output.resolve()
    if output.exists():
        parser.error("Output already exists; choose a new version directory")

    with Image.open(args.base) as image:
        size = image.size
    with Image.open(args.normal) as image:
        source_size = image.size
        rgb = np.asarray(image.convert("RGB")).copy()
    with Image.open(args.mask) as image:
        if image.size != size:
            parser.error("Mask dimensions must match the base; do not stretch silhouettes")
        if args.mask_channel == "alpha":
            if "A" not in image.getbands():
                parser.error("Alpha mask requested but input has no alpha channel")
            matte = np.asarray(image.getchannel("A")).copy()
        else:
            matte = np.asarray(image.convert("L")).copy()
    if not np.any(matte == 0) or not np.any(matte > 220):
        parser.error("Mask must contain both zero-coverage background and opaque foreground")

    resized = source_size != size
    if resized:
        if not args.resize_normal:
            parser.error("Normal dimensions must match the base; verify registration before --resize-normal")
        if abs((source_size[0] / source_size[1]) / (size[0] / size[1]) - 1) > 0.015:
            parser.error("Normal aspect ratio differs by more than 1.5%; regenerate it")
        vectors = rgb.astype(np.float32) / 127.5 - 1
        vectors = np.stack([
            np.asarray(Image.fromarray(vectors[:, :, channel]).resize(size, Image.Resampling.BILINEAR))
            for channel in range(3)
        ], axis=-1)
        vectors /= np.maximum(np.linalg.norm(vectors, axis=-1, keepdims=True), 1e-8)
        rgb = np.rint((vectors * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
    rgb[matte == 0] = [128, 128, 255]
    clip = np.full((*matte.shape, 4), 255, dtype=np.uint8)
    clip[:, :, 3] = matte

    runtime = SKILL / "assets/runtime"
    runtime_lock = json.loads((SKILL / "assets/runtime-lock.json").read_text(encoding="utf-8"))
    for name, expected in runtime_lock["sha256"].items():
        if digest(runtime / name) != expected:
            parser.error(f"Bundled runtime hash mismatch: {name}")

    output.mkdir(parents=True)
    materials = output / "materials"
    materials.mkdir()
    sources = output / "sources"
    sources.mkdir()
    base_name = "base" + args.base.suffix.lower()
    shutil.copyfile(args.base, materials / base_name)
    shutil.copyfile(args.normal, sources / ("normal-original" + args.normal.suffix.lower()))
    shutil.copyfile(args.mask, sources / ("mask-original" + args.mask.suffix.lower()))
    Image.fromarray(rgb).save(materials / "normal.png")
    Image.fromarray(matte).save(materials / "mask.png")
    Image.fromarray(clip).save(materials / "clip.png")
    shutil.copytree(runtime, output / "runtime")
    shutil.copyfile(SKILL / "assets/runtime-lock.json", output / "runtime-lock.json")
    for source in (SKILL / "assets/template").iterdir():
        if source.name == "index.html":
            text = source.read_text(encoding="utf-8").replace("__TITLE__", html.escape(args.title))
            (output / source.name).write_text(text, encoding="utf-8")
        else:
            shutil.copyfile(source, output / source.name)
    manifest = {
        "base": f"materials/{base_name}",
        "normal": "materials/normal.png",
        "mask": "materials/mask.png",
        "clip": "materials/clip.png",
        "width": size[0], "height": size[1],
        "background": args.background.upper(),
        "brush": args.brush,
        "normalResized": resized,
        "sourceDimensions": list(source_size),
        "sourceSha256": {"base": digest(args.base), "normal": digest(args.normal), "mask": digest(args.mask)},
        "materialSha256": {path.name: digest(path) for path in materials.iterdir()},
        "visualReview": "not-assessed",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "dimensions": list(size), "normalResized": resized,
                      "baseBytesPreserved": digest(materials / base_name) == digest(args.base),
                      "visualReview": "not-assessed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
