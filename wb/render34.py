import bpy, os, math, re
from mathutils import Vector
sc=bpy.context.scene; O=bpy.data.objects; sc.frame_set(1)
ONLY=os.environ.get("ONLY")
for o in sc.objects:
    c=o.users_collection[0].name if o.users_collection else ''
    if ONLY: o.hide_render = not (c==ONLY or (o.parent and o.parent.users_collection and o.parent.users_collection[0].name==ONLY))
    elif c in('Room','SheetCutting','Annotations') or re.match(r"^(Demo|Arrow_|Sheet_|Rip_|Cross_|TrackSaw)",o.name): o.hide_render=True
    if o.type=='LIGHT': o.hide_render=False
try: sc.render.engine='BLENDER_EEVEE_NEXT'
except Exception: sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1400; sc.render.resolution_y=1000; sc.render.film_transparent=False
w=bpy.data.worlds.get('World') or bpy.data.worlds.new('World'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.85,0.88,0.93,1); w.node_tree.nodes['Background'].inputs[1].default_value=1.2
cd=bpy.data.cameras.new('C34'); cam=bpy.data.objects.new('C34',cd); sc.collection.objects.link(cam); cd.lens=32
c=Vector((1.0,0.85,0.75)); cam.location=c+Vector((-2.6,-3.1,1.9)); cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
sd=bpy.data.lights.new('S','SUN'); sd.energy=3.5; so=bpy.data.objects.new('S',sd); sc.collection.objects.link(so); so.rotation_euler=(math.radians(50),0,math.radians(30))
sc.render.filepath=os.environ.get("OUTPNG","/workspace/wb/render34.png"); bpy.ops.render.render(write_still=True); print("RENDERED",flush=True)
