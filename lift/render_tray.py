import bpy, math
bpy.ops.wm.open_mainfile(filepath='/workspace/lift/lift_floor_tray.blend')
sc=bpy.context.scene
def cam(loc,rot,lens,out):
    bpy.ops.object.camera_add(location=loc); c=bpy.context.object; c.rotation_euler=[math.radians(a) for a in rot]; c.data.lens=lens; sc.camera=c
    sc.render.filepath=out; bpy.ops.render.render(write_still=True)
bpy.ops.object.light_add(type='SUN',location=(0,0,3)); s=bpy.context.object; s.data.energy=3; s.rotation_euler=(math.radians(40),0,math.radians(30))
bpy.ops.object.light_add(type='SUN',location=(0,0,-3)); s=bpy.context.object; s.data.energy=1.2; s.rotation_euler=(math.radians(150),0,math.radians(-40))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=.6
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1000; sc.render.resolution_y=700; sc.view_settings.view_transform='Standard'
cam((1.9,-2.3,1.5),(60,0,40),35,'/workspace/lift/tray_top.png')
cam((1.6,-1.9,-.9),(118,0,40),35,'/workspace/lift/tray_bottom.png')
cam((.35,-1.33,.25),(62,0,25),50,'/workspace/lift/tray_threshold.png')
