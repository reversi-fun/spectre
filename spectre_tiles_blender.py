#!/usr/bin/env python3
import os, sys, math, subprocess
from random import random, uniform, choice
from time import time
try:
	import bpy, mathutils
except:
	bpy=None

_thisdir = os.path.split(os.path.abspath(__file__))[0]
if _thisdir not in sys.path: sys.path.insert(0,_thisdir)

if sys.platform == 'win32':
	BLENDER = 'C:/Program Files/Blender Foundation/Blender 4.2/blender.exe'
	if not os.path.isfile(BLENDER):
		BLENDER = 'C:/Program Files/Blender Foundation/Blender 3.6/blender.exe'
elif sys.platform == 'darwin':
	BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'
else:
	BLENDER = 'blender'
	if os.path.isfile(os.path.expanduser('~/Downloads/blender-4.2.1-linux-x64/blender')):
		BLENDER = os.path.expanduser('~/Downloads/blender-4.2.1-linux-x64/blender')

if bpy:
	import spectre
	bpy.types.Object.tile_index = bpy.props.IntProperty(name='tile index')
	bpy.types.Object.tile_mystic = bpy.props.BoolProperty(name='tile mystic')
	bpy.types.Object.tile_angle = bpy.props.IntProperty(name='tile angle')
	bpy.types.Object.tile_match_error = bpy.props.FloatProperty(name='tile error')

SHAPE_TEST = False
RENDER_TEST = False
DEBUG_NUM = True
USE_PRINT = False
MAKE_SHAPES = True

