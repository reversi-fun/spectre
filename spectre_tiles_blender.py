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
	if os.path.isfile(os.path.expanduser('~/Downloads/blender-3.0.0-linux-x64/blender')):
		BLENDER = os.path.expanduser('~/Downloads/blender-3.0.0-linux-x64/blender')
	elif os.path.isfile(os.path.expanduser('~/Downloads/blender-3.6.1-linux-x64/blender')):
		BLENDER = os.path.expanduser('~/Downloads/blender-3.6.1-linux-x64/blender')
	elif os.path.isfile(os.path.expanduser('~/Downloads/blender-4.2.1-linux-x64/blender')):
		BLENDER = os.path.expanduser('~/Downloads/blender-4.2.1-linux-x64/blender')

if bpy:
	import spectre
	bpy.types.World.tile_active_collection = bpy.props.PointerProperty(name="active shape", type=bpy.types.Collection)
	bpy.types.World.tile_export_path = bpy.props.StringProperty(name="export path")
	bpy.types.World.tile_import_path = bpy.props.StringProperty(name="import path")
	bpy.types.World.tile_generate_steps = bpy.props.IntProperty(name="generate steps", default=2)
	bpy.types.World.tile_generate_gizmos = bpy.props.BoolProperty(name="generate gizmos")
	bpy.types.Object.tile_index = bpy.props.IntProperty(name='tile index')
	bpy.types.Object.tile_x = bpy.props.FloatProperty(name='tile x')
	bpy.types.Object.tile_y = bpy.props.FloatProperty(name='tile y')
	bpy.types.Object.tile_shape_join = bpy.props.BoolProperty(name="join")
	bpy.types.Object.tile_shape_left = bpy.props.BoolProperty(name="left")
	bpy.types.Object.tile_shape_right = bpy.props.BoolProperty(name="right")
	bpy.types.Object.tile_collection = bpy.props.PointerProperty(name="shape", type=bpy.types.Collection)
	bpy.types.Object.tile_mystic = bpy.props.BoolProperty(name='tile mystic')
	bpy.types.Object.tile_angle = bpy.props.IntProperty(name='tile angle')
	bpy.types.Object.tile_match_error = bpy.props.FloatProperty(name='tile error')
	bpy.types.Object.tile_pair = bpy.props.PointerProperty(name="pair", type=bpy.types.Object)
	bpy.types.Object.tile_shape_border_left = bpy.props.BoolProperty(name="border left")
	bpy.types.Object.tile_shape_border_right = bpy.props.BoolProperty(name="border right")
	bpy.types.Object.tile_shape_index = bpy.props.IntProperty(name='shape index')

AUTO_SHAPES = False
SHAPE_TEST = False
RENDER_TEST = False
DEBUG_NUM = True
USE_PRINT = False
MAKE_SHAPES = True
USE_GPEN = False

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
	if type(name) is list:
		r,g,b = name
		name = '%s|%s|%s' % (round(r,3),round(g,3),round(b,3))
	print(name,color)
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
def build_tiles( a=10, b=10, iterations=3, curve=False, lattice=False, gizmos=False ):
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

	if USE_GPEN:
		bpy.ops.object.gpencil_add(type="EMPTY")
		g = bpy.context.object
		#glayer = g.data.layers.new("notes", set_active=True)
		#gframe = glayer.frames.new(1)
		g.data.layers[0].info = 'notes'
	else:
		g = None

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
		build_shapes(iterations=iterations, gizmos=gizmos)

