import bpy, sys, math
from mathutils import Vector
name,cam3,tgt3,ortho=sys.argv[sys.argv.index('--')+1], eval(sys.argv[-3]), eval(sys.argv[-2]), float(sys.argv[-1])
bpy.ops.wm.open_mainfile(filepath=f'/workspace/props/{name}.blend')
T=lambda v: Vector((v[0],-v[2],v[1]))
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1280; sc.render.resolution_y=960
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1); w.node_tree.nodes['Background'].inputs[1].default_value=.35
sc.view_settings.view_transform='Standard'
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
cam.location=T(cam3); d=T(tgt3)-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
if ortho>0: cam.data.type='ORTHO'; cam.data.ortho_scale=ortho
else: cam.data.lens=50
for loc,e in(((2,-2,3),4),((-2,-1,2),2)):
    l=bpy.data.objects.new('l',bpy.data.lights.new('l','SUN')); l.data.energy=e; sc.collection.objects.link(l); l.rotation_euler=(Vector((0,0,0))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=10); p=bpy.context.object; m=bpy.data.materials.new('floor'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.95,.95,.95,1); p.data.materials.append(m)
sc.render.filepath=f'/workspace/props/render_{name}.png'; bpy.ops.render.render(write_still=True)
