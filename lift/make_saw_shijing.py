# Blender 4.5: SHIJING 9201A-1600 large-format electric wet tile saw (overhead rail, moving head). Specs: cut length 1600, table 1600x600,
# disc 200 mm (kerf 2.0), cut depth 50 (90deg)/40 (45deg), 4500 W brushless, 3000-6000 rpm, laser, 2 side tables, 56 kg, package 2280x610x580.
# Game frame (three.js, y up): x = rail / cut direction, z = depth (+z = operator side), origin = floor centre; T() converts to Blender.
import bpy, math
from mathutils import Vector, Matrix
OUT='/workspace/lift/'
def T(v): return Vector((v[0],-v[2],v[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(n,rgb,met=0,rough=.5):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Metallic'].default_value=met; b.inputs['Roughness'].default_value=rough; return m
RED=mat('Shijing_Grey',(.18,.2,.23),0,.45); BLK=mat('Black_Paint',(.04,.04,.045),0,.5); RUB=mat('Table_Rubber',(.05,.05,.05),0,.9); ALU=mat('Rail_Alu',(.75,.76,.78),.6,.3)
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
TY=.70; ZB,ZF=-.62,.10; L=1.60
RED=mat('Shijing_Orange',(.92,.42,.05),0,.45)
box('Table_Back',(0,TY-.005,(ZB-.003)/2),(L,.01,-ZB-.003),RUB); box('Table_Front',(0,TY-.005,(ZF+.003)/2),(L,.01,ZF-.003),RUB)
box('Table_Groove',(0,TY-.012,0),(L,.004,.006),RED,bev=0)
box('Body_Tray',(0,TY-.06,-.26),(L+.06,.10,.76),BLK); box('Body_Rail_F',(0,TY-.03,ZF+.02),(L+.12,.05,.03),BLK); box('Body_Rail_B',(0,TY-.03,ZB-.02),(L+.12,.05,.03),BLK)
box('Water_Tray_Orange',(0,TY-.115,-.26),(L-.1,.02,.70),RED)
box('Label_Plate',(-.20,TY-.035,ZF+.036),(.40,.03,.002),WHT,bev=0)
for s_ in(-1,1):
    box('Side_Table_%d'%s_,(s_*(L/2+.17),TY-.006,-.26),(.30,.012,.50),ALU); box('Side_Table_Arm_%d'%s_,(s_*(L/2+.05),TY-.03,-.26),(.12,.03,.04),BLK)
for sx in(-1,1):
    for sz in(-1,1):
        o=box('Leg_%d_%d'%(sx,sz),(sx*.74,(TY-.11)/2,-.26+sz*.32),(.04,TY-.09,.04),BLK); o.rotation_euler=(0,math.radians(-6*sx),0)
    box('Leg_Brace_%d'%sx,(sx*.70,.30,-.26),(.025,.025,.64),BLK)
for sz in(-1,1): cyl('Wheel_%d'%sz,(.82,.07,-.26+sz*.34),.08,.04,'z',BLK)
# rail columns at both ends behind the table; aluminium rail 1850 above, head arm reaches the cut line
for s_ in(-1,1): box('Column_%d'%s_,(s_*.90,TY+.17,-.70),(.05,.46,.06),BLK)
RY=TY+.38; box('Rail_Alu_1850',(0,RY,-.70),(1.85,.07,.06),ALU); box('Rail_Cap',(0,RY+.037,-.70),(1.85,.004,.062),RED,bev=0)
for i in range(7): box('Cable_Chain_%d'%i,(-.95,RY-.02-i*.05,-.74+.01*i),(.03,.04,.03),BLK)
# fence with knob; origin = front face (moves along -z, 5..600 mm from the disc)
bpy.ops.object.empty_add(location=T((0,TY,-.10))); fence=bpy.context.object; fence.name='Saw_Fence'
box('Fence_Angle_V',(0,TY+.025,-.10-.002),(1.30,.05,.004),ALU,fence,bev=0); box('Fence_Angle_H',(0,TY+.002,-.10-.025),(1.30,.004,.05),ALU,fence,bev=0)
for s_ in(-1,1): box('Fence_Knob_%d'%s_,(s_*.62,TY+.05,-.13),(.035,.035,.035),BLK,fence)
box('Scale_Strip',(.73,TY+.001,-.31),(.03,.002,.60),WHT,bev=0)
DY=TY+.10-.05
bpy.ops.object.empty_add(location=T((0,DY,0))); head=bpy.context.object; head.name='Saw_Head'
box('Carriage',(0,RY,-.70),(.16,.12,.12),BLK,head); box('Head_Arm',(0,RY-.06,-.40),(.07,.06,.60),BLK,head)
box('Head_Drop',(0,(RY+DY)/2,-.12),(.07,RY-DY,.07),BLK,head)
cyl('Motor_Brushless',(0,DY+.02,-.13),.06,.14,'z',RED,head,28); cyl('Motor_Cap',(0,DY+.02,-.205),.045,.012,'z',GRY,head)
cyl('Guard',(0,DY+.02,.0),.12,.05,'z',RED,head,40)
box('Guard_cut',(0,DY-.09,0),(.4,.2,.08),RED,head,bev=0)
g=bpy.data.objects['Guard']; b=g.modifiers.new('cut','BOOLEAN'); b.object=bpy.data.objects['Guard_cut']; b.operation='DIFFERENCE'; b.solver='EXACT'
bpy.context.view_layer.objects.active=g; bpy.ops.object.modifier_apply(modifier='cut'); bpy.data.objects.remove(bpy.data.objects['Guard_cut'])
box('Laser_Unit',(.13,DY+.10,.0),(.03,.03,.03),RED,head)
cyl('Handle_Grip',(-.18,DY+.16,.0),.016,.12,'x',BLK,head); box('Handle_Bar',(-.11,DY+.16,0),(.12,.02,.02),GRY,head)
bpy.ops.object.empty_add(location=T((0,DY,0))); dsk=bpy.context.object; dsk.name='Saw_Disc'; dsk.parent=head; dsk.matrix_parent_inverse=head.matrix_world.inverted()
cyl('Disc_Body',(0,DY,0),.095,.0016,'z',DSK,dsk,64); cyl('Disc_Rim',(0,DY,0),.10,.0020,'z',SEG,dsk,64); cyl('Disc_Flange',(0,DY,.0025),.025,.004,'z',GRY,dsk,24)
for k in range(8):
    a=k*math.pi/4; box('Disc_Slot_%d'%k,(math.cos(a)*.091,DY+math.sin(a)*.091,0),(.01,.002,.0024),BLK,dsk,bev=0)
# export
n=0
for o in bpy.data.objects:
    if o.type=='MESH': o.data.calc_loop_triangles(); n+=len(o.data.loop_triangles)
print('SAW_TRIS',n)
bpy.ops.export_scene.gltf(filepath=OUT+'tile_saw_shijing.glb',export_format='GLB',export_apply=True,export_yup=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'tile_saw_shijing.blend')
# render 3/4 front-left like the product photo
sc=bpy.context.scene
bpy.ops.object.camera_add(location=T((-1.8,1.9,1.9))); c=bpy.context.object; sc.camera=c
dirv=T((0.0,.6,-.3))-c.location; c.rotation_euler=dirv.to_track_quat('-Z','Y').to_euler(); c.data.lens=40
bpy.ops.object.light_add(type='SUN'); s=bpy.context.object; s.data.energy=3; s.rotation_euler=(math.radians(45),0,math.radians(-30))
bpy.ops.object.light_add(type='SUN'); s=bpy.context.object; s.data.energy=1; s.rotation_euler=(math.radians(70),0,math.radians(140))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1); w.node_tree.nodes['Background'].inputs[1].default_value=.9
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1024; sc.render.resolution_y=700; sc.view_settings.view_transform='Standard'; sc.render.filepath=OUT+'saw_shijing_render.png'; bpy.ops.render.render(write_still=True)