def build_shapes(iterations=3, sharp_nurb_shapes=False, gizmos=False):
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
			if not a.tile_pair:
				a.tile_pair = b
			hits.append(b)
		if hits:
			pairs[a] = hits
			tiles.append(a)
			tiles += hits

	shapes = {}
	curves = []
	curves_by_height = {}
	curves_by_x = {}
	for a in pairs:
		print(a.name, pairs[a])

		#width = (b.location - a.location).length
		b = pairs[a][-1]
		width = abs(a.location.x - b.location.x)
		#print('WIDTH:', width)
		width = round(width,4)
		if width not in shapes:
			shapes[width] = {'color':[uniform(0.7,0.9), uniform(0.7,0.9), uniform(0.7,0.9), 1], 'pairs':[], 'curves':[]}

		shape = shapes[width]
		shape['pairs'].append([a]+pairs[a])
		if AUTO_SHAPES:
			if a.location.x < b.location.x:
				a.tile_shape_left = True
				b.tile_shape_right = True
			else:
				a.tile_shape_right = True
				b.tile_shape_left = True

		if gizmos:
			cu,points = pairs_to_curve( shape['pairs'][-1], iterations=iterations )
			shape['curves'].append(cu)
			if len(points)==5:
				curves.append(cu)

			z = a.location.z
			if z not in curves_by_height:
				curves_by_height[z] = []
			curves_by_height[z].append(cu)

			x = a.location.x
			if x not in curves_by_x:
				curves_by_x[x] = []
			curves_by_x[x].append(cu)

	if curves:
		nurb = create_nurbs( curves )
		nurb.scale.y = -1

	for sidx, width in enumerate(shapes):
		shape = shapes[width]
		for cu in shape['curves']:
			cu.color=shape['color']
		if sharp_nurb_shapes:
			nurb = create_nurbs(
				shape['curves'], 
				sharp=True, 
				material=shape['pairs'][0][0].data.materials[0],
				color=shape['color'],
			)

		#print(width, shape)
		tag = 'shape(%s)' % sidx
		if tag not in bpy.data.collections:
			col = bpy.data.collections.new(tag)
			if not bpy.data.worlds[0].tile_active_collection:
				bpy.data.worlds[0].tile_active_collection = col
		for pair in shape['pairs']:
			for tile in pair:
				tile.color = shape['color']
				tile.tile_shape_index = sidx + 1
				if AUTO_SHAPES:
					tile.tile_collection = bpy.data.collections[tag]

	if False:
		xs = list(curves_by_x.keys())
		xs.sort()
		prev_x = None
		xsurfs = []
		for x in xs:
			for cu in curves_by_x[x]:
				if prev_x is None or abs(x - prev_x) > 2:
					surf = []
					xsurfs.append(surf)
					prev_x=x
				surf.append(cu)
			prev_x = x

		for surf in xsurfs:
			if len(surf) < 3: continue
			nurb = create_nurbs(surf)
			if nurb:
				nurb.scale.y = -1

	if gizmos:
		zs = list(curves_by_height.keys())
		zs.sort()
		print('heights:', zs)
		prev_z = None
		surfs = []
		for z in zs:
			for cu in curves_by_height[z]:
				if prev_z is None or abs(z - prev_z) > 5:
					surf = []
					surfs.append(surf)
					prev_z=z
				surf.append(cu)
			prev_z = z

		prev_surf = None
		next_surf = None
		for sidx, surf in enumerate(surfs):
			print('nurbs surface:', surf)
			if sidx+1 < len(surfs):
				next_surf = surfs[sidx+1]

			mat = surf[0].data.materials[0]

			if prev_surf and next_surf:
				curves = [prev_surf[-1]]+surf+[next_surf[0]]
			elif prev_surf:
				curves = [prev_surf[-1]]+surf
			elif next_surf:
				curves = surf+[next_surf[0]]
			else:
				curves = surf
			nurb = create_nurbs(curves, material=mat)

			prev_surf = surf

	#for sidx, width in enumerate(shapes):
	#	shape = shapes[width]
	#	for pair in shape['pairs']:
	#		for tile in pair:
	#			near = []
	#			for b in bpy.data.objects:
	#				if not b.tile_index: continue
	#				if tile.tile_index==b.tile_index: continue
	#				if b.tile_shape_index: continue

def pairs_to_curve(pairs, iterations=2):
	a = pairs[0]
	x,y,z = a.location

	points = [ [x,y,z, math.radians(a.tile_angle)]]

	if a.tile_mystic:
		points.append([x,y-3,z,math.radians(a.tile_angle)])
	else:
		points.append([x,y+3,z,math.radians(a.tile_angle)])
	rad = 0.1
	for b in pairs[1:]:
		#print('error:', b.tile_match_error)
		diff = b.location-a.location
		mid = a.location + (diff*0.5)
		if b.tile_mystic:
			mid.y -= diff.length * 0.5
		else:
			mid.y += diff.length * 0.5
		points.append(mid)
		x,y,z = b.location
		if b.tile_mystic:
			points.append([x,y-3,z, math.radians(-b.tile_angle)])
		else:
			points.append([x,y+3,z, math.radians(-b.tile_angle)])
		#points.append(b.location)
		points.append([x,y,z, math.radians(-b.tile_angle)])
		rad = diff.length
	if iterations==1:
		extrude=1
	elif iterations==2:
		extrude=0.4
	elif iterations==3:
		extrude=0.1
	else:
		extrude=0.02
	cu = create_bezier_curve(points, radius=rad*0.1, extrude=extrude, depth=0.01, material=a.data.materials[0])
	return cu, points