grease_font = {
	'0' : [[-0.08, 0.81], [0.04, 0.86], [0.19, 0.86], [0.36, 0.75], [0.44, 0.6], [0.45, 0.31], [0.43, -0.68], [0.36, -0.89], [0.19, -1.0], [-0.08, -0.95], [-0.22, -0.78], [-0.31, -0.6], [-0.34, -0.31], [-0.35, 0.36], [-0.31, 0.57], [-0.21, 0.74], [-0.09, 0.8]],
	'1' : [[-0.23, 0.66], [-0.16, 0.74], [-0.11, 0.78], [-0.02, 0.86], [-0.0, -0.87], [0.2, -0.95], [-0.0, -0.94], [-0.24, -0.96]],
	'2' : [[-0.47, 0.36], [-0.16, 0.74], [0.29, 0.61], [0.22, -0.03], [-0.31, -0.2], [-0.39, -0.78], [-0.0, -0.94], [0.38, -0.92]],
	'3' : [[-0.47, 0.36], [-0.16, 0.74], [0.29, 0.61], [0.22, -0.03], [-0.31, -0.2], [0.25, -0.22], [0.23, -0.97], [-0.45, -0.89]],
	'4' : [[0.3, -0.11], [0.28, -0.11], [0.0, -0.14], [-0.6, -0.12], [-0.5, 0.05], [-0.31, 0.27], [-0.16, 0.46], [-0.05, 0.65], [-0.05, 0.34], [-0.05, 0.05], [-0.03, -0.46], [-0.04, -0.96]],
	'5' : [[0.29, 0.68], [0.27, 0.68], [-0.52, 0.66], [-0.43, 0.12], [-0.03, 0.1], [0.27, -0.05], [0.28, -0.6], [-0.03, -0.83], [-0.37, -0.8], [-0.5, -0.7]],
	'6' : [[0.03, 0.73], [0.01, 0.72], [-0.25, 0.53], [-0.44, 0.25], [-0.54, -0.12], [-0.42, -0.42], [-0.22, -0.64], [0.09, -0.77], [0.38, -0.48], [0.39, -0.13], [0.15, 0.08], [-0.19, -0.12], [-0.35, -0.43]],
	'7' : [[-0.52, 0.6], [-0.5, 0.61], [0.05, 0.66], [0.37, 0.63], [0.15, 0.05], [-0.04, -0.67], [-0.12, -0.98]],
	'8' : [[0.34, 0.56], [0.08, 0.73], [-0.22, 0.67], [-0.32, 0.3], [-0.15, 0.09], [0.23, 0.03], [0.57, -0.22], [0.61, -0.68], [0.4, -0.99], [0.01, -1.1], [-0.43, -0.95], [-0.53, -0.52], [-0.41, -0.13], [0.07, 0.06], [0.33, 0.15], [0.39, 0.4], [0.29, 0.61]],
	'9' : [[0.35, 0.33], [0.33, 0.32], [0.0, 0.08], [-0.36, 0.34], [-0.19, 0.7], [0.36, 0.82], [0.46, 0.41], [0.34, -0.02], [0.21, -0.46], [0.17, -1.07]],
	'★'  : [[-0.15, 0.09], [-0.13, 0.09], [0.03, 0.51], [0.04, 0.56], [0.22, 0.04], [0.64, 0.01], [0.35, -0.27], [0.51, -0.63], [0.23, -0.54], [-0.08, -0.4], [-0.39, -0.62], [-0.35, -0.48], [-0.3, -0.12], [-0.68, 0.12], [-0.17, 0.1]],
}

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
ITER = 0
def build_tiles( a=10, b=10, iterations=3, curve=False, lattice=False ):
	global TRACE, num_tiles, ITER
	ITER = iterations
	num_tiles = 0
	TRACE = []

	if USE_PRINT:
		cam = bpy.data.objects['Camera']
		cam.data.type='ORTHO'
		cam.data.ortho_scale = 50
		cam.rotation_euler = [math.pi/2, 0,0]
		cam.location = [8, -1, -15]
		cam.location.x = CAM_COORDS[0][0]
		cam.location.z = CAM_COORDS[0][1]
	world = bpy.data.worlds[0]
	world.use_nodes = False
	world.color=[1,1,1]

	scn = bpy.data.scenes[0]
	scn.render.engine = "BLENDER_WORKBENCH"

	start = time()
	spectreTiles = spectre.buildSpectreTiles(iterations,a,b)
	time1 = time()-start

	print(f"supertiling loop took {round(time1, 4)} seconds")

	bpy.ops.object.gpencil_add(type="EMPTY")
	g = bpy.context.object
	#glayer = g.data.layers.new("notes", set_active=True)
	#gframe = glayer.frames.new(1)
	g.data.layers[0].info = 'notes'

	start = time()
	spectreTiles["Delta"].forEachTile( lambda a,b: plotVertices(a,b,scale=0.1, gpencil=g))
	time2 = time()-start
	print(f"tile recursion loop took {round(time2, 4)} seconds, generated {num_tiles} tiles")

	if curve:
		points = []
		for info in TRACE:
			o = info[0]
			points.append(o.location)
		cu = create_linear_curve(points)
		mod = cu.modifiers.new(name='smooth', type="SMOOTH")
		mod.iterations = 10

	if lattice:
		bpy.ops.object.add(type="LATTICE")
		lattice = bpy.context.active_object

		mod = lattice.modifiers.new(type='SIMPLE_DEFORM', name='bend')
		mod.deform_method='BEND'
		mod.deform_axis = 'Z'
		mod.angle = 0
		#mod.angle = math.radians(645)
		#mod.angle = math.radians(544)
		#mod.angle = math.radians(746)
		mod.angle = math.radians(790)

		lattice.data.points_u = 8
		lattice.data.points_v = 2
		lattice.data.points_w = 1
		lattice.scale *= 20
		lattice.location = [-46.39, 0, 30]

		for info in TRACE:
			o = info[0]
			mod = o.modifiers.new(type="LATTICE", name='cylinder')
			mod.object=lattice

		bpy.ops.object.add(type="LATTICE")
		lattice = bpy.context.active_object
		lattice.data.points_u = 8
		lattice.data.points_v = 8
		lattice.data.points_w = 8
		lattice.scale *= 20
		lattice.location = [-46.39, 1.48, 30]

		mod = lattice.modifiers.new(type='CAST', name='cast')
		mod.cast_type = "SPHERE"
		mod.factor = 2.7
		mod.use_z = False
		for info in TRACE:
			o = info[0]
			mod = o.modifiers.new(type="LATTICE", name='sphere')
			mod.object=lattice
			if o.tile_mystic:
				mod = o.modifiers.new(name='solid', type='SOLIDIFY')
				mod.thickness = -2
				mod.use_rim_only = True



	if RENDER_TEST:
		scn.render.film_transparent=True
		scn.render.resolution_x = 1920
		scn.render.resolution_y = 1260
		scn.render.resolution_percentage = 200
		for i,v in enumerate(CAM_COORDS):
			cam.location.x = v[0]
			cam.location.z = v[1]
			scn.render.filepath='/tmp/tiles.%s.png' % i
			bpy.ops.render.render(write_still=True)

	if MAKE_SHAPES:
		build_shapes()

