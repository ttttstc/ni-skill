#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

# Only remove byte-identical files from the previous bundled font package.
LEGACY_FONTS = {
    "BabelStoneHan.ttf": ("d8bb747b3fdccd84a60bd0aa56bb90937270d0bd15f1101cd8f2a5a3709dd0a3", "BabelStoneHan-LICENSE.txt", "bce2b6aca2727c45b73adfd13992acba7d3e61e9ea15c05d7bb5ccc4ed36ff87"),
    "EarlySummerSerif-VF.ttf": ("63de2404b7e46204a2a89ca00e1462ea48c2d2b0d261486a34b9615f134fae80", "EarlySummerSerif-OFL.txt", "8a5942ebacff93b00d842331d11b75f133b1c474f8bba1fc1323e4d55c2bc625"),
    "I.Ming-8.10.ttf": ("cba13b75b050d671b611d0063147262e421e14359ad4530948b070f56111f0f3", "I.Ming-LICENSE.md", "e905e64dbad6c2c6299bbb35708b874da623e9568ed38f25d07703e69f176b25"),
    "LXGWWenKai-Regular.ttf": ("2d73eea94ad808999d90c0000c239a84a33b09d4bc6ab6c5b8bbf1eda8a7fc8b", "LXGW-WenKai-OFL.txt", "d43c47335b621550a73fc1d20dcf61dfa6d905c0679fb3fcc000a35c4595d5ca"),
    "SourceHanSerifSC-VF.ttf": ("04f163fb935acd9c0caa79e535a43d510a724d25e584d36212e494a9f9db64f4", "SourceHanSerif-OFL.txt", "c606a29cd5c76629d6b02a0ad8fa636beeb4320a1f0ceba616c476ee83775aa3"),
}


def remove_stock_legacy_fonts(destination):
    font_dir = destination / "assets" / "fonts"
    if font_dir.resolve() != destination.resolve() / "assets" / "fonts":
        print(f"旧字体目录包含链接，保留旧字体：{font_dir}")
        return
    for name, (digest, license_name, license_digest) in LEGACY_FONTS.items():
        font = font_dir / name
        if font.is_symlink() or (font.exists() and not font.is_file()):
            print(f"保留非普通文件：{font}")
            continue
        if not font.is_file():
            continue
        if hashlib.sha256(font.read_bytes()).hexdigest() != digest:
            print(f"保留已修改的旧字体：{font}")
            continue
        font.unlink()
        license_file = font_dir / license_name
        if not license_file.is_symlink() and license_file.is_file() and hashlib.sha256(license_file.read_bytes()).hexdigest() == license_digest:
            license_file.unlink()


def main():
    parser = argparse.ArgumentParser(description="安装 Poetry Book Skill")
    parser.add_argument("--dest", default=str(Path.home() / ".agents" / "skills" / "ni-poetry-book"))
    args = parser.parse_args()
    destination = Path(args.dest).expanduser().absolute()
    if destination.is_symlink():
        raise SystemExit(f"拒绝安装到符号链接：{destination}")
    if destination.resolve() == ROOT:
        print(f"Poetry Book 已位于目标目录：{destination}")
        return
    if destination.exists():
        skill_file = destination / "SKILL.md"
        if not destination.is_dir() or not skill_file.is_file() or "name: ni-poetry-book" not in skill_file.read_text(encoding="utf-8"):
            raise SystemExit(f"目标已存在且不是 Poetry Book 技能，停止覆盖：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", "*.pyc"))
    remove_stock_legacy_fonts(destination)
    print(f"Poetry Book 已安装：{destination}")


if __name__ == "__main__":
    main()