def create_nurbs( curves, sharp=False, material=None, color=None ):
	nurbs_surface = bpy.data.curves.new("NURBS Surface", type='SURFACE') 
	nurbs_surface.dimensions = '3D' 
	nurbs_surface.resolution_u = 3
	nurbs_surface.resolution_v = 3
	nurbs_obj = bpy.data.objects.new("NURBS", nurbs_surface) 
	bpy.context.scene.collection.objects.link(nurbs_obj)
	N = 5 #N = len(curves[1].data.splines[0].bezier_points)
	C = 0
	steps = 1
	if sharp:
		curves = [curves[0]] + curves + [curves[-1]]
		steps = 2
	for cu in curves:
		if len(cu.data.splines[0].bezier_points) != N:
			#raise RuntimeError('invalid curve: %s' % cu)
			continue
		for j in range(steps):
			C += 1
			spline = nurbs_surface.splines.new('NURBS')
			spline.points.add( N-1 )  # -1 because of default point
			for i in range(N):
				x,y,z = cu.data.splines[0].bezier_points[i].co
				spline.points[i].co = mathutils.Vector((x,y,z, 1))
				spline.points[i].select=True
	print('nurbs: %s x %s' % (C, N))
	if not C:
		return None
	bpy.context.view_layer.objects.active = nurbs_obj
	bpy.ops.object.mode_set(mode='EDIT') 
	bpy.ops.curve.make_segment()
	bpy.ops.object.mode_set(mode='OBJECT') 
	nurbs_obj.show_wire=True
	if material:
		nurbs_obj.data.materials.append(material)
	if color:
		r,g,b,a = color
		nurbs_obj.color = [r,g,b,0.8]
	nurbs_obj.select_set(False)
	return nurbs_obj


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

def create_bezier_curve(points, radius=1.0, extrude=0.08, depth=0.02, material=None):
	curve_data = bpy.data.curves.new(name="BezCurve", type='CURVE')
	curve_data.dimensions = '3D'
	curve_data.bevel_resolution = 1
	curve_data.resolution_u = 8
	spline = curve_data.splines.new('BEZIER')
	spline.bezier_points.add( len(points) - 1)
	for i, point in enumerate(points):
		if len(point)==3:
			x,y,z = point
		else:
			x,y,z,tilt = point
			spline.bezier_points[i].tilt = tilt

		spline.bezier_points[i].co.x = x
		spline.bezier_points[i].co.y = y
		spline.bezier_points[i].co.z = z
		spline.bezier_points[i].handle_left_type = 'AUTO' # ‘FREE’, ‘VECTOR’, ‘ALIGNED’, ‘AUTO’
		spline.bezier_points[i].handle_right_type = 'AUTO' # ‘FREE’, ‘VECTOR’, ‘ALIGNED’, ‘AUTO’
	curve_obj = bpy.data.objects.new("BezCurveObject", curve_data)
	bpy.context.collection.objects.link(curve_obj)
	curve_obj.data.extrude = extrude
	curve_obj.data.bevel_depth=depth
	if material:
		curve_obj.data.materials.append(material)
		curve_obj.show_wire = True
	return curve_obj


def create_linear_curve(points, radius=None, start_rad=None, end_rad=None, closed=False):
	curve_data = bpy.data.curves.new(name="LinearCurve", type='CURVE')
	curve_data.dimensions = '3D'
	polyline = curve_data.splines.new('POLY')
	polyline.points.add(len(points) - 1)
	if closed:
		polyline.use_cyclic_u=True
	for i, point in enumerate(points):
		if len(point)==3:
			x,y,z = point
		else:
			x,y,z,w = point
		polyline.points[i].co.x = x
		polyline.points[i].co.y = y
		polyline.points[i].co.z = z
		#polyline.points[i].tilt = i*30
		if radius:
			polyline.points[i].radius = radius

	#polyline.points[0].tilt = math.radians(90)
	#polyline.points[1].tilt = math.radians(180)
	#polyline.points[1].radius = 0
	if start_rad:
		polyline.points[0].radius = start_rad
	if end_rad:
		polyline.points[-1].radius = end_rad

	curve_obj = bpy.data.objects.new("LinearCurveObject", curve_data)
	bpy.context.collection.objects.link(curve_obj)
	curve_obj.data.extrude = 0.1
	curve_obj.data.bevel_depth=0.3
	return curve_obj



num_tiles = 0
def plotVertices(tile_transformation, label, scale=1.0, gizmos=False, center=True, gpencil=None, use_mesh=True):
	"""
	T: transformation matrix
	label: label of shape type
	"""
	print(tile_transformation)
	global num_tiles
	num_tiles += 1
	vertices = (spectre.SPECTRE_POINTS if label != "Gamma2" else spectre.Mystic_SPECTRE_POINTS).dot(tile_transformation[:,:2].T) + tile_transformation[:,2]
	color_array = spectre.get_color_array(tile_transformation, label)
	color_array *= 0.5
	color_array += 0.5
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
		obj.tile_x = tile_transformation[0][-1]
		obj.tile_y = tile_transformation[1][-1]


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