def build_shapes():
	pairs = {}
	tiles = []
	for a in bpy.data.objects:
		if a in tiles: continue
		if not a.tile_index: continue
		hits = []
		for b in bpy.data.objects:
			if b.tile_index == a.tile_index: continue
			if b.tile_angle != a.tile_angle: continue
			if round(b.location.z,0) != round(a.location.z,0):
				continue
			b.tile_match_error = a.location.z - b.location.z
			hits.append(b)
		if hits:
			pairs[a] = hits
			tiles.append(a)
			tiles += hits

	shapes = {}

	for a in pairs:
		print(a.name, pairs[a])

		#width = (b.location - a.location).length
		b = pairs[a][-1]
		width = abs(a.location.x - b.location.x)
		print('WIDTH:', width)
		width = round(width,4)
		if width not in shapes:
			shapes[width] = {'color':[random(), random(), random(), 1], 'pairs':[]}

		shape = shapes[width]
		shape['pairs'].append([a]+pairs[a])

		points = [a.location]
		x,y,z = a.location
		if a.tile_mystic:
			points.append([x,y-3,z])
		else:
			points.append([x,y+3,z])
		rad = 0.1
		for b in pairs[a]:
			print('error:', b.tile_match_error)
			diff = b.location-a.location
			mid = a.location + (diff*0.5)
			if b.tile_mystic:
				mid.y -= diff.length * 0.5
			else:
				mid.y += diff.length * 0.5
			points.append(mid)
			x,y,z = b.location
			if b.tile_mystic:
				points.append([x,y-3,z])
			else:
				points.append([x,y+3,z])
			points.append(b.location)
			rad = diff.length
		create_bezier_curve(points, radius=rad*0.1)

	for width in shapes:
		shape = shapes[width]
		print(width, shape)
		for pair in shape['pairs']:
			for tile in pair:
				tile.color = shape['color']


CAM_COORDS = [
	[-50, 35],
	[-44, 18],
	[-44, 2],
	[-70, -7],
	[-40, -7],
	[7, -7],
	[7, -25],
	[-25, -25],
	[-50, -25],
	[-50, -45],
	[-25, -45],
	[0, -45],
	#[25, -45],
	#[50, -45],

	#[50, -60],
	#[25, -60],
	#[0, -60],
	#[-25, -60],
	#[-50, -60],

]

def create_bezier_curve(points, radius=1.0):
	curve_data = bpy.data.curves.new(name="BezCurve", type='CURVE')
	curve_data.dimensions = '3D'
	curve_data.bevel_resolution = 1
	spline = curve_data.splines.new('BEZIER')
	spline.bezier_points.add( len(points) - 1)
	for i, point in enumerate(points):
		x,y,z = point
		spline.bezier_points[i].co.x = x
		spline.bezier_points[i].co.y = y
		spline.bezier_points[i].co.z = z
		spline.bezier_points[i].handle_left_type = 'AUTO' # ‘FREE’, ‘VECTOR’, ‘ALIGNED’, ‘AUTO’
		spline.bezier_points[i].handle_right_type = 'AUTO' # ‘FREE’, ‘VECTOR’, ‘ALIGNED’, ‘AUTO’
	curve_obj = bpy.data.objects.new("BezCurveObject", curve_data)
	bpy.context.collection.objects.link(curve_obj)
	#curve_obj.data.extrude = 0.1
	#curve_obj.data.bevel_depth=0.3
	return curve_obj


