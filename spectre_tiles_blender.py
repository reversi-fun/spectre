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

	cam = bpy.data.objects['Camera']
	cam.data.type='ORTHO'
	cam.data.ortho_scale = 50
	cam.rotation_euler = [math.pi/2, 0,0]
	cam.location = [8, -1, -15]
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

		if False:
			mod = lattice.modifiers.new(type='CAST', name='cast')
			mod.cast_type = "CYLINDER"
			mod.factor = 10
			mod.use_y = True
			mod.use_z = False

		mod = lattice.modifiers.new(type='SIMPLE_DEFORM', name='bend')
		mod.deform_method='BEND'
		mod.deform_axis = 'Z'
		mod.angle = 0
		#mod.angle = math.radians(645)
		#mod.angle = math.radians(544)
		#mod.angle = math.radians(746)

		lattice.data.points_u = 8
		lattice.data.points_v = 2
		lattice.data.points_w = 1
		#lattice.scale *= 100
		#lattice.location.x = 10

		for info in TRACE:
			o = info[0]
			mod = o.modifiers.new(type="LATTICE", name='lattice')
			mod.object=lattice

	if iterations==5:
		scn.render.resolution_percentage = 200
		for i,v in enumerate(CAM_COORDS):
			cam.location.x = v[0]
			cam.location.z = v[1]
			scn.render.filepath='/tmp/tiles.%s.png' % i
			bpy.ops.render.render(write_still=True)


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
	[25, -45],
	[50, -45],

	[50, -60],
	[25, -60],
	[0, -60],
	[-25, -60],
	[-50, -60],

]

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
def plotVertices(tile_transformation, label, scale=1.0, gizmos=False, center=False, gpencil=None):
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

	verts = []
	for v in vertices:
		x,y = v
		#verts.append([x*scale,0,y*scale])
		verts.append([x,0,y])

	if gpencil:
		if label not in gpencil.data.layers:
			layer = gpencil.data.layers.new(label)
			frame = layer.frames.new(1)
		frame = gpencil.data.layers[label].frames[0]
		stroke = frame.strokes.new()
		stroke.points.add(count=len(verts))
		stroke.line_width = 100
		#print(dir(stroke))
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

	else:

		faces = [
			list(range(len(verts)))
		]

		mesh = bpy.data.meshes.new(label)
		mesh.from_pydata(verts, [], faces)
		# Create object
		#if 'SPECTRE' not in bpy.data.meshes:
		#mesh = mktiles(SPECTRE_POINTS, scale=scale)
		#mesh = bpy.data.meshes['SPECTRE']
		oname='%s(%s.%s)' % (label, rot,scl)
		obj = bpy.data.objects.new(oname, mesh)
		bpy.context.collection.objects.link(obj)

		if scl == 1:
			obj.color = [0,0,0,1]
		else:
			obj.color = list(color_array) + [1]

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

		if scl == 1:
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



if __name__ == '__main__':
	args = []
	kwargs = {}
	blend = None
	for arg in sys.argv:
		if arg.startswith('--') and '=' in arg:
			args.append(arg)
			k,v = arg.split('=')
			k = k[2:]
			if k=='iterations':
				kwargs[k]=int(v)
			else:
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

	print('kwargs:', kwargs)
	build_tiles(**kwargs)
