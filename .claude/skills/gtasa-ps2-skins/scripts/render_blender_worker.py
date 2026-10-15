"""Blender-only worker. Called by render_blender_cli.py, never by an image model."""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

args = sys.argv[sys.argv.index('--')+1:]
payload, output = Path(args[0]), Path(args[1])
data = np.load(payload)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 640
scene.render.resolution_y = 880
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world.color = (0.28, 0.28, 0.28)
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1

def world(v):
    return np.column_stack([-v[:, 2], v[:, 1], v[:, 0]])

vertices = world(data['vertices'])
posed = world(data['posed'])
mesh = bpy.data.meshes.new('Actual exported DFF')
mesh.from_pydata(vertices.tolist(), [], data['triangles'].tolist())
mesh.update()
obj = bpy.data.objects.new('sindaco_lsv2', mesh)
scene.collection.objects.link(obj)
uv_layer = mesh.uv_layers.new(name='Original DFF UV')
for poly in mesh.polygons:
    poly.use_smooth = True
    for loop_idx in poly.loop_indices:
        vi = mesh.loops[loop_idx].vertex_index
        uv_layer.data[loop_idx].uv = (data['uvs'][vi, 0], 1-data['uvs'][vi, 1])
tex = data['texture']
height, width = tex.shape[:2]
img = bpy.data.images.new('Actual TXD raster', width=width, height=height, alpha=True)
rgba = np.ones((height, width, 4), dtype=np.float32)
rgba[:, :, :3] = tex[::-1] / 255
img.pixels.foreach_set(rgba.ravel())
img.pack()
mat = bpy.data.materials.new('Vanilla TXD')
mat.use_nodes = True
nodes = mat.node_tree.nodes
texture = nodes.new('ShaderNodeTexImage')
texture.image = img
texture.interpolation = 'Closest'
shader = nodes.get('Principled BSDF')
shader.inputs['Roughness'].default_value = 1
mat.node_tree.links.new(texture.outputs['Color'], shader.inputs['Base Color'])
mat.node_tree.links.new(texture.outputs['Color'], shader.inputs['Emission Color'])
shader.inputs['Emission Strength'].default_value = .35
obj.data.materials.append(mat)

for name, location, energy, size in [('Key', (2, 4, 4), 350, 4), ('Fill', (-3, 1, 2), 100, 3)]:
    light_data = bpy.data.lights.new(name, 'AREA')
    light_data.energy, light_data.shape, light_data.size = energy, 'DISK', size
    light_obj = bpy.data.objects.new(name, light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = location
    light_obj.rotation_euler = (Vector((0, 0, 0))-light_obj.location).to_track_quat('-Z', 'Y').to_euler()
camera_data = bpy.data.cameras.new('Camera')
camera = bpy.data.objects.new('Camera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
output.mkdir(parents=True, exist_ok=True)

def render(label, yaw, pose=False, closeup=False):
    verts = posed if pose else vertices
    mesh.vertices.foreach_set('co', verts.astype(np.float32).ravel())
    mesh.update()
    center_z = (verts[:, 2].max()+verts[:, 2].min())*.5
    target = Vector((0, 0, .63 if closeup else center_z))
    a = math.radians(yaw)
    camera.location = target + Vector((math.sin(a)*4, math.cos(a)*4, 0))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
    projected_width = np.ptp(verts[:, 0]*math.cos(a)-verts[:, 1]*math.sin(a))
    camera_data.ortho_scale = .70 if closeup else max(2.1, projected_width*880/640*1.12)
    scene.render.filepath = str(output / (label+'.png'))
    bpy.ops.render.render(write_still=True)

for label, yaw, pose, closeup in [('Front', 0, False, False), ('Side', 90, False, False),
    ('Back', 180, False, False), ('ThreeQuarter', 35, False, False), ('PoseTest', 25, True, False),
    ('NeckFront', 0, False, True), ('NeckSide', 90, False, True)]:
    render(label, yaw, pose, closeup)
bpy.ops.wm.save_as_mainfile(filepath=str(output/'sindaco_lsv2.blend'))
print('BLENDER_SCREENSHOTS_COMPLETE', flush=True)
