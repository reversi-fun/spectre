# draw Polygons Svg by blender #####
import os, sys, math, subprocess
from random import random, uniform, choice
from time import time
try:
	import bpy, mathutils
except:
	bpy=None

_thisdir = os.path.split(os.path.abspath(__file__))[0]
if _thisdir not in sys.path: sys.path.insert(0,_thisdir)

if bpy:
	from spectre import buildSpectreTiles,get_color_array, SPECTRE_POINTS, Mystic_SPECTRE_POINTS, Edge_a,Edge_b, N_ITERATIONS, print_trot_inv_prof

def smaterial(name, color):
	if name not in bpy.data.materials:
		m = bpy.data.materials.new(name=name)
		m.use_nodes = False
		if len(color)==3:
			r,g,b = color
			m.diffuse_color = [r,g,b,1]
		else:
			m.diffuse_color = color
	return bpy.data.materials[name]

def build_tiles():
	start = time()
	spectreTiles = buildSpectreTiles(N_ITERATIONS,Edge_a,Edge_b)
	time1 = time()-start

	print(f"supertiling loop took {round(time1, 4)} seconds")

	start = time()
	spectreTiles["Delta"].forEachTile( lambda a,b: plotVertices(a,b,scale=0.1))
	time2 = time()-start
	print(f"tile recursion loop took {round(time2, 4)} seconds, generated {num_tiles} tiles")


num_tiles = 0
def plotVertices(tile_transformation, label, scale=1.0):
	"""
	T: transformation matrix
	label: label of shape type
	"""
	print(tile_transformation)
	global num_tiles
	num_tiles += 1
	vertices = (SPECTRE_POINTS if label != "Gamma2" else Mystic_SPECTRE_POINTS).dot(tile_transformation[:,:2].T) + tile_transformation[:,2]
	color_array = get_color_array(tile_transformation, label)

	verts = []
	for v in vertices:
		x,y = v
		verts.append([x*scale,0,y*scale])

	faces = [
		list(range(len(verts)))
	]

	mesh = bpy.data.meshes.new(label)
	mesh.from_pydata(verts, [], faces)
	# Create object
	obj = bpy.data.objects.new('TILE:'+label, mesh)
	bpy.context.collection.objects.link(obj)

	tag = ','.join([str(v) for v in color_array])
	mat = smaterial(tag, color_array)
	obj.data.materials.append(mat)


def mk_prims():
	verts = []
	for v in SPECTRE_POINTS:
		x,y = v
		verts.append([x,0,y])

	faces = [
		list(range(len(verts)))
	]

	mesh = bpy.data.meshes.new("SPECTRE")
	mesh.from_pydata(verts, [], faces)
	# Create object
	obj = bpy.data.objects.new("SPECTRE", mesh)
	bpy.context.collection.objects.link(obj)



if __name__ == '__main__':
	args = []
	kwargs = {}
	blend = None
	for arg in sys.argv:
		if arg.startswith('--') and '=' in arg:
			args.append(arg)
			k,v = arg.split('=')
			k = k[2:]
			kwargs[k]=float(v)
		elif arg.endswith('.blend'):
			blend = arg
	if not bpy:
		cmd = ['blender']
		if blend: cmd.append(blend)
		cmd += ['--python', __file__]
		if args:
			cmd += ['--'] + args
		print(cmd)
		subprocess.check_call(cmd)
		sys.exit()

	if 'Cube' in bpy.data.objects:
		bpy.data.objects.remove( bpy.data.objects['Cube'] )


	print(SPECTRE_POINTS)
	print(Mystic_SPECTRE_POINTS)
	build_tiles(**kwargs)
