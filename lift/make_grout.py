# Blender 4.5: grout kit (v7.3 stage 5), real dims. Grout bag 2 kg 200x300x60 (Ceresit CE 40 type: 0.64 l water per 2 kg),
# clean 10 l pail (top D290, bottom D250, H 250), 10 l HDPE water canister 230x165x330, rubber grout float 240x100, sponge 190x130x70.
# Game frame: y up, origin at the item's bottom centre.
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
WHTP=mat('Pail_White',(.93,.94,.95),0,.45); GRT=mat('Grout_Grey',(.55,.56,.58),0,.8); BLUC=mat('Canister_Blue',(.15,.38,.75),0,.35); YEL=mat('Sponge_Yellow',(.95,.78,.15),0,.95)
FLB=mat('Float_Rubber',(.18,.18,.2),0,.9); FLP=mat('Float_Base_Orange',(.95,.45,.1),0,.4); BAGM=mat('Bag_Paper',(.85,.85,.82),0,.7); BAGR=mat('Bag_Stripe',(.85,.12,.12),0,.6)
def emp(n,c=(0,0,0)):
    bpy.ops.object.empty_add(location=T(c)); o=bpy.context.object; o.name=n; return o
def cone(n,c,r1,r2,L,m,par,v=40):
    bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r1,radius2=r2,depth=L,location=T(c),end_fill_type='NOTHING'); o=bpy.context.object; o.name=n; o.data.materials.append(m); o.parent=par; o.matrix_parent_inverse=par.matrix_world.inverted(); return o
# clean pail at x=0
X=0; p=emp('Grout_Bucket',(X,0,0))
o=cone('GB_Wall',(X,.125,0),.125,.145,.25,WHTP,p); s_=o.modifiers.new('s','SOLIDIFY'); s_.thickness=.003
bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='s')
cyl('GB_Bottom',(X,.002,0),.124,.004,'y',WHTP,p,40); cyl('GB_Rim',(X,.248,0),.148,.008,'y',WHTP,p,40)
bpy.ops.mesh.primitive_torus_add(major_radius=.15,minor_radius=.003,location=T((X,.29,0))); h=bpy.context.object; h.name='GB_Handle'; h.rotation_euler=(0,math.pi/2,0); h.scale=(1,1,.55); h.data.materials.append(GRY); h.parent=p
# canister at x=.5 : 230 x 330(h) x 165
X=.5; c=emp('Water_Canister',(X,0,0))
box('WC_Body',(X,.155,0),(.23,.31,.165),BLUC,c,bev=.02); box('WC_Handle',(X-.03,.335,0),(.12,.03,.03),BLUC,c,bev=.008); box('WC_HandleL',(X-.08,.315,0),(.02,.03,.03),BLUC,c); box('WC_HandleR',(X+.02,.315,0),(.02,.03,.03),BLUC,c)
cyl('WC_Spout',(X+.08,.325,0),.02,.04,'y',BLUC,c,20); cyl('WC_Cap',(X+.08,.35,0),.024,.014,'y',BAGR,c,20)
box('WC_Scale',(X,.16,.0835),(.04,.26,.001),WHTP,c,bev=0)
# bag at x=1.0: 200 x 300 x 60 (lying flat: footprint 200 x 300, thickness 60)
X=1.0; b=emp('Grout_Bag',(X,0,0))
box('Bag_Body',(X,.03,0),(.20,.06,.30),BAGM,b,bev=.02); box('Bag_Stripe',(X,.061,-.09),(.20,.002,.05),BAGR,b,bev=0); box('Bag_Seal',(X,.03,.152),(.20,.02,.006),BAGM,b,bev=0)
# float at x=1.5: rubber 240x100x10, plastic base 240x100x12, handle
X=1.5; f=emp('Rubber_Float',(X,0,0))
box('Float_Rubber',(X,.005,0),(.24,.01,.10),FLB,f,bev=.002); box('Float_Base',(X,.016,0),(.24,.012,.10),FLP,f,bev=.002)
box('Float_Handle',(X,.065,0),(.14,.025,.03),FLP,f,bev=.008); box('Float_PostL',(X-.06,.04,0),(.02,.035,.025),FLP,f); box('Float_PostR',(X+.06,.04,0),(.02,.035,.025),FLP,f)
# sponge at x=2.0: 190 x 70(h) x 130
X=2.0; sp=emp('Grout_Sponge',(X,0,0)); box('Sponge_Body',(X,.035,0),(.19,.07,.13),YEL,sp,bev=.015)
n=0
for o in bpy.data.objects:
    if o.type=='MESH': o.data.calc_loop_triangles(); n+=len(o.data.loop_triangles)
print('GROUT_TRIS',n)
bpy.ops.export_scene.gltf(filepath=OUT+'grout_kit.glb',export_format='GLB',export_apply=True,export_yup=True)
sc=bpy.context.scene
bpy.ops.object.camera_add(location=T((1.0,1.3,2.1))); c=bpy.context.object; sc.camera=c
dirv=T((1.0,.08,0))-c.location; c.rotation_euler=dirv.to_track_quat('-Z','Y').to_euler(); c.data.lens=32
bpy.ops.object.light_add(type='SUN'); s=bpy.context.object; s.data.energy=3; s.rotation_euler=(math.radians(45),0,math.radians(-30))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1); w.node_tree.nodes['Background'].inputs[1].default_value=.35
sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1024; sc.render.resolution_y=600; sc.view_settings.view_transform='Standard'; sc.render.filepath=OUT+'grout_render.png'; bpy.ops.render.render(write_still=True)