def create_linear_curve(points, radius=0.5, start_rad=1, end_rad=1):
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
		polyline.points[i].radius = radius

	#polyline.points[0].tilt = math.radians(90)
	#polyline.points[1].tilt = math.radians(180)
	#polyline.points[1].radius = 0
	polyline.points[0].radius = start_rad
	polyline.points[-1].radius = end_rad

	curve_obj = bpy.data.objects.new("LinearCurveObject", curve_data)
	bpy.context.collection.objects.link(curve_obj)
	curve_obj.data.extrude = 0.1
	curve_obj.data.bevel_depth=0.3
	return curve_obj



num_tiles = 0
def plotVertices(tile_transformation, label, scale=1.0, gizmos=True, center=True, gpencil=None, use_mesh=True):
	"""
	T: transformation matrix
	label: label of shape type
	"""
	#print(tile_transformation)
	global num_tiles
	num_tiles += 1
	vertices = (spectre.SPECTRE_POINTS if label != "Gamma2" else spectre.Mystic_SPECTRE_POINTS).dot(tile_transformation[:,:2].T) + tile_transformation[:,2]
	color_array = spectre.get_color_array(tile_transformation, label)
	rot,scl = spectre.trot_inv(tile_transformation)


	#use_mesh = not gpencil
	if gpencil:
		verts = []
		for v in vertices:
			x,y = v
			verts.append([x,0,y])

		show_num = USE_PRINT
		line_width = 100
		if SHAPE_TEST:
			use_mesh = True
			shape = SHAPES[5][0]
			if num_tiles not in shape['tiles']:
				line_width = 60
				use_mesh = False
				if DEBUG_NUM:
					show_num = True
				else:
					return
		if label not in gpencil.data.layers:
			layer = gpencil.data.layers.new(label)
			frame = layer.frames.new(1)
		frame = gpencil.data.layers[label].frames[0]
		stroke = frame.strokes.new()
		stroke.points.add(count=len(verts))
		stroke.line_width = line_width
		stroke.use_cyclic = True
		ax = ay = az = 0.0
		for i,v in enumerate(verts):
			x,y,z = v
			stroke.points[i].co.x = x * scale
			stroke.points[i].co.y = y * scale
			stroke.points[i].co.z = z * scale
			ax += x
			az += z
		ax /= len(verts)
		az /= len(verts)

		#X = tile_transformation[0][-1]
		#Y = tile_transformation[1][-1]
		if show_num:
			frame = gpencil.data.layers['notes'].frames[0]
			X = 0
			info = str(num_tiles)
			if scl==1:  ## this is when iterations is odd
				info = '★' + info
			for char in info:
				assert char in grease_font
				arr = grease_font[char]
				stroke = frame.strokes.new()
				stroke.points.add(count=len(arr))
				stroke.line_width = 30
				for i,v in enumerate(arr):
					x,y = v
					stroke.points[i].co.x = (x+ax+X) * scale
					stroke.points[i].co.z = (y+az) * scale
				X += 1.0

	if use_mesh:
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
		oname='%s(%s|%s)' % (label, rot,scl)
		obj = bpy.data.objects.new(oname, mesh)
		bpy.context.collection.objects.link(obj)
		obj.tile_index = num_tiles
		obj.tile_angle = rot


		if (ITER % 2 and scl == 1) or (not ITER % 2 and scl == -1):
			#if scl == 1:
			obj.tile_mystic=True
			#obj.color = [0,0,0,1]
		else:
			#obj.color = list(color_array) + [1]
			pass

		tag = ','.join([str(v) for v in color_array])
		mat = smaterial(tag, color_array)
		obj.data.materials.append(mat)

		#print(rot, scl)
		#obj.rotation_euler.y = math.radians(rot)
		x = tile_transformation[0][-1]
		y = tile_transformation[1][-1]
		#obj.location.x = x * scale
		#obj.location.z = y * scale
		if center:
			bpy.context.view_layer.objects.active = obj
			obj.select_set(True)
			bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
		if gizmos:
			bpy.ops.object.empty_add(type="ARROWS")
			ob = bpy.context.active_object
			ob.parent = obj
			ob.rotation_euler.y = math.radians(rot)
			ob.scale.y = scl
		else:

			ob = None
		#if scl == -1:
		#	mod = obj.modifiers.new(name='solid', type='SOLIDIFY')
		#	mod.thickness = rot * 0.01

		#if scl == 1:
		if obj.tile_mystic:
			mod = obj.modifiers.new(name='solid', type='SOLIDIFY')
			mod.thickness = -1
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

