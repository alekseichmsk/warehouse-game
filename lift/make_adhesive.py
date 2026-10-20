# v7.1 two-component tile adhesive kit. Build in GAME coords (Y up, +Z toward player), convert T(v)=(x,-z,y).
# Real dims: pail A 10 l (top D286 rim D296, bottom D258, H238), lid; pail B 2.5 l (top D196, bottom D176, H140), lid;
# hardener foil pouch 150x190 (0.9 kg); snap-off utility knife 18 mm (body 160x30x16, blade 18x0.5, 8 segments);
# corded drill mixer 1200 W (body ~300, D72 motor, pistol rear grip, side handle) + paddle whisk D120 x 600 (M14 shank).
import bpy, bmesh, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
def T(v): return (v[0],-v[2],v[1])
MATS={}
def mat(n,c,r=.6,m=0.):
    if n in MATS: return MATS[n]
    M=bpy.data.materials.new(n); M.use_nodes=True; b=M.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=m; MATS[n]=M; return M
def obj(name,verts,faces,M,parent=None,loc=(0,0,0)):
    me=bpy.data.meshes.new(name); me.from_pydata([T(v) for v in verts],[],faces); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(M)
    if parent: o.parent=parent
    o.location=T(loc); return o
def empty(name,parent=None,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(o); o.location=T(loc)
    if parent: o.parent=parent
    return o
def lathe(name,prof,M,n=40,parent=None,loc=(0,0,0),axis='y'):
    # prof: list of (r,y) ; revolve about y
    V=[];F=[]
    for i in range(n):
        a=2*math.pi*i/n
        for r,y in prof: V.append((r*math.cos(a),y,r*math.sin(a)) if axis=='y' else (y,r*math.cos(a),r*math.sin(a)))
    m=len(prof)
    for i in range(n):
        j=(i+1)%n
        for k in range(m-1): F.append((i*m+k,j*m+k,j*m+k+1,i*m+k+1))
    return obj(name,V,F,M,parent,loc)
def box(name,c,s,M,parent=None):
    x,y,z=c; a,b,d=[v/2 for v in s]
    V=[(x+i*a,y+j*b,z+k*d) for i in(-1,1) for j in(-1,1) for k in(-1,1)]
    F=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return obj(name,V,F,M,parent)
def tube(name,pts,r,M,parent=None,n=10):
    V=[];F=[]
    for i,p in enumerate(pts):
        p=Vector(p); d=(Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(i-1,0)])).normalized()
        u=d.orthogonal().normalized(); w=d.cross(u)
        for k in range(n):
            a=2*math.pi*k/n; V.append(tuple(p+r*(math.cos(a)*u+math.sin(a)*w)))
    for i in range(len(pts)-1):
        for k in range(n): F.append((i*n+k,i*n+(k+1)%n,(i+1)*n+(k+1)%n,(i+1)*n+k))
    return obj(name,V,F,M,parent)
