# excalidraw-gardener

园丁 loop（作者自己的每日复盘 loop，https://github.com/ythx-101/gardener-loop ）用 `excalidraw` view 画成会动的手绘图，中文，4:5 和 3:4 两版。
数字都来自园丁 README：B 段最佳候选规则 30 题从 10% 到 57%，没过 75% 线，一条没提；C 段「审美」攒到 5 次后作者提前批准固化。
门槛 2 次 / 6 次借自胡海岚团队 Science 2017。动效是示意。需要先跑 `sh scripts/fetch_fonts.sh` 下载小赖字体。

    python3 examples/excalidraw-gardener/build_config.py
    python3 scripts/render.py --config examples/excalidraw-gardener/config-4x5.json --out gardener-4x5.mp4