SHAPES = {
	5 : [
		{'tiles':[
			1211,1212,1213,1214,1215,1216,
			1199,1200,1201,1202,1203,1204,1205,1206,1207,
			1377,1391,1392,1368,1375,1395,1396,1397,1398, 1347,1399,1400,1401,1402,
			1449,1450,1451,1452,1453,1454,1455,1456,

			1190,1191,1192,1193,1194,1195,1196,1197,1198,
			1388,1387,1386,1393,1394,1390,1391,1392,
			1232,1255,1256,1257,1258,1259,1260,
			1253,1254,1636,1458,1459,1460,1461,1462,

			1369,1370,1371,

			1389, 1448,

		]},
	],
}

def mkshapes(shapes=5):
	rem = []
	i = 0
	for ob in bpy.data.objects:
		ok = False
		for shape in SHAPES[shapes]:
			if i in shape['tiles']:
				ok = True
				break
		if not ok:
			rem.append(ob)

	for ob in rem:
		bpy.data.objects.remove( ob )

if __name__ == '__main__':
	args = []
	kwargs = {}
	blend = None
	for arg in sys.argv:
		if arg.startswith('--') and '=' in arg:
			args.append(arg)
			k,v = arg.split('=')
			k = k[2:]
			if k=='iterations' or k == 'shapes':
				kwargs[k]=int(v)
			else:
				kwargs[k]=float(v)
		elif arg.endswith('.blend'):
			blend = arg
		elif arg=='--print':
			USE_PRINT = True
			args.append(arg)
		elif arg=='--shape-test':
			SHAPE_TEST = True
			args.append(arg)

	if not bpy:
		cmd = [BLENDER]
		if blend: cmd.append(blend)
		cmd += ['--python', __file__]
		if args:
			cmd += ['--'] + args
		print(cmd)
		subprocess.check_call(cmd)

		## TODO
		#if 'iterations' in kwargs and kwargs['iterations']==5:
		#	tmp = '/tmp/spectre.%s.blend' % kwargs['iterations']
		#	cmd = ['blender', tmp, '--python', __file__, '--', '--shapes=5']

		sys.exit()

	if 'Cube' in bpy.data.objects:
		bpy.data.objects.remove( bpy.data.objects['Cube'] )

	print('kwargs:', kwargs)
	if '--print' in sys.argv:
		RENDER_TEST = True
		build_tiles(a=5, b=5, iterations=5)
	elif 'shapes' in kwargs:
		mkshapes(**kwargs)
	elif 'iterations' in kwargs:
		tmp = '/tmp/spectre.%s.blend' % kwargs['iterations']
		#if not os.path.isfile(tmp):
		build_tiles(**kwargs)
		bpy.ops.wm.save_as_mainfile(filepath=tmp, check_existing=False)

	else:
		build_tiles(**kwargs)