def import_json( jfile, scale=0.1, show_num=False, gpencil_cyclic=False, grow_patches=False ):
	import json
	dump = json.loads(open(jfile).read())
	print(dump)
	if len(dump['tiles']):
		bpy.ops.object.gpencil_add(type="EMPTY")
		gpencil = bpy.context.active_object
		gpencil.data.layers[0].info = 'notes'
		mod = gpencil.grease_pencil_modifiers.new(name='subdiv', type="GP_SUBDIV")
		mod.level = 2
		mod = gpencil.grease_pencil_modifiers.new(name='subdiv', type="GP_SMOOTH")
		mod.factor=1.0

	for o in dump['tiles']:
		trans = spectre.trot( o['angle'] )
		trans[0][-1] = o['x']
		trans[1][-1] = o['y']
		if 'mystic' in o:
			vertices = (spectre.Mystic_SPECTRE_POINTS).dot(trans[:,:2].T) + trans[:,2]
		else:
			vertices = (spectre.SPECTRE_POINTS).dot(trans[:,:2].T) + trans[:,2]

		verts = []
		for v in vertices:
			x,y = v
			verts.append([x,0,y])

		line_width = 100
		label = o['name'].split('(')[0]
		if label not in gpencil.data.layers:
			layer = gpencil.data.layers.new(label)
			frame = layer.frames.new(1)
		frame = gpencil.data.layers[label].frames[0]
		stroke = frame.strokes.new()
		stroke.points.add(count=len(verts))
		stroke.line_width = line_width
		stroke.use_cyclic = gpencil_cyclic
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
		if show_num:
			frame = gpencil.data.layers['notes'].frames[0]
			X = 0
			info = str(o['index'])
			if 'mystic' in o:  ## this is when iterations is odd
				info = '★' + info
			for char in info:
				assert char in grease_font
				arr = grease_font[char]
				stroke = frame.strokes.new()
				stroke.points.add(count=len(arr))
				stroke.line_width = 30
				for i,v in enumerate(arr):
					x,y = v
					x*=2
					y*=2
					stroke.points[i].co.x = (x+ax+X) * scale
					stroke.points[i].co.z = (y+az) * scale
				X += 2.0


	for shape_name in dump['shapes']:
		print('SHAPE:', shape_name)
		tiles = {}
		bpy.ops.object.empty_add(type="SINGLE_ARROW")
		root = bpy.context.active_object
		root.name='SHAPE:%s' % shape_name

		for o in dump['shapes'][shape_name]:
			print('	TILE:', o['name'])
			trans = spectre.trot( o['angle'] )
			trans[0][-1] = o['x']
			trans[1][-1] = o['y']
			if 'mystic' in o:
				vertices = (spectre.Mystic_SPECTRE_POINTS).dot(trans[:,:2].T) + trans[:,2]
			else:
				vertices = (spectre.SPECTRE_POINTS).dot(trans[:,:2].T) + trans[:,2]

			verts = []
			for v in vertices:
				x,y = v
				verts.append([x*scale,0,y*scale])

			faces = [
				list(range(len(verts)))
			]

			mesh = bpy.data.meshes.new(o['name'])
			mesh.from_pydata(verts, [], faces)
			mesh.materials.append(smaterial(o['color'], o['color']))
			obj = bpy.data.objects.new(o['name'], mesh)
			bpy.context.collection.objects.link(obj)
			tiles[ obj ] = o
			obj.show_wire=True
			obj.tile_index = o['index']
			obj.tile_angle = o['angle']
			obj.tile_x = o['x']
			obj.tile_y = o['y']
			if 'border' in o:
				if o['border']=='left':
					obj.tile_shape_border_left=True
				elif o['border']=='right':
					obj.tile_shape_border_right=True
			if 'mystic' in o:
				obj.tile_mystic=True
			if 'type' in o:
				if o['type']=='left':
					obj.tile_shape_left=True
				elif o['type']=='right':
					obj.tile_shape_right=True
			if 'join' in o:
				obj.tile_shape_join=True

			bpy.context.view_layer.objects.active = obj
			obj.select_set(True)
			bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")

			bpy.ops.object.empty_add(type="ARROWS")
			ob = bpy.context.active_object
			ob.parent = obj
			ob.rotation_euler.y = math.radians(o['angle'])

			obj.parent=root

		curves = []
		left = []
		left_bor = []
		right = []
		right_bor = []
		for tile in tiles:
			if tile.tile_shape_border_left:
				left_bor.append(tile)
			elif tile.tile_shape_border_right:
				right_bor.append(tile)

			if 'pair' in tiles[tile]:
				pname = tiles[tile]['pair']
				if pname in bpy.data.objects:
					b = bpy.data.objects[pname]
					tile.tile_pair = b
					cu,points = pairs_to_curve( [tile, tile.tile_pair] )
					cu.parent = root
					curves.append(cu)
					if tile.tile_shape_left:
						left.append( tile )
					elif tile.tile_shape_right:
						right.append( tile )
					if b.tile_shape_left:
						left.append( b )
					elif b.tile_shape_right:
						right.append( b )
				else:
					print("WARN: missing tile pair:", pname)

		if len(curves) >= 2:
			mat = tile.data.materials[0]
			nurb = create_nurbs([curves[0]]+curves+[curves[-1]], material=mat)
			nurb.parent=root

		if grow_patches:
			if len(left):
				trace_tiles(left, dump['tiles'])
			if len(right):
				trace_tiles(right, dump['tiles'])

		if len(left_bor) > 1:
			cu = trace_tiles(left_bor+left)
			#cu.data.offset = -0.1
			if cu.type=='CURVE':
				cu.data.extrude = 0.5
				cu.location.y = 0.1
		if len(right_bor) > 1:
			cu = trace_tiles(right_bor+right)
			#cu.data.offset = -0.1
			cu.data.extrude = 0.5
			cu.location.y = 0.1

