# Blender 4.5 headless: FUBAG Free Air 240/24/2.0 S compressor + combination pliers + screwdriver + hammer.
# Coordinates in the helpers are THREE.js (x right, y up, z forward); converted to Blender (x, -z, y).
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix
OUT='/workspace/props/'
def T(v): return Vector((v[0], -v[2], v[1]))
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
MATS={}
def M(name,col,rough=.5,metal=0.):
    if name in MATS: return MATS[name]
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    MATS[name]=m; return m
def obj_from_bm(bm,name,mat,parent=None,smooth=True):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o)
    me.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth=True
    if parent: o.parent=parent
    return o
def cyl(name,a,b,r,mat,seg=16,r2=None,parent=None,cap=True):
    a=T(a); b=T(b); d=b-a; L=d.length
    bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=cap,segments=seg,radius1=r,radius2=(r if r2 is None else r2),depth=L)
    q=Vector((0,0,1)).rotation_difference(d.normalized())
    bmesh.ops.transform(bm,matrix=Matrix.Translation((a+b)/2)@q.to_matrix().to_4x4(),verts=bm.verts)
    return obj_from_bm(bm,name,mat,parent)
def box(name,c,s,mat,parent=None,bevel=0.0,smooth=False,taper=None):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1)
    for v in bm.verts:
        x,y,z=v.co.x*s[0],v.co.y*s[1],v.co.z*s[2]   # three-axis sizes: s=(sx,sy,sz) mapped below
        v.co=Vector((x,y,z))
    if taper:  # taper along three z (+z end scaled)
        for v in bm.verts:
            if v.co.z>0: v.co.x*=taper[0]; v.co.y*=taper[1]
    # map three (x,y,z) local -> blender (x,-z,y)
    for v in bm.verts: v.co=Vector((v.co.x,-v.co.z,v.co.y))+T(c)
    o=obj_from_bm(bm,name,mat,parent,smooth)
    if bevel>0:
        md=o.modifiers.new('bv','BEVEL'); md.width=bevel; md.segments=2; md.limit_method='ANGLE'
    return o
def sph(name,c,r,mat,parent=None,scale=(1,1,1),seg=16):
    bm=bmesh.new(); bmesh.ops.create_uvsphere(bm,u_segments=seg,v_segments=seg//2,radius=r)
    for v in bm.verts: v.co=Vector((v.co.x*scale[0],v.co.y*scale[2],v.co.z*scale[1]))+T(c)
    return obj_from_bm(bm,name,mat,parent)
def torus(name,c,R,r,mat,axis='x',parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R,minor_radius=r,major_segments=24,minor_segments=8,location=T(c))
    o=bpy.context.object; o.name=name; o.data.materials.append(mat)
    if axis=='x': o.rotation_euler=(0,math.pi/2,0)
    for p in o.data.polygons: p.use_smooth=True
    if parent: o.parent=parent
    return o
def root(name):
    e=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(e); return e
def apply_all():
    for o in bpy.data.objects:
        if o.type=='MESH':
            bpy.context.view_layer.objects.active=o
            for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)
def export(name):
    apply_all()
    bpy.ops.wm.save_as_mainfile(filepath=OUT+name+'.blend')
    bpy.ops.export_scene.gltf(filepath=OUT+name+'.glb',export_format='GLB',export_apply=True,export_yup=True)
    tris=sum(len(o.data.loop_triangles) if (o.data.calc_loop_triangles() or True) else 0 for o in bpy.data.objects if o.type=='MESH')
    print('EXPORT',name,'tris',tris,'objs',[o.name for o in bpy.data.objects if o.parent is None])

