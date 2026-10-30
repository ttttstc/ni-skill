#!/bin/sh
# Fetch Xiaolai (小赖字体, OFL-1.1, by LXGW, based on Seto Font) - the CJK handwriting font Excalidraw itself uses -
# into assets/fonts/. It is 22 MB, so it is not committed; build_page subsets it to the characters of each config.
# Excalifont (Latin, OFL-1.1) is already in assets/fonts/.
set -e
cd "$(dirname "$0")/../assets/fonts"
[ -f Xiaolai-Regular.ttf ] || curl -fL -o Xiaolai-Regular.ttf https://github.com/lxgw/kose-font/releases/download/v3.126/Xiaolai-Regular.ttf
echo "ok: $(pwd)/Xiaolai-Regular.ttf"