WH=mat('PailWhite',(.92,.93,.94),.5); BL=mat('PailBlue',(.08,.25,.62),.45); OR=mat('PailOrange',(.95,.45,.08),.45)
GRY=mat('PasteGrey',(.50,.52,.53),.85); STL=mat('Steel',(.75,.77,.8),.3,.9); BLK=mat('Rubber',(.05,.05,.06),.8)
FOIL=mat('Foil',(.78,.78,.80),.25,.85); YEL=mat('KnifeYellow',(.98,.75,.05),.45); ZG=mat('DrillGreen',(.05,.45,.25),.45); DK=mat('DrillGrey',(.18,.19,.2),.6)
# ---------- pail A 10 l ----------
pa=empty('Pail_A')
lathe('Pail_A_Body',[(0,.003),(.129,.003),(.129,0),(.140,.200),(.143,.228),(.148,.230),(.148,.238),(.140,.238),(.137,.232),(.126,.010),(0,.010)],WH,48,pa)
lathe('Pail_A_Band',[(.1405,.150),(.1425,.190)],BL,48,pa)  # label band
for s in(-1,1): lathe('Pail_A_Ear%d'%(s>0),[(0,0),(.012,0),(.012,.012),(0,.012)],WH,12,pa,(s*.146,.205,0),axis='x')
pts=[(-.150,.205,0)]+[(.152*math.cos(a),.205+.11*math.sin(a),0) for a in [math.pi-i*math.pi/20 for i in range(21)]]+[(.150,.205,0)]
tube('Pail_A_Handle',[(math.copysign(.150,p[0]) if abs(p[0])>.148 else p[0],p[1],0) for p in pts],.0022,STL,pa,6)
lid=empty('Pail_A_Lid',None,(0,.238,0))
lathe('Pail_A_LidMesh',[(0,.006),(.142,.006),(.150,.004),(.151,-.012),(.146,-.012),(.146,0),(0,0)],BL,48,lid)
box('Pail_A_TearTab',(.152,-.006,0),(.012,.012,.03),BL,lid)
# ---------- pail B 2.5 l ----------
pb=empty('Pail_B')
lathe('Pail_B_Body',[(0,.003),(.088,.003),(.088,0),(.097,.130),(.100,.134),(.100,.140),(.094,.140),(.092,.134),(.084,.008),(0,.008)],WH,40,pb)
lathe('Pail_B_Band',[(.0955,.075),(.0975,.115)],OR,40,pb)
lidb=empty('Pail_B_Lid',None,(0,.140,0))
lathe('Pail_B_LidMesh',[(0,.005),(.096,.005),(.102,.003),(.103,-.010),(.098,-.010),(.098,0),(0,0)],OR,40,lidb)
# ---------- hardener foil pouch 150x190, flat (lies on XZ, top seal toward -z) ----------
bag=empty('Bag')
def pillow(name,x0,x1,z0,z1,th,M,par,nx=12,nz=12):
    V=[];F=[]
    for s in(1,-1):
        for i in range(nx+1):
            for k in range(nz+1):
                x=x0+(x1-x0)*i/nx; z=z0+(z1-z0)*k/nz
                ex=math.sin(math.pi*i/nx); ez=math.sin(math.pi*k/nz); V.append((x,s*th*(ex*ez)**.5+ (th+.0004 if s>0 else 0)*0,z))
    N=(nx+1)*(nz+1)
    for i in range(nx):
        for k in range(nz):
            a=i*(nz+1)+k; F.append((a,a+1,a+nz+2,a+nz+1)); F.append((N+a,N+a+nz+1,N+a+nz+2,N+a+1))
    return obj(name,V,F,M,par)
