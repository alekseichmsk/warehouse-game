# Blender 4.5: ЗУБР ЭП-250-1200С electric wet tile saw (rail type, moving head) after lift/saw.jpg + manufacturer specs:
# table 1060x468 rubber, table height 700, overall 1370x590x460 (w/o legs), disc 250x25.4 (kerf 2.2), cut length 1020, depth 52, 2950 rpm.
# Game frame (three.js, y up): x = rail / cut direction, z = depth (+z = operator side), origin = floor centre; T() converts to Blender.
import bpy, math
from mathutils import Vector, Matrix
OUT='/workspace/lift/'
def T(v): return Vector((v[0],-v[2],v[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(n,rgb,met=0,rough=.5):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Metallic'].default_value=met; b.inputs['Roughness'].default_value=rough; return m
RED=mat('Zubr_Red',(.78,.05,.04),0,.45); BLK=mat('Black_Paint',(.04,.04,.045),0,.5); RUB=mat('Table_Rubber',(.05,.05,.05),0,.9); ALU=mat('Rail_Alu',(.75,.76,.78),.6,.3)
DSK=mat('Diamond_Disc',(.62,.64,.66),.7,.35); SEG=mat('Disc_Segments',(.25,.25,.26),.4,.6); BLU=mat('Water_Hose',(.2,.6,.7),0,.4); GRY=mat('Grey_Plastic',(.35,.36,.38),0,.5); WHT=mat('Label',(.92,.92,.9),0,.5)
def box(n,c,s,m,par=None,bev=.0015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=T(c)); o=bpy.context.object; o.name=n; o.scale=(s[0],s[2],s[1]); bpy.ops.object.transform_apply(scale=True)
    if bev: mo=o.modifiers.new('b','BEVEL'); mo.width=bev; mo.segments=1
    o.data.materials.append(m)
    if par: o.parent=par; o.matrix_parent_inverse=par.matrix_world.inverted()
    return o
def cyl(n,c,r,L,axis,m,par=None,v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=L,location=T(c)); o=bpy.context.object; o.name=n
    if axis=='x': o.rotation_euler=(0,math.pi/2,0)
    elif axis=='z': o.rotation_euler=(math.pi/2,0,0)   # game z = blender -y
    o.data.materials.append(m)
    if par: o.parent=par; o.matrix_parent_inverse=par.matrix_world.inverted()
    return o
TY=.70; ZB,ZF=-.30,.168
# rubber table, two halves with the blade groove at z=0
box('Table_Back',(0,TY-.005,(ZB-.003)/2),(1.06,.01,-ZB-.003),RUB); box('Table_Front',(0,TY-.005,(ZF+.003)/2),(1.06,.01,ZF-.003),RUB)
box('Table_Groove_Red',(0,TY-.012,0),(1.06,.004,.006),RED,bev=0)
# red body: water tray + frame rails, end gussets
box('Body_Tray',(0,TY-.06,-.066),(1.12,.10,.52),RED); box('Body_Rail_F',(0,TY-.03,ZF+.02),(1.20,.05,.03),RED); box('Body_Rail_B',(0,TY-.03,ZB-.02),(1.20,.05,.03),RED)
for s in(-1,1): box('Gusset_%d'%s,(s*.585,TY+.04,-.20),(.02,.14,.18),RED)
box('Label_Plate',(-.12,TY-.035,ZF+.036),(.30,.03,.002),WHT,bev=0)
box('Side_Table',(.08,TY-.06,ZF+.12),(.26,.012,.18),RED); box('Side_Table_Mat',(.08,TY-.053,ZF+.12),(.24,.004,.16),RUB,bev=0)
# legs (folding, black) + wheels on the right end
for sx in(-1,1):
    for sz in(-1,1):
        o=box('Leg_%d_%d'%(sx,sz),(sx*.55,(TY-.11)/2,sz*.23-.066),(.035,TY-.09,.035),BLK); o.rotation_euler=(0,math.radians(-9*sx),0)
    box('Leg_Brace_%d'%sx,(sx*.50,.35,-.066),(.02,.02,.46),BLK)
for sz in(-1,1): cyl('Wheel_%d'%sz,(.63,.07,sz*.26-.066),.08,.04,'z',BLK)
# rail columns + aluminium rail (at the back, head overhangs to the cut line)
for s in(-1,1): box('Column_%d'%s,(s*.665,TY+.15,-.255),(.04,.42,.05),BLK)
RY=TY+.33; box('Rail_Alu_1370',(0,RY,-.255),(1.37,.06,.05),ALU); box('Rail_Cap',(0,RY+.032,-.255),(1.37,.004,.052),BLK,bev=0)
# cable chain on the left
for i in range(6): box('Cable_Chain_%d'%i,(-.70+.0*i,RY-.02-i*.05,-.30+.012*i),(.03,.04,.03),BLK)
# fence (упор со шкалой) on the BACK half: aluminium angle parallel to the cut, origin = its front face (moves along -z)
bpy.ops.object.empty_add(location=T((0,TY,-.10))); fence=bpy.context.object; fence.name='Saw_Fence'
box('Fence_Angle_V',(0,TY+.02,-.10-.0015),(.80,.04,.003),ALU,fence,bev=0); box('Fence_Angle_H',(0,TY+.0015,-.10-.02),(.80,.003,.04),ALU,fence,bev=0)
box('Fence_Knob',(.38,TY+.045,-.12),(.03,.03,.03),BLK,fence)
box('Scale_Strip',(.505,TY+.001,-.15),(.03,.002,.30),WHT,bev=0)
# moving head: empty at the disc centre (TY+0.073 => 52 mm depth)
DY=TY+.125-.052
bpy.ops.object.empty_add(location=T((0,DY,0))); head=bpy.context.object; head.name='Saw_Head'
box('Carriage',(0,RY,-.255),(.12,.10,.10),BLK,head); box('Head_Arm',(0,RY-.08,-.14),(.06,.06,.18),BLK,head)
cyl('Motor',(0,DY+.03,-.12),.065,.16,'z',BLK,head,28); cyl('Motor_Cap',(0,DY+.03,-.205),.05,.012,'z',GRY,head)
cyl('Guard',(0,DY+.03,.0),.145,.05,'z',RED,head,40)
box('Guard_cut',(0,DY-.10,0),(.4,.2,.08),RED,head,bev=0)
g=bpy.data.objects['Guard']; b=g.modifiers.new('cut','BOOLEAN'); b.object=bpy.data.objects['Guard_cut']; b.operation='DIFFERENCE'; b.solver='EXACT'
bpy.context.view_layer.objects.active=g; bpy.ops.object.modifier_apply(modifier='cut'); bpy.data.objects.remove(bpy.data.objects['Guard_cut'])
cyl('Guard_Hub',(0,DY,.028),.03,.012,'z',RED,head)
# handle bar (lever) up and forward
bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.011,depth=.42,location=T((-.08,DY+.24,-.02))); h=bpy.context.object; h.name='Handle_Bar'; h.rotation_euler=(0,math.radians(-35),0); h.data.materials.append(GRY); h.parent=head; h.matrix_parent_inverse=head.matrix_world.inverted()
cyl('Handle_Grip',(-.20,DY+.41,-.02),.016,.10,'x',BLK,head)
# water hose to the guard nozzle
for i,(a,bq) in enumerate([((.0,RY-.05,-.22),(.05,DY+.12,-.05)),((.05,DY+.12,-.05),(.04,DY+.06,.03))]):
    A=Vector(a);B=Vector(bq);M=(A+B)/2;L=(B-A).length; o=cyl('Water_Hose_%d'%i,tuple(M),.005,L,'y',BLU,head,10); d=T(B)-T(A); o.rotation_mode='QUATERNION'; o.rotation_quaternion=Vector((0,0,1)).rotation_difference(d)
# disc 250 x 2.2 (separate node so it can spin about local z)
bpy.ops.object.empty_add(location=T((0,DY,0))); dsk=bpy.context.object; dsk.name='Saw_Disc'; dsk.parent=head; dsk.matrix_parent_inverse=head.matrix_world.inverted()
cyl('Disc_Body',(0,DY,0),.118,.0018,'z',DSK,dsk,64); cyl('Disc_Rim',(0,DY,0),.125,.0022,'z',SEG,dsk,64); cyl('Disc_Flange',(0,DY,.0025),.03,.004,'z',GRY,dsk,24)
for k in range(8):
    a=k*math.pi/4; box('Disc_Slot_%d'%k,(math.cos(a)*.114,DY+math.sin(a)*.114,0),(.012,.002,.0026),BLK,dsk,bev=0)
# export
n=0
for o in bpy.data.objects:
    if o.type=='MESH': o.data.calc_loop_triangles(); n+=len(o.data.loop_triangles)
print('SAW_TRIS',n)
bpy.ops.export_scene.gltf(filepath=OUT+'tile_saw_zubr.glb',export_format='GLB',export_apply=True,export_yup=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'tile_saw_zubr.blend')
# render 3/4 front-left like the product photo
sc=bpy.context.scene
bpy.ops.object.camera_add(location=T((-1.35,1.55,1.75))); c=bpy.context.object; sc.camera=c
dirv=T((0.05,.55,-.05))-c.location; c.rotation_euler=dirv.to_track_quat('-Z','Y').to_euler(); c.data.lens=40
bpy.ops.object.light_add(type='SUN'); s=bpy.context.object; s.data.energy=3; s.rotation_euler=(math.radians(45),0,math.radians(-30))
bpy.ops.object.light_add(type='SUN'); s=bpy.context.object; s.data.energy=1; s.rotation_euler=(math.radians(70),0,math.radians(140))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1); w.node_tree.nodes['Background'].inputs[1].default_value=.9
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1024; sc.render.resolution_y=700; sc.view_settings.view_transform='Standard'; sc.render.filepath=OUT+'saw_render.png'; bpy.ops.render.render(write_still=True)