# ---------------- COMPRESSOR (origin = floor centre, +x = wheel end, +z = front/label side) ----------------
def compressor():
    reset(); R=root('Compressor_FUBAG_FreeAir240')
    red=M('Red_Paint',(0.78,0.03,0.03),.35); blk=M('Black_Plastic',(0.03,0.03,0.035),.55); rub=M('Rubber',(0.02,0.02,0.02),.9)
    grey=M('Dark_Grey',(0.12,0.12,0.13),.5); chrome=M('Chrome',(0.8,0.8,0.82),.2,1.); wht=M('Label_White',(0.92,0.92,0.92),.6); yel=M('Label_Yellow',(0.95,0.75,0.05),.6)
    TY=.195; TR=.135; TL=.50                          # receiver: D290, L440 (24 l), axis along x
    t=cyl('Receiver_Tank',(-TL/2+.04,TY,0),(TL/2-.04,TY,0),TR,red,32,parent=R)
    for sx in(-1,1): sph('Receiver_Dome_'+('L' if sx<0 else 'R'),(sx*(TL/2-.04),TY,0),TR,red,R,(0.28,1,1),24)
    box('Label_Main',(.0,TY+.0,TR-.01),(.22,.09,.03),wht,R)
    box('Label_Specs',(.15,TY+.04,TR-.03),(.07,.09,.03),wht,R)
    # wheels D115 x 25 at +x end, rear-ish; axle bracket
    for sz in(-1,1):
        w=root('Wheel_'+('Front' if sz>0 else 'Rear')); w.location=T((.19,.0575,sz*.135)); w.parent=R
        cyl('Tyre_'+w.name,(.19,.0575,sz*.135-.0125),(.19,.0575,sz*.135+.0125),.0575,rub,24,parent=R)
        cyl('Hub_'+w.name,(.19,.0575,sz*.135-.0135),(.19,.0575,sz*.135+.0135),.03,blk,16,parent=R)
    cyl('Wheel_Axle',(.19,.0575,-.15),(.19,.0575,.15),.006,chrome,8,parent=R)
    box('Wheel_Bracket',(.19,.095,0),(.03,.07,.22),red,R,.004)
    cyl('Rubber_Foot',(-.15,.0,0),(-.15,.06,0),.03,rub,16,r2=.024,parent=R)
    # handle: vertical tube at -x end, then horizontal grip toward +x at top (h 560)
    H=.535
    cyl('Handle_Tube_V',(-.265,TY,0),(-.265,H-.02,0),.011,red,12,parent=R)
    sph('Handle_Bend',(-.265,H-.02,0),.011,red,R)
    cyl('Handle_Tube_H',(-.265,H-.02,0),(-.17,H,-.0),.011,red,12,parent=R)
    cyl('Handle_Grip',(-.17,H,0),(-.06,H+.005,0),.016,blk,16,parent=R)
    # pump/motor saddle bracket on top of the tank
    box('Pump_Saddle',(.06,TY+TR+.012,0),(.24,.03,.16),red,R,.006)
    # twin-cylinder oil-free head: motor drum along x + two finned heads with red stripe + fan grilles
    MY=TY+TR+.095
    cyl('Motor_Drum',(-.04,MY,0),(.16,MY,0),.065,grey,24,parent=R)
    for i,sx in enumerate((-.06,.18)):
        box(f'Fan_Cover_{i}',(sx,MY,0),(.05,.19,.19),blk,R,.012)
    for i,sx in enumerate((-.01,.12)):
        box(f'Cylinder_Head_{i}',(sx,MY+.115,0),(.12,.08,.13),blk,R,.01)
        box(f'Head_Stripe_{i}',(sx,MY+.09,0),(.122,.01,.132),red,R)
        for k in range(4): box(f'Head_Fin_{i}_{k}',(sx,MY+.16,-.045+k*.03),(.12,.012,.008),blk,R)
    # pressure switch block + regulator + gauges + quick coupler (left front)
    PX=-.17
    cyl('Switch_Post',(PX,TY+TR-.01,.03),(PX,TY+TR+.09,.03),.012,red,12,parent=R)
    box('Pressure_Switch',(PX+.01,TY+TR+.14,.03),(.08,.10,.07),blk,R,.006)
    box('Switch_Warning_Label',(PX+.01,TY+TR+.14,.066),(.04,.05,.002),yel,R)
    cyl('Switch_Button',(PX+.01,TY+TR+.19,.03),(PX+.01,TY+TR+.205,.03),.009,red,12,parent=R)
    cyl('Regulator_Body',(PX-.06,TY+TR+.08,.06),(PX-.06,TY+TR+.125,.06),.018,red,16,parent=R)
    cyl('Regulator_Knob',(PX-.06,TY+TR+.125,.06),(PX-.06,TY+TR+.15,.06),.016,red,16,parent=R)
    cyl('Manifold',(PX-.10,TY+TR+.065,.06),(PX+.06,TY+TR+.065,.06),.010,chrome,12,parent=R)
    for i,gx in enumerate((PX-.11,PX+.06)):
        cyl(f'Gauge_{i}',(gx,TY+TR+.075,.07),(gx,TY+TR+.075,.095),.026,blk,20,parent=R)
        cyl(f'Gauge_Face_{i}',(gx,TY+TR+.075,.095),(gx,TY+TR+.075,.097),.022,wht,20,parent=R)
    cyl('Quick_Coupler_Out',(PX-.03,TY+TR+.065,.07),(PX-.03,TY+TR+.065,.12),.011,chrome,12,parent=R)
    cyl('Drain_Valve',(-.24,TY-.06,.08),(-.24,TY-.06,.11),.012,chrome,10,parent=R)
    export('compressor_fubag')

