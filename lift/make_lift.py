# Blender 4.5 headless: elevator cabin floor tray 1100x2100 (perimeter RHS 60x40x2, cross RHS 40x40x2, top sheet 2 mm, rim angle 20x20x2)
# + checker plate (рифлёнка «чечевица», AMg2 aluminium 3+1.5 mm) threshold strip 1100x150 at the door edge; also a 300x300 sample for the ref render.
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix
OUT='/workspace/lift/'
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,rgb,metal=0.0,rough=0.5):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough; return m
def box(name,cx,cy,cz,sx,sy,sz,m,bev=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,cy,cz)); o=bpy.context.object; o.name=name; o.scale=(sx,sy,sz); bpy.ops.object.transform_apply(scale=True)
    if bev>0: mo=o.modifiers.new('b','BEVEL'); mo.width=bev; mo.segments=1
    o.data.materials.append(m); return o
def tube(name,cx,cy,cz,sx,sy,sz,t,m,axis):
    # hollow rectangular hollow section: outer box minus inner (boolean), axis = long axis 'x' or 'y'
    o=box(name,cx,cy,cz,sx,sy,sz,m,bev=.002)
    ix,iy,iz=(sx+.01, sy-2*t, sz-2*t) if axis=='x' else (sx-2*t, sy+.01, sz-2*t)
    c=box(name+'_cut',cx,cy,cz,ix,iy,iz,m); b=o.modifiers.new('h','BOOLEAN'); b.object=c; b.operation='DIFFERENCE'; b.solver='EXACT'
    bpy.context.view_layer.objects.active=o
    for mo in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mo.name)
    bpy.data.objects.remove(c); return o
def lens_plate(name,W,D,t,m,pitch=.032,row=.018,L=.025,w=.0085,h=.0018,ang=28):
    plate=box(name,0,0,t/2,W,D,t,m,bev=.0006)
    bm=bmesh.new(); 
    ny=int(D/row); nx=int(W/pitch)
    for j in range(ny):
        y=-D/2+row*(j+.5); a=math.radians(ang if j%2==0 else -ang); off=(pitch/2 if j%2 else 0)
        for i in range(nx):
            x=-W/2+pitch*(i+.5)+off-pitch/4
            if abs(x)>W/2-.014: continue
            g=bmesh.ops.create_uvsphere(bm,u_segments=12,v_segments=5,radius=1)
            vs=g['verts']; M=Matrix.Translation((x,y,t))@Matrix.Rotation(a,4,'Z')@Matrix.Diagonal((L/2,w/2,h,1))
            for v in vs:
                if v.co.z<0: v.co.z=0
                v.co.y*=(1-min(1,abs(v.co.x)))**0.45*1.25
                v.co=M@v.co
    me=bpy.data.meshes.new(name+'_lens'); bm.to_mesh(me); bm.free(); lo=bpy.data.objects.new(name+'_Lens',me); bpy.context.collection.objects.link(lo); lo.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT'); plate.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active=plate; bpy.ops.object.join()
    bpy.ops.object.shade_auto_smooth(angle=math.radians(40)) if hasattr(bpy.ops.object,'shade_auto_smooth') else None
    return plate
def export(name,objs=None):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=OUT+name+'.glb',export_format='GLB',export_apply=True,export_yup=True,use_selection=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT+name+'.blend')
def tris():
    n=0
    for o in bpy.data.objects:
        if o.type=='MESH': o.data.calc_loop_triangles(); n+=len(o.data.loop_triangles)
    return n
# ---------------- tray ----------------
clear()
W,D=1.10,2.10; ST=mat('Steel_Primer',(.42,.45,.48),.3,.55); SH=mat('Sheet_Galv',(.62,.64,.66),.6,.38); AL=mat('Checker_AMg2',(.78,.79,.80),.85,.3)
H=.060
for s in(-1,1):
    tube('Beam_Long_%s'%('L' if s<0 else 'R'),s*(W/2-.02),0,H/2,.040,D,H,.002,ST,'y')
    tube('Beam_End_%s'%('Door' if s<0 else 'Back'),0,s*(D/2-.02),H/2,W-.08,.040,H,.002,ST,'x')
for k,y in enumerate([-.6,-.1,.4,.85]): tube('Beam_Cross_%d'%k,0,y,.020+.0,W-.08,.040,.040,.002,ST,'x')
box('Top_Sheet_2mm',0,0,H+.001,W,D,.002,SH,bev=.0005)
for s in(-1,1): box('Rim_Angle_%s'%('L' if s<0 else 'R'),s*(W/2-.001),0,H+.002+.010,.002,D,.020,ST); 
box('Rim_Angle_Back',0,D/2-.001,H+.002+.010,W,.002,.020,ST)
box('Rim_Angle_L_flange',-(W/2-.011),0,H+.003,.020,D,.002,ST); box('Rim_Angle_R_flange',(W/2-.011),0,H+.003,.020,D,.002,ST); box('Rim_Angle_Back_flange',0,D/2-.011,H+.003,W,.020,.002,ST)
box('Threshold_Riser_10mm',0,-D/2+.075,H+.002+.005,W-.004,.150,.010,ST)
cp=lens_plate('CheckerPlate_Threshold',W-.004,.150,.003,AL); cp.location=(0,-D/2+.075,H+.012)
print('TRAY_TRIS',tris())
export('lift_floor_tray')
# ---------------- checker plate sample 300x300 for the ref comparison render ----------------
clear(); AL=mat('Checker_AMg2',(.55,.57,.62),.45,.5)
s=lens_plate('CheckerPlate_Sample',.9,.9,.003,AL)
bpy.ops.object.camera_add(location=(0,-.17,.075)); cam=bpy.context.object; cam.rotation_euler=(math.radians(60),0,math.radians(-8)); cam.data.lens=30; bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-.15,.25,.35)); L=bpy.context.object; L.data.energy=6; L.data.size=.5
bpy.ops.object.light_add(type='SUN',location=(0,0,1)); S=bpy.context.object; S.data.energy=1.2; S.rotation_euler=(math.radians(55),0,math.radians(160))
w=bpy.data.worlds.new('w'); bpy.context.scene.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=.35
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=800; sc.render.resolution_y=800; sc.view_settings.view_transform='Standard'; sc.view_settings.exposure=-1.3
sc.render.filepath=OUT+'checker_render.png'; bpy.ops.render.render(write_still=True)
print('SAMPLE_TRIS',tris())
