default:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace

layers:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace

trace:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace

order:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --order-expand=1 --trace

odd:
	python3 spectre_tiles_blender.py --iterations=1,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace
even:
	python3 spectre_tiles_blender.py --iterations=2,4 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace


level1:
	python3 spectre_tiles_blender.py --iterations=1 --gpencil --gpen-fills=0 --num-mystic --rotation=30 --plot
level1_90:
	python3 spectre_tiles_blender.py --iterations=1 --gpencil --gpen-fills=0 --num-mystic --rotation=90 --plot

level2:
	python3 spectre_tiles_blender.py --iterations=2 --gpencil --gpen-fills=0 --num-mystic --rotation=30 --plot

level3:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=30 --plot

level3_0:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=0 --plot

level3_31:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=31 --plot

level3_90:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=90 --plot

level3_270:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=270 --plot

level4:
	python3 spectre_tiles_blender.py --iterations=4 --gpencil --gpen-fills=1 --num-mystic --rotation=30 --plot --minimal
level5:
	python3 spectre_tiles_blender.py --iterations=5 --gpencil --gpen-fills=1 --num-mystic --rotation=30 --plot --minimal