# ---------------- PLIERS 180 mm (frame = game: axis +z to jaws, opening plane x, pivot at z=.045) ----------------
def pliers():
    reset(); R=root('Pliers_Combination_180')
    st=M('Steel_Forged',(0.35,0.36,0.38),.35,1.); red=M('Handle_Red',(0.8,0.05,0.04),.6); blk=M('Handle_Black',(0.03,0.03,0.03),.7); br=M('Steel_Bright',(0.75,0.76,0.78),.25,1.)
    for sx,nm in((-1,'Left'),(1,'Right')):
        pts=[(sx*.005,0,.04),(sx*.008,0,.01),(sx*.012,0,-.03),(sx*.015,0,-.07),(sx*.0155,0,-.095)]
        for i in range(len(pts)-1):
            mat=red if i<2 else blk if i==3 else red
            cyl(f'Handle_{nm}_{i}',pts[i],pts[i+1],.0068 if i<3 else .0075,mat,12,r2=(.0075 if i<3 else .0062),parent=R)
        sph(f'Handle_{nm}_End',pts[-1],.0062,blk,R)
    box('Joint_Plate',(0,0,.047),(.026,.009,.024),st,R,.002)
    cyl('Pivot_Rivet',(0,-.0055,.047),(0,.0055,.047),.0055,br,16,parent=R)
    # jaws: flat-nose with serrations + cutter
    box('Jaw_Left',(-.0045,0,.077),(.009,.008,.042),st,R,.0015,taper=(.6,.8))
    box('Jaw_Right',(.0045,0,.077),(.009,.008,.042),st,R,.0015,taper=(.6,.8))
    for k in range(6): box(f'Serration_{k}',(0,0,.066+k*.005),(.0012,.0085,.0012),br,R)
    box('Cutter_Edge',(0,0,.058),(.0015,.009,.008),br,R)
    export('pliers_180')

# ---------------- SCREWDRIVER PH2 x 100, handle 110 (frame: +z to tip, handle z -.055..+.055) ----------------
def screwdriver():
    reset(); R=root('Screwdriver_PH2')
    yel=M('Handle_Yellow',(0.95,0.68,0.02),.5); blk=M('Handle_Black_Soft',(0.03,0.03,0.03),.8); ch=M('Chrome_Shaft',(0.85,0.86,0.88),.15,1.)
    prof=[(-.055,.012),(-.05,.0155),(-.03,.0165),(-.005,.0158),(.02,.0145),(.04,.0125),(.05,.0095),(.056,.007)]
    for i in range(len(prof)-1):
        z0,r0=prof[i]; z1,r1=prof[i+1]
        cyl(f'Handle_{i}',(0,0,z0),(0,0,z1),r0,yel if i in(0,4,5,6) else blk,20,r2=r1,parent=R)
    for k in range(6):
        a=k*math.pi/3; box(f'Grip_Rib_{k}',(math.cos(a)*.0158,math.sin(a)*.0158,-.017),(.004,.004,.05),blk,R,.001)
    cyl('Shaft',(0,0,.056),(0,0,.148),.003,ch,10,parent=R)
    cyl('Tip_PH2',(0,0,.148),(0,0,.158),.003,ch,4,r2=.0006,parent=R)
    export('screwdriver_ph2')

# ---------------- HAMMER 500 g, fibreglass handle 300 (frame: handle along +z, head at z=.16 along y) ----------------
def hammer():
    reset(); R=root('Hammer_Claw_500g')
    st=M('Steel_Head',(0.25,0.26,0.28),.35,1.); face=M('Steel_Face',(0.7,0.71,0.73),.25,1.); yel=M('Fibreglass_Yellow',(0.95,0.7,0.02),.5); blk=M('Grip_Rubber',(0.03,0.03,0.03),.85)
    cyl('Handle_Grip',(0,0,-.17),(0,0,-.03),.0165,blk,18,r2=.0145,parent=R)
    sph('Grip_End',(0,0,-.17),.0168,blk,R,(1,1,.5))
    cyl('Handle_Core',(0,0,-.03),(0,0,.145),.0125,yel,16,r2=.0115,parent=R)
    # head: neck block + round striking face (-y), claw (+y) curving back toward -z
    box('Head_Eye',(0,.005,.16),(.026,.05,.03),st,R,.003)
    cyl('Head_Neck',(0,-.02,.16),(0,-.042,.16),.013,st,20,parent=R)
    cyl('Strike_Face',(0,-.042,.16),(0,-.05,.16),.0145,face,20,parent=R)
    for sx in(-1,1):
        p=[(sx*.006,.03,.16),(sx*.0065,.05,.155),(sx*.007,.065,.143),(sx*.007,.074,.128)]
        for i in range(3): cyl(f'Claw_{"L" if sx<0 else "R"}_{i}',p[i],p[i+1],.007-.0015*i,st,10,r2=.0055-.0015*i,parent=R)
    export('hammer_500g')

which=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
for f in (compressor,pliers,screwdriver,hammer):
    if 'all' in which or f.__name__ in which: f()
