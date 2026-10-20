# v7.2 tile laying tools. GAME coords (Y up), T(v)=(x,-z,y). Real dims (mm):
# flat steel trowel 280x120x0.7 + closed handle 120 (Ø30); notched trowel 280x120, square teeth 10x10 (pitch 20) on both long edges;
# rubber mallet: white non-marking head Ø60x110, handle Ø28x300; SVP (Russian "СВП клин"): clip 2 mm = base 50x30x1 + tab 20x36x2 with window 9x15,
# wedge 80x18 ramp 3->14 ribbed; SVP pliers 230 mm.
import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
def T(v): return (v[0],-v[2],v[1])
MATS={}
def mat(n,c,r=.6,m=0.):
    if n in MATS: return MATS[n]
    M=bpy.data.materials.new(n); M.use_nodes=True; b=M.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=m; MATS[n]=M; return M
def obj(name,V,F,M,parent=None):
    me=bpy.data.meshes.new(name); me.from_pydata([T(v) for v in V],[],F); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(M)
    if parent: o.parent=parent
    return o
def empty(name,parent=None,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(o); o.location=T(loc)
    if parent: o.parent=parent
    return o
def box(name,c,s,M,parent=None):
    x,y,z=c; a,b,d=[v/2 for v in s]
    V=[(x+i*a,y+j*b,z+k*d) for i in(-1,1) for j in(-1,1) for k in(-1,1)]
    return obj(name,V,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],M,parent)
