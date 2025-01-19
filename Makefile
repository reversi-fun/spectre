default:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace

layers:
	python3 spectre_tiles_blender.py --iterations=1,2,3 --plot --plot-labels --gpencil --num-mystic --rotation=30 --layer-expand=30 --trace

layers4:
	python3 spectre_tiles_blender.py --iterations=1,2,3,4 --plot --plot-labels --gpencil --minimal --num-mystic --rotation=30 --layer-expand=30 --trace

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

new_shape:
	python3 spectre_tiles_blender.py --iterations=3 --make-shapes

echo_shape0:
	echo '{"left":[72],"right":[257],"left_bor":[269,73,79,80,86,270,268],"right_bor":[278,251,258,256,279,250],"joins":[]}' > /tmp/tmp.json

load_shape: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --color-fade=0

load_shape: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --color-fade=0

load_shape_smooth_1: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=0.1 --trace-shape-smooth-iter=5 --color-fade=0
load_shape_smooth_2: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=0.2 --trace-shape-smooth-iter=5 --color-fade=0
load_shape_smooth_4: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=0.4 --trace-shape-smooth-iter=5 --color-fade=0
load_shape_smooth_6: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=0.6 --trace-shape-smooth-iter=5 --color-fade=0
load_shape_smooth_8: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=0.8 --trace-shape-smooth-iter=5 --color-fade=0
load_shape_smooth_10: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=1 --trace-shape-smooth-iter=5 --color-fade=0

load_shape_sharp: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=0 --trace-shape-smooth-iter=0 --color-fade=0

load_shape_smooth: echo_shape0
	python3 spectre_tiles_blender.py --iterations=3 --gpencil --gpen-fills=0 /tmp/tmp.json --trace-shape --trace-shape-smooth=1 --trace-shape-smooth-iter=10 --color-fade=0