def create_mesh_tile(o, scale=0.1):
	trans = spectre.trot( o['angle'] )
	trans[0][-1] = o['x']
	trans[1][-1] = o['y']
	if 'mystic' in o:
		vertices = (spectre.Mystic_SPECTRE_POINTS).dot(trans[:,:2].T) + trans[:,2]
	else:
		vertices = (spectre.SPECTRE_POINTS).dot(trans[:,:2].T) + trans[:,2]

	verts = []
	for v in vertices:
		x,y = v
		verts.append([x*scale,0,y*scale])

	faces = [
		list(range(len(verts)))
	]

	mesh = bpy.data.meshes.new(o['name'])
	mesh.from_pydata(verts, [], faces)
	mesh.materials.append(smaterial(o['color'], o['color']))
	obj = bpy.data.objects.new(o['name'], mesh)
	bpy.context.collection.objects.link(obj)
	return obj

def trace_tiles( tiles, space_tiles=None ):
	print('trace_tiles:', tiles)
	bpy.ops.object.select_all(action='DESELECT')
	tmp = []
	ax = ay = 0.0
	for tile in tiles:
		ax += tile.tile_x
		ay += tile.tile_y
		copy = tile.copy()
		copy.data= tile.data.copy()
		tmp.append( copy )
		bpy.context.scene.collection.objects.link(copy)
	tiles = tmp
	bpy.context.view_layer.objects.active = tiles[0]

	if space_tiles:
		ax /= len(tiles)
		ay /= len(tiles)
		print('shape center: %s : %s' %(ax,ay))
		for o in space_tiles:
			dx = abs(o['x']-ax)
			dy = abs(o['y']-ay)
			d = (dx+dy)/2
			#print('delta: %s : %s : %s' % (dx,dy, d))
			if d < 28:
				tmp = create_mesh_tile(o)
				tiles.append(tmp)

	for ob in tiles:
		ob.select_set(True)

	bpy.ops.object.join()
	ob = bpy.context.active_object
	ob.select_set(True)
	bpy.context.view_layer.objects.active = ob
	if 1:
		mod = ob.modifiers.new(name='merge', type="WELD")
		bpy.ops.object.modifier_apply(modifier=mod.name)

		#mod = ob.modifiers.new(name='clean', type="DECIMATE")
		#mod.ratio = 0.98
		#bpy.ops.object.modifier_apply(modifier=mod.name)

		#mod = ob.modifiers.new(name='smooth', type="LAPLACIANSMOOTH")
		#mod.lambda_border=1

		#mod = ob.modifiers.new(name='smooth', type="SMOOTH")
		#mod.factor=1

	trace_inner_edges(ob)

	ob.location.y = -1# + random()
	return ob

	bpy.ops.object.convert(target="CURVE")
	return ob

def trace_inner_edges( ob ):
	e = extract_inner_edges_and_faces(ob.data)
	e.select_set(True)
	e.parent = ob
	bpy.context.view_layer.objects.active = e
	bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
	#mod = e.modifiers.new(name='smooth', type="LAPLACIANSMOOTH")
	#mod.lambda_border=1
	#bpy.ops.object.modifier_apply(modifier=mod.name)

	mod = e.modifiers.new(name='smooth', type="SMOOTH")
	mod.factor=1
	return

	bpy.ops.object.convert(target="CURVE")
	cu = bpy.context.active_object
	for spline in cu.data.splines:
		if spline.use_cyclic_v:
			print('cyclic v')
		if spline.use_cyclic_u:
			print('cyclic u')
			#cu['curve_length'] = spline.calc_length()
			points = [v.co for v in spline.points]
			c = create_linear_curve(points, closed=True)
			c.parent = cu
			break

