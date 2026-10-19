import bpy, math, json, numpy as np
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
d=np.load('/workspace/hand/hand_sdf.npz'); J=json.load(open('/workspace/hand/chains.json'))
ch={k:[Vector(p) for p in v] for k,v in J['chains'].items()}; R=J['rads']
me=bpy.data.meshes.new('Hand'); me.from_pydata(d['v'].tolist(),[],d['f'].tolist()); me.update()
ob=bpy.data.objects.new('Hand_R',me); sc.collection.objects.link(ob); bpy.context.view_layer.objects.active=ob; ob.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
m=ob.modifiers.new('S','SMOOTH'); m.factor=.5; m.iterations=4; bpy.ops.object.modifier_apply(modifier='S')
dc=ob.modifiers.new('D','DECIMATE'); dc.ratio=4700/len(me.polygons); bpy.ops.object.modifier_apply(modifier='D')
bpy.ops.object.shade_smooth()
skin=bpy.data.materials.new('Skin'); skin.use_nodes=True; bs=skin.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(.60,.39,.27,1); bs.inputs['Roughness'].default_value=.6
bs.inputs['Subsurface Weight'].default_value=.12; bs.inputs['Subsurface Radius'].default_value=(.01,.004,.002)
nail=bpy.data.materials.new('Nail'); nail.use_nodes=True; bn=nail.node_tree.nodes['Principled BSDF']; bn.inputs['Base Color'].default_value=(.70,.50,.40,1); bn.inputs['Roughness'].default_value=.28
me.materials.append(skin)
nails=[]
for n,pts in ch.items():
    a,b=pts[2],pts[3]; dv=(b-a).normalized(); L=(b-a).length; r=R[n][3]
    c=a+dv*(L*.70)+Vector((0,-r*.80,0))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14,ring_count=8,radius=1,location=c); nb=bpy.context.object
    nb.scale=(r*1.0,r*.30,L*.40); nb.rotation_mode='QUATERNION'; nb.rotation_quaternion=Vector((0,0,1)).rotation_difference(dv)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True); nb.data.materials.append(nail); bpy.ops.object.shade_smooth()
    vg=nb.vertex_groups.new(name=n+'_3'); vg.add(list(range(len(nb.data.vertices))),1.0,'REPLACE'); nails.append(nb)
ad=bpy.data.armatures.new('HandRig'); arm=bpy.data.objects.new('HandRig',ad); sc.collection.objects.link(arm)
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=arm; arm.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
def bone(n,h,t,par):
    b=ad.edit_bones.new(n); b.head=h; b.tail=t; b.parent=par; b.align_roll(Vector((0,-1,0))); return b   # bone Z axis = back of hand -> X axis = flex axis
fa=bone('forearm',Vector((0,0,-.10)),Vector((0,0,0)),None); hb=bone('hand',Vector((0,0,0)),Vector((0,0,.07)),fa)
tm=J['tmeta']; t0=bone('thumb_0',Vector(tm[0]),Vector(tm[1]),hb)
for n,pts in ch.items():
    par=t0 if n=='thumb' else hb
    for i in range(3): par=bone(f'{n}_{i+1}',pts[i],pts[i+1],par)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active=arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
bpy.ops.object.select_all(action='DESELECT'); [x.select_set(True) for x in nails]; ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.join()
print('TRIS',sum(len(p.vertices)-2 for p in ob.data.polygons),'GROUPS',[g.name for g in ob.vertex_groups][:6], 'EMPTYW',sum(1 for v in ob.data.vertices if not v.groups))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/hand/hand.blend')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath='/workspace/warehouse_game/hand.glb',export_format='GLB',export_skins=True,export_yup=True,export_animations=False)
# render 4 views
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=350; sc.render.resolution_y=620
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(.16,.16,.16,1); bg.inputs[1].default_value=.7
for loc,en in [((-.8,-1.5,1.4),3.0),((1.5,1.0,.8),1.6),((0,1.8,.4),1.2),((0,-1,-.6),.6)]:
    L=bpy.data.lights.new('L','SUN'); L.energy=en; lo=bpy.data.objects.new('L',L); sc.collection.objects.link(lo); lo.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('C'); cam.type='ORTHO'; cam.ortho_scale=.31; co=bpy.data.objects.new('C',cam); sc.collection.objects.link(co); sc.camera=co
co.location=(0,-2,.05); co.rotation_euler=(math.radians(90),0,0)
import sys; pose=sys.argv[-1]
if pose=='grip':
    for pb in arm.pose.bones:
        if pb.name[-1] in '123' and not pb.name.startswith('thumb'): pb.rotation_mode='XYZ'; pb.rotation_euler.x=math.radians(80 if pb.name.endswith('1') else 95 if pb.name.endswith('2') else 60)
        if pb.name.startswith('thumb'): pb.rotation_mode='XYZ'; pb.rotation_euler.x=math.radians(30)
for i,ang in enumerate([0,-90,180,90]):
    arm.rotation_euler=(0,0,math.radians(ang)); sc.render.filepath=f'/workspace/hand/{pose}_v{i}.png'; bpy.ops.render.render(write_still=True)
