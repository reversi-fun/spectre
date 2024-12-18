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
	import spectre
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

TRACE = []
def build_tiles():
	global TRACE
	TRACE = []
	start = time()
	spectreTiles = buildSpectreTiles(N_ITERATIONS,Edge_a,Edge_b)
	time1 = time()-start

	print(f"supertiling loop took {round(time1, 4)} seconds")

	start = time()
	spectreTiles["Delta"].forEachTile( lambda a,b: plotVertices(a,b,scale=0.1))
	time2 = time()-start
	print(f"tile recursion loop took {round(time2, 4)} seconds, generated {num_tiles} tiles")

	points = []
	for info in TRACE:
		o = info[0]
		points.append(o.location)
	cu = create_linear_curve(points)
	mod = cu.modifiers.new(name='smooth', type="SMOOTH")
	mod.iterations = 10

def create_linear_curve(points):
	curve_data = bpy.data.curves.new(name="LinearCurve", type='CURVE')
	curve_data.dimensions = '3D'
	polyline = curve_data.splines.new('POLY')
	polyline.points.add(len(points) - 1)
	for i, point in enumerate(points):
		x,y,z = point
		polyline.points[i].co.x = x
		polyline.points[i].co.y = y
		polyline.points[i].co.z = z
		#polyline.points[i].tilt = i*30

	#polyline.points[0].tilt = math.radians(90)
	#polyline.points[1].tilt = math.radians(180)
	polyline.points[1].radius = 0
	polyline.points[0].radius = 10
	polyline.points[-1].radius = 10

	curve_obj = bpy.data.objects.new("LinearCurveObject", curve_data)
	bpy.context.collection.objects.link(curve_obj)
	curve_obj.data.extrude = 0.1
	curve_obj.data.bevel_depth=0.3
	return curve_obj



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

	if 1:
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
	#if 'SPECTRE' not in bpy.data.meshes:
	#mesh = mktiles(SPECTRE_POINTS, scale=scale)
	#mesh = bpy.data.meshes['SPECTRE']
	obj = bpy.data.objects.new('TILE:'+label, mesh)
	bpy.context.collection.objects.link(obj)

	tag = ','.join([str(v) for v in color_array])
	mat = smaterial(tag, color_array)
	obj.data.materials.append(mat)

	rot,scl = spectre.trot_inv(tile_transformation)
	print(rot, scl)
	#obj.rotation_euler.y = math.radians(rot)
	x = tile_transformation[0][-1]
	y = tile_transformation[1][-1]
	#obj.location.x = x * scale
	#obj.location.z = y * scale
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
	bpy.ops.object.empty_add(type="ARROWS")
	ob = bpy.context.active_object
	ob.parent = obj
	ob.rotation_euler.y = math.radians(rot)
	ob.scale.y = scl
	#if scl == -1:
	#	mod = obj.modifiers.new(name='solid', type='SOLIDIFY')
	#	mod.thickness = rot * 0.01
	if scl == 1:
		mod = obj.modifiers.new(name='solid', type='SOLIDIFY')
		mod.thickness = -100
		mod.use_rim_only = True

	TRACE.append([obj, ob, rot, scl, tile_transformation])

def mktiles(vertices, scale=1.0):
	verts = []
	for v in vertices:
		x,y = v
		verts.append([x*scale,0,y*scale])

	faces = [
		list(range(len(verts)))
	]

	mesh = bpy.data.meshes.new('SPECTRE')
	mesh.from_pydata(verts, [], faces)

	return mesh



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