def extract_inner_edges_and_faces(mesh):
	import bmesh
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bm.verts.ensure_lookup_table()
	bm.edges.ensure_lookup_table()
	vertices = []
	edges = []
	faces = []
	vertex_map = {}
	# Find inner edges and create vertex/edge lists
	for edge in bm.edges:
		if len(edge.link_faces) == 2: 
			v1 = edge.verts[0]
			v2 = edge.verts[1]
			if v1.index not in vertex_map:
				vertex_map[v1.index] = len(vertices)
				vertices.append(v1.co.copy())
			if v2.index not in vertex_map:
				vertex_map[v2.index] = len(vertices)
				vertices.append(v2.co.copy())
			v1_index = vertex_map[v1.index]
			v2_index = vertex_map[v2.index]
			edges.append((v1_index, v2_index))
	# Find and store faces that contain only inner edges
	for face in bm.faces:
		all_inner_edges = True
		for edge in face.edges:
			if len(edge.link_faces) != 2:
				all_inner_edges = False
				break
		if all_inner_edges:
			face_indices = [vertex_map[v.index] for v in face.verts]
			faces.append(face_indices)
			for i in range(len(face_indices) - 1):
				edges.append((face_indices[i], face_indices[i+1]))
			edges.append((face_indices[-1], face_indices[0])) 

	new_mesh = bpy.data.meshes.new("InnerEdges")
	new_mesh.from_pydata(vertices, edges, faces) 
	new_mesh.update()
	new_object = bpy.data.objects.new("InnerEdges", new_mesh)
	bpy.context.collection.objects.link(new_object)
	bm.free()
	return new_object


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