def prism(name,poly,y0,y1,M,parent=None):  # extrude XZ polygon along y
    n=len(poly); V=[(x,y0,z) for x,z in poly]+[(x,y1,z) for x,z in poly]
    F=[tuple(range(n))[::-1],tuple(range(n,2*n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    return obj(name,V,F,M,parent)
def prismX(name,poly,x0,x1,M,parent=None):  # extrude YZ polygon along x
    n=len(poly); V=[(x0,y,z) for y,z in poly]+[(x1,y,z) for y,z in poly]
    F=[tuple(range(n)),tuple(range(n,2*n))[::-1]]+[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
    return obj(name,V,F,M,parent)
def cyl(name,a,b,r,M,parent=None,n=16):
    a=Vector(a); b=Vector(b); d=(b-a).normalized(); u=d.orthogonal().normalized(); w=d.cross(u); V=[];F=[]
    for p in (a,b):
        for k in range(n): t=2*math.pi*k/n; V.append(tuple(p+r*(math.cos(t)*u+math.sin(t)*w)))
    F=[(k,(k+1)%n,n+(k+1)%n,n+k) for k in range(n)]+[tuple(range(n))[::-1],tuple(range(n,2*n))]
    return obj(name,V,F,M,parent)
STL=mat('Steel',(.72,.74,.77),.3,.9); WOOD=mat('Wood',(.55,.35,.18),.7); BLK=mat('Black',(.06,.06,.07),.7); RUB=mat('RubberWhite',(.93,.93,.92),.8)
RED=mat('SvpRed',(.85,.12,.12),.5); BLU=mat('SvpBlue',(.12,.35,.85),.5); YEL=mat('Yellow',(.98,.78,.08),.5); GRN=mat('Green',(.1,.55,.25),.5)
# flat trowel: origin = blade bottom centre, blade on XZ (x=280 along +x? -> length along z for pushing), handle above
ft=empty('Trowel_Flat')
box('Trowel_Flat_Blade',(0,.00035,0),(.120,.0007,.280),STL,ft)
box('Trowel_Flat_Mount',(0,.008,-.01),(.012,.016,.16),STL,ft)
cyl('Trowel_Flat_Handle',(0,.045,-.07),(0,.045,.05),.015,WOOD,ft,14)
for z in(-.075,.055): box('Trowel_Flat_Post%d'%(z>0),(0,.025,z),(.008,.04,.008),STL,ft)
# notched trowel: blade 120x280 with square teeth 10x10 pitch 20 on both long edges (x = ±0.06)
nt=empty('Trowel_Notched')
poly=[]
N=14
for i in range(N):  # +x edge, teeth along z
    z0=-.14+i*.02; poly+= [(.05,z0),(.06,z0),(.06,z0+.01),(.05,z0+.01)]
poly+=[(.05,.14)]
for i in range(N):
    z0=.14-i*.02; poly+=[(-.05,z0),(-.06,z0),(-.06,z0-.01),(-.05,z0-.01)]
poly+=[(-.05,-.14)]
# polygon is non-convex -> build as quads strip: centre plate + teeth boxes (cleaner)
box('Trowel_Notched_Plate',(0,.00035,0),(.100,.0007,.280),STL,nt)
for s in(-1,1):
    for i in range(N): box('Trowel_Notched_Tooth%d_%d'%(s>0,i),(s*.055,.00035,-.135+i*.02),(.010,.0007,.010),STL,nt)
box('Trowel_Notched_Mount',(0,.008,-.01),(.012,.016,.16),STL,nt)
cyl('Trowel_Notched_Handle',(0,.045,-.07),(0,.045,.05),.015,GRN,nt,14)
for z in(-.075,.055): box('Trowel_Notched_Post%d'%(z>0),(0,.025,z),(.008,.04,.008),STL,nt)
# rubber mallet: origin = handle centre, handle along z, head at +z end (axis x)
ml=empty('Mallet')
cyl('Mallet_Handle',(0,0,-.15),(0,0,.15),.014,WOOD,ml,14)
cyl('Mallet_Head',(-.055,0,.18),(.055,0,.18),.030,RUB,ml,24)
cyl('Mallet_Ring',(-.004,0,.18),(.004,0,.18),.0305,BLK,ml,24)
# SVP clip 2 mm: origin = seam centre at tile bottom level (base under tiles, tab up through the seam). Tab plane = YZ? tab is 2 mm thick along x (seam across x)
cl=empty('SVP_Clip')
box('SVP_Clip_Base',(0,-.0005,0),(.030,.001,.050),RED,cl)
# tab: 2 mm (x) x 20 (z) x 36 (y), with window 15 high x 9 wide starting 12 mm above base
for (zc,zw) in((-.0075,.005),(.0075,.005)): box('SVP_Clip_Side%d'%(zc>0),(0,.018,zc),(.002,.036,zw),RED,cl)
box('SVP_Clip_Low',(0,.006,0),(.002,.012,.020),RED,cl); box('SVP_Clip_Top',(0,.0315,0),(.002,.009,.020),RED,cl)
# wedge: origin at its tip, slides along +x through the window; ramp height 3 -> 14 over 80 mm, 18 wide (z)
wd=empty('SVP_Wedge')
prismX('SVP_Wedge_Body',[(0,-.009),(0,.009),(.003,.009),(.003,-.009)],0,.001,BLU,wd)  # dummy small
o=obj('SVP_Wedge_Ramp',[(0,0,-.009),(.08,0,-.009),(.08,.014,-.009),(0,.003,-.009),(0,0,.009),(.08,0,.009),(.08,.014,.009),(0,.003,.009)],
      [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)],BLU,wd)
for i in range(7): x=.012+i*.01; h=.003+.011*x/.08; box('SVP_Wedge_Rib%d'%i,(x,h+.0008,0),(.002,.0016,.018),BLU,wd)
# SVP pliers 230 mm: origin = jaw tip, handles toward -z
pl=empty('SVP_Pliers')
box('SVP_Pliers_JawA',(0,.012,-.02),(.012,.010,.05),STL,pl); box('SVP_Pliers_JawB',(0,-.004,-.03),(.012,.008,.06),STL,pl)
cyl('SVP_Pliers_Pivot',(-.009,.004,-.05),(.009,.004,-.05),.008,STL,pl,14)
cyl('SVP_Pliers_HandleA',(0,.012,-.055),(0,.035,-.23),.009,YEL,pl,10); cyl('SVP_Pliers_HandleB',(0,-.004,-.055),(0,-.03,-.23),.009,BLK,pl,10)
# preview layout
ft.location=T((-.45,0,0)); nt.location=T((-.2,0,0)); ml.location=T((.08,.03,0)); cl.location=T((.28,.0,.05)); wd.location=T((.29,.012,.05)); pl.location=T((.45,.015,.08))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/lift/laying_tools.blend')
ft.location=nt.location=ml.location=cl.location=wd.location=pl.location=(0,0,0)
bpy.ops.export_scene.gltf(filepath='/workspace/lift/laying_tools.glb',export_format='GLB',export_yup=True,export_apply=True)
ft.location=T((-.45,0,0)); nt.location=T((-.2,0,0)); ml.location=T((.08,.03,0)); cl.location=T((.28,.0,.05)); wd.location=T((.29,.012,.05)); pl.location=T((.45,.015,.08))
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.view_settings.view_transform='Standard'; sc.render.resolution_x=1280; sc.render.resolution_y=720
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
cam.location=T((0,.75,.75)); d=Vector(T((0,0,0)))-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); cam.data.lens=28
for p,e in(((2,3,4),900),((-3,2,3),400)):
    L=bpy.data.objects.new('L',bpy.data.lights.new('L','POINT')); L.data.energy=e; L.location=p; sc.collection.objects.link(L)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(.25,.27,.30,1)
sc.render.filepath='/workspace/lift/laying_render.png'; bpy.ops.render.render(write_still=True)
print('TRIS',sum(len(o.data.polygons) for o in sc.objects if o.type=='MESH'))