pillow('Bag_Body',-.075,.075,-.068,.095,.011,FOIL,bag)
top=empty('Bag_Top',bag,(0,0,-.080))
box('Bag_TopSeal',(0,0,0),(.150,.0012,.026),FOIL,top)
for i in range(15): box('Bag_Crimp%d'%i,(-.07+i*.01,.0008,0),(.004,.0004,.024),FOIL,top)
# ---------- snap-off knife 18 mm: origin at grip centre, blade toward +z ----------
kn=empty('Knife')
V=[];F=[]
box('Knife_Body',(0,0,0),(.030,.016,.160),YEL,kn); box('Knife_Grip',(0,-.0002,-.025),(.0305,.0165,.085),BLK,kn)
box('Knife_Rail',(0,.0085,.03),(.008,.002,.10),STL,kn); box('Knife_Nose',(0,0,.084),(.022,.010,.012),STL,kn)
sl=empty('Knife_Slider',kn,(0,.0095,.02)); box('Knife_SliderBtn',(0,0,0),(.012,.006,.018),BLK,sl)
bl=empty('Knife_Blade',kn,(0,0,.0))   # slides +z (extended: +0.03)
# blade: 18 x 0.5, segments 13 mm with snap lines, angled tip
bv=[(-.009,0,-.06),(.009,0,-.06),(.009,0,.085),(-.009,0,.098)]
bm=obj('Knife_BladeMesh',[(x,y+d,z) for d in(-.00025,.00025) for x,y,z in bv],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],STL,bl)
# ---------- drill mixer: origin at chuck nose; shaft down -y, body up ----------
mx=empty('Mixer')
lathe('Mixer_Chuck',[(0,0),(.016,0),(.022,.012),(.023,.055),(.020,.07),(0,.07)],DK,24,mx)
lathe('Mixer_Gear',[(0,.07),(.032,.07),(.036,.12),(.034,.13),(0,.13)],DK,24,mx)
lathe('Mixer_Motor',[(0,.13),(.036,.13),(.037,.26),(.033,.29),(0,.30)],ZG,24,mx)
for i in range(8): box('Mixer_Vent%d'%i,(.037*math.cos(i*.785),.27,.037*math.sin(i*.785)),(.006,.02,.006),BLK,mx)
# rear loop handle (D-grip) on top, toward +z (operator)
tube('Mixer_RearGrip',[(0,.29,0),(0,.36,.03),(0,.38,.10),(0,.33,.17),(0,.24,.17),(0,.20,.07)],.016,BLK,mx,12)
box('Mixer_Trigger',(0,.30,.165),(.012,.04,.012),DK,mx)
# side handle (two-hand) at the gear housing
tube('Mixer_SideGrip',[(.036,.10,0),(.12,.10,0),(.24,.10,0)],.016,BLK,mx,12)
cord=tube('Mixer_CordStub',[(0,.25,.17),(0,.22,.22),(0,.17,.25)],.006,BLK,mx,8)
pad=empty('Mixer_Paddle',mx,(0,0,0))
lathe('Mixer_Shaft',[(0,0),(.0055,0),(.0055,-.60),(0,-.60)],STL,12,pad)
lathe('Mixer_Hex',[(0,0),(.0075,0),(.0075,-.03),(0,-.03)],STL,6,pad)
# helix whisk D120: two counter-rotating helical ribbons, ring at bottom
for side,sg in(('L',1),('R',-1)):
    V=[];F=[]; N=24
    for i in range(N+1):
        t=i/N; a=sg*t*math.pi*1.4; y=-.60+t*.11
        for r in(.012,.060): V.append((r*math.cos(a+ (0 if sg>0 else math.pi)),y+ (.006 if r>.03 else 0),r*math.sin(a+(0 if sg>0 else math.pi))))
    for i in range(N): F.append((2*i,2*i+1,2*i+3,2*i+2))
    o=obj('Mixer_Blade'+side,V,F,STL,pad); m=o.modifiers.new('s','SOLIDIFY'); m.thickness=.0025
pts=[(.060*math.cos(a),-.60,.060*math.sin(a)) for a in [i*2*math.pi/24 for i in range(25)]]
tube('Mixer_Ring',pts,.0035,STL,pad,8)
for o in bpy.context.scene.objects:
    if o.type=='MESH':
        for m in o.modifiers: 
            bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=m.name)
# layout for preview render
pa.location=T((-.35,0,0)); lid.location=T((-.35,.238,0)); pb.location=T((.0,0,0)); lidb.location=T((0,.14,0))
bag.location=T((.25,0,.15)); kn.location=T((.42,.01,.15)); mx.location=T((.6,.62,0))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/lift/adhesive_kit.blend')
bpy.ops.export_scene.gltf(filepath='/workspace/lift/adhesive_kit.glb',export_format='GLB',export_yup=True,export_apply=True)
# render preview
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.view_settings.view_transform='Standard'; sc.render.resolution_x=1280; sc.render.resolution_y=800
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
cam.location=T((.15,1.0,1.55)); 
d=Vector(T((.12,.32,0)))-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); cam.data.lens=32
for p,e in(((2,3,4),900),((-3,2,3),400)):
    L=bpy.data.objects.new('L',bpy.data.lights.new('L','POINT')); L.data.energy=e; L.location=p; sc.collection.objects.link(L)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(.25,.27,.30,1)
sc.render.filepath='/workspace/lift/adhesive_render.png'; bpy.ops.render.render(write_still=True)
print('TRIS',sum(len(o.data.polygons) for o in sc.objects if o.type=='MESH'))