if bpy:
	@bpy.utils.register_class
	class TilesPanel(bpy.types.Panel):
		bl_idname = "TILES_PT_Tiles_Object_Panel"
		bl_label = "Spectre Tile"
		bl_space_type = "PROPERTIES"
		bl_region_type = "WINDOW"
		bl_context = "object"

		def draw(self, context):
			if not context.active_object: return
			ob = context.active_object
			if ob.type=='CURVE':
				for spline in ob.data.splines:
					if spline.use_cyclic_u:
						a = spline.calc_length()
						self.layout.label(text="length=%s" % a)
						break
				return
			if not ob.tile_index: return

			self.layout.label(text="index=%s" % ob.tile_index)
			self.layout.prop(ob, 'tile_collection')

			row = self.layout.row()
			row.prop(ob, 'tile_shape_border_left', text="<|")
			row.prop(ob, 'tile_shape_border_right', text="|>")
			row.prop(ob, 'tile_shape_left', text="<")
			row.prop(ob, 'tile_shape_join', text="|")
			row.prop(ob, 'tile_shape_right', text=">")

			row = self.layout.row()
			row.operator('spectre.tile_shape_border_left')
			row.operator('spectre.tile_shape_border_right')

			row = self.layout.row()
			if ob.tile_shape_left:
				row.operator('spectre.tile_left', text="LEFT✔")
			else:
				row.operator('spectre.tile_left')


			if ob.tile_shape_join:
				row.operator('spectre.tile_join', text="JOIN✔")
			else:
				row.operator('spectre.tile_join')
			if ob.tile_shape_right:
				row.operator('spectre.tile_right', text="RIGHT✔")
			else:
				row.operator('spectre.tile_right')

			self.layout.label(text="x=%s y=%s angle=%s" % (round(ob.tile_x,2), round(ob.tile_y), ob.tile_angle))

			self.layout.prop(ob, 'tile_pair')

	@bpy.utils.register_class
	class SpecExport(bpy.types.Operator):
		bl_idname = "spectre.export_json"
		bl_label = "Spectre export json"
		@classmethod
		def poll(cls, context):
			return True
		def execute(self, context):
			export_json(context.world)
			return {"FINISHED"}

	@bpy.utils.register_class
	class SpecImport(bpy.types.Operator):
		bl_idname = "spectre.import_json"
		bl_label = "Spectre import json"
		@classmethod
		def poll(cls, context):
			return True
		def execute(self, context):
			path = context.world.tile_import_path.strip()
			if not path: path = '/tmp/spectre.json'
			if path.startswith('~'): path = os.path.expanduser(path)
			if not path.endswith('.json'): path += '.json'
			import_json(path)
			return {"FINISHED"}


	@bpy.utils.register_class
	class SpecLeft(bpy.types.Operator):
		bl_idname = "spectre.tile_left"
		bl_label = "Left"
		@classmethod
		def poll(cls, context):
			return context.active_object
		def execute(self, context):
			ob = context.active_object
			ob.tile_shape_left = True
			ob.tile_shape_right = False
			if not ob.tile_collection:
				if bpy.data.worlds[0].tile_active_collection:
					ob.tile_collection=bpy.data.worlds[0].tile_active_collection
			if ob.data.materials[0].name != 'LEFT':
				ob.data.materials.clear()
				mat = smaterial('LEFT', [1,0,0])
				ob.data.materials.append(mat)
			ob.color = [1,0,0, 1]
			if ob.tile_pair:
				ob.tile_pair.select_set(True)
			if ob.tile_pair and not ob.tile_pair.tile_shape_right:
				ob = ob.tile_pair
				ob.tile_shape_right=True
				if not ob.tile_collection:
					if bpy.data.worlds[0].tile_active_collection:
						ob.tile_collection=bpy.data.worlds[0].tile_active_collection

				if ob.data.materials[0].name != 'RIGHT':
					ob.data.materials.clear()
					mat = smaterial('RIGHT', [0,0,1])
					ob.data.materials.append(mat)
				ob.color = [0,0,1, 1]
			return {"FINISHED"}

	@bpy.utils.register_class
	class SpecLeftBorder(bpy.types.Operator):
		bl_idname = "spectre.tile_shape_border_left"
		bl_label = "Left Border"
		@classmethod
		def poll(cls, context):
			return context.active_object
		def execute(self, context):
			ob = context.active_object
			ob.tile_shape_border_left = True
			ob.tile_shape_border_right = False
			if not ob.tile_collection:
				if bpy.data.worlds[0].tile_active_collection:
					ob.tile_collection=bpy.data.worlds[0].tile_active_collection
			if ob.data.materials[0].name != 'LEFT_EDGE':
				ob.data.materials.clear()
				mat = smaterial('LEFT_EDGE', [1,0.5,0])
				ob.data.materials.append(mat)
			ob.color = [1,0.5,0, 1]
			if ob.tile_pair:
				ob.tile_pair.select_set(True)
			if ob.tile_pair and not ob.tile_pair.tile_shape_border_right:
				ob = ob.tile_pair
				ob.tile_shape_border_right=True
				if not ob.tile_collection:
					if bpy.data.worlds[0].tile_active_collection:
						ob.tile_collection=bpy.data.worlds[0].tile_active_collection
				if ob.data.materials[0].name != 'RIGHT_EDGE':
					ob.data.materials.clear()
					mat = smaterial('RIGHT_EDGE', [0,0.5,1])
					ob.data.materials.append(mat)
				ob.color = [0,0.5,1, 1]
			return {"FINISHED"}

	@bpy.utils.register_class
	class SpecRightBorder(bpy.types.Operator):
		bl_idname = "spectre.tile_shape_border_right"
		bl_label = "Right Border"
		@classmethod
		def poll(cls, context):
			return context.active_object
		def execute(self, context):
			ob = context.active_object
			ob.tile_shape_border_left = False
			ob.tile_shape_border_right = True
			if not ob.tile_collection:
				if bpy.data.worlds[0].tile_active_collection:
					ob.tile_collection=bpy.data.worlds[0].tile_active_collection
			if ob.data.materials[0].name != 'RIGHT_EDGE':
				ob.data.materials.clear()
				mat = smaterial('RIGHT_EDGE', [0,0.5,1])
				ob.data.materials.append(mat)
			ob.color = [0,0.5,1, 1]
			if ob.tile_pair:
				ob.tile_pair.select_set(True)
			if ob.tile_pair and not ob.tile_pair.tile_shape_border_left:
				ob = ob.tile_pair
				ob.tile_shape_border_left=True
				if not ob.tile_collection:
					if bpy.data.worlds[0].tile_active_collection:
						ob.tile_collection=bpy.data.worlds[0].tile_active_collection
				if ob.data.materials[0].name != 'LEFT_EDGE':
					ob.data.materials.clear()
					mat = smaterial('LEFT_EDGE', [1,0.5,0])
					ob.data.materials.append(mat)
				ob.color = [1,0.5,0, 1]
			return {"FINISHED"}


	@bpy.utils.register_class
	class SpecRight(bpy.types.Operator):
		bl_idname = "spectre.tile_right"
		bl_label = "Right"
		@classmethod
		def poll(cls, context):
			return context.active_object
		def execute(self, context):
			ob = context.active_object
			ob.tile_shape_right = True
			ob.tile_shape_left = False
			if not ob.tile_collection:
				if bpy.data.worlds[0].tile_active_collection:
					ob.tile_collection=bpy.data.worlds[0].tile_active_collection
			if ob.data.materials[0].name != 'RIGHT':
				ob.data.materials.clear()
				mat = smaterial('RIGHT', [0,0,1])
				ob.data.materials.append(mat)
			ob.color = [0,0,1, 1]
			if ob.tile_pair:
				ob.tile_pair.select_set(True)

			if ob.tile_pair and not ob.tile_pair.tile_shape_left:
				ob = ob.tile_pair
				ob.tile_shape_left=True
				if not ob.tile_collection:
					if bpy.data.worlds[0].tile_active_collection:
						ob.tile_collection=bpy.data.worlds[0].tile_active_collection

				if ob.data.materials[0].name != 'LEFT':
					ob.data.materials.clear()
					mat = smaterial('LEFT', [1,0,0])
					ob.data.materials.append(mat)
				ob.color = [1,0,0, 1]

			return {"FINISHED"}

	@bpy.utils.register_class
	class SpecJoin(bpy.types.Operator):
		bl_idname = "spectre.tile_join"
		bl_label = "Join"
		@classmethod
		def poll(cls, context):
			return context.active_object
		def execute(self, context):
			ob = context.active_object
			ob.tile_shape_join = True
			if not ob.tile_collection:
				if bpy.data.worlds[0].tile_active_collection:
					ob.tile_collection=bpy.data.worlds[0].tile_active_collection
			if ob.data.materials[0].name != 'JOIN':
				ob.data.materials.clear()
				mat = smaterial('JOIN', [0,1,0])
				ob.data.materials.append(mat)
			ob.color = [0,1,0, 1]
			return {"FINISHED"}

	@bpy.utils.register_class
	class SpecGenerate(bpy.types.Operator):
		bl_idname = "spectre.generate"
		bl_label = "Generate"
		@classmethod
		def poll(cls, context):
			return True
		def execute(self, context):
			build_tiles(
				iterations=bpy.data.worlds[0].tile_generate_steps,
				gizmos=bpy.data.worlds[0].tile_generate_gizmos,
			)

			return {"FINISHED"}



	@bpy.utils.register_class
	class SpecWorldPanel(bpy.types.Panel):
		bl_idname = "WORLD_PT_Spec_Panel"
		bl_label = "Spectre Tiles"
		bl_space_type = "PROPERTIES"
		bl_region_type = "WINDOW"
		bl_context = "world"
		def draw(self, context):
			self.layout.prop(context.world, 'tile_active_collection')

			box = self.layout.box()
			box.label(text="Export:")

			box.prop(context.world, 'tile_export_path')
			box.operator("spectre.export_json", icon="CONSOLE")

			box = self.layout.box()
			box.label(text="Import:")

			box.prop(context.world, 'tile_import_path')
			box.operator("spectre.import_json", icon="CONSOLE")

			box = self.layout.box()
			box.label(text="Generate:")
			row = box.row()
			row.prop(context.world, 'tile_generate_steps')
			row.prop(context.world, 'tile_generate_gizmos')
			box.operator("spectre.generate", icon="CONSOLE")


