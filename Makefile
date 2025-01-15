default:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30

level1:
	python3 spectre_tiles_blender.py --iterations=1 --gpencil --gpen-fills=0 --num-mystic --rotation=30

level2:
	python3 spectre_tiles_blender.py --iterations=2 --gpencil --gpen-fills=0 --num-mystic --rotation=30

level3:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=30 --plot

level3_90:
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 --num-mystic --rotation=90 --plot