def export_json(world):
	import json
	tiles = []
	shapes = {}
	for ob in bpy.data.objects:
		if not ob.tile_index: continue
		r,g,b,a = ob.data.materials[0].diffuse_color
		o = {
			'name':ob.name,
			'index':ob.tile_index,
			'x':ob.tile_x,
			'y':ob.tile_y,
			'angle':ob.tile_angle,
			'color':[r,g,b],
		}
		if ob.tile_mystic:
			o['mystic']=1
		if ob.tile_shape_border_left:
			o['border']='left'
		if ob.tile_shape_border_right:
			o['border']='right'
		if ob.tile_shape_left:
			o['type']='left'
		if ob.tile_shape_right:
			o['type']='right'
		if ob.tile_shape_join:
			o['join']=1
		if ob.tile_pair:
			o['pair']=ob.tile_pair.name

		if ob.tile_collection:
			if ob.tile_collection.name not in shapes:
				shapes[ob.tile_collection.name] = []
			shapes[ob.tile_collection.name].append(o)
		elif ob.select_get():
			tiles.append( o )

	if world.tile_export_path.strip():
		tmp = world.tile_export_path.strip()
		if tmp.startswith('~'): tmp = os.path.expanduser(tmp)
		if not tmp.endswith('.json'): tmp += '.json'
	else:
		tmp = '/tmp/spectre.json'
	dump = json.dumps( {'shapes':shapes, 'tiles':tiles} )
	#print(dump)
	print('saving:', tmp)
	open(tmp, 'wb').write(dump.encode('utf-8'))




if __name__ == '__main__':
	args = []
	kwargs = {}
	blend = None
	jfile = None
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
		elif arg.endswith('.json'):
			args.append(arg)
			jfile = arg
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
	if jfile:
		import_json( jfile )
	elif '--print' in sys.argv:
		RENDER_TEST = True
		build_tiles(a=5, b=5, iterations=5)
	elif 'shapes' in kwargs:
		mkshapes(**kwargs)
	elif 'iterations' in kwargs:
		tmp = '/tmp/spectre.%s.blend' % kwargs['iterations']
		#if not os.path.isfile(tmp):
		build_tiles(**kwargs)
		bpy.ops.wm.save_as_mainfile(filepath=tmp, check_existing=False)

	#else:
	#	build_tiles(**kwargs)
