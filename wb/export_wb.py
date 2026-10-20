import bpy, re, json, math, os
from mathutils import Vector, Matrix
sc=bpy.context.scene; O=bpy.data.objects; sc.frame_set(1)
EXC=re.compile(r"^(Floor|Wall|Back_Wall|Ceiling|Room_|Rack_|Sheet_|Rip_|Cross_|TrackSaw|Demo|Arrow_|Camera|CamTarget|Sun|Fill|Case_|Consumables|Wall_Socket|Tool_(Screwdriver_\d|Pliers_\d|Hammer_H|AirGun$|AirGun_N|TapeRoll$)|ToolShelf_(Drill|Grinder|Battery|Level)|Fastener_\d|Tray_.*_(Clamp_\d|TapeMeasure|Marker))")
SKIPC={'Room','SheetCutting','Annotations','Scene Collection'}
inc=[o for o in sc.objects if o.type in('MESH','CURVE') and not o.hide_render and 'Cutter' not in o.name and not EXC.match(o.name) and o.users_collection[0].name not in SKIPC]
ROOT_RE=re.compile(r"^(Drawer_\d|Drawer_Deep_Front|Drawer_Side_Left|Drawer_Side_Right|Drawer_Side_(Left|Right)_Latch_Bolt|Tray_(Left|Right)_Pivot)$")
def root_of(o):
    p=o; best=None
    while p:
        if ROOT_RE.match(p.name): best=best or p.name   # nearest movable ancestor
        p=p.parent
    return best or 'Static'
# motion metadata straight from fcurves (local channels), converted to world deltas
meta={}
for n in [o.name for o in O if ROOT_RE.match(o.name)]:
    r=O[n]; a=r.animation_data.action if r.animation_data else None
    if not a: continue
    loc=[0,0,0]; rot=[0,0,0]
    for fc in a.fcurves:
        vals=[k.co[1] for k in fc.keyframe_points]; v0=fc.evaluate(1)
        ext=max(vals,key=lambda v:abs(v-v0))-v0
        if fc.data_path=='location': loc[fc.array_index]=ext
        if fc.data_path=='rotation_euler': rot[fc.array_index]=ext
    pm=r.parent.matrix_world.to_3x3() if r.parent else Matrix.Identity(3)
    dl=pm@Vector(loc); 
    # rotation axis in world
    ax=None; ang=0
    for i in range(3):
        if abs(rot[i])>1e-3: v=Vector((0,0,0)); v[i]=1; ax=(pm@(r.matrix_basis.to_3x3()@v)).normalized(); ang=rot[i]
    piv=r.matrix_world.translation
    meta[n]=dict(dloc=list(dl),axis=list(ax) if ax else None,angle=ang,pivot=list(piv),parent=root_of(r.parent) if r.parent else 'Static')
print("META",json.dumps(meta),flush=True)
# bake evaluated meshes in world space, grouped by (root, material)
dg=bpy.context.evaluated_depsgraph_get(); buckets={}
for o in inc:
    ev=o.evaluated_get(dg)
    try: me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=False,depsgraph=dg)
    except Exception as e: continue
    if not me or len(me.polygons)==0: continue
    me.transform(o.matrix_world)
    mats=[s.material for s in o.material_slots] or [None]
    # split by material index
    for mi,m in enumerate(mats):
        key=(root_of(o),m.name if m else 'None')
        ob=bpy.data.objects.new(o.name+f"_m{mi}",me.copy() if len(mats)>1 else me); sc.collection.objects.link(ob)
        if len(mats)>1:
            import bmesh
            bm=bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=mi],context='FACES'); bm.to_mesh(ob.data); bm.free()
        ob.data.materials.clear(); ob.data.materials.append(m)
        buckets.setdefault(key,[]).append(ob)
print("BUCKETS",len(buckets),flush=True)
# hide/remove originals from export by moving merged into new collection
outc=bpy.data.collections.new("GameExport"); sc.collection.children.link(outc)
merged=[]
for (root,mname),L in buckets.items():
    L=[o for o in L if len(o.data.polygons)>0]
    if not L: continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in L: o.select_set(True)
    bpy.context.view_layer.objects.active=L[0]
    if len(L)>1: bpy.ops.object.join()
    ob=bpy.context.view_layer.objects.active; ob.name=f"{root}__{mname}"
    for c in list(ob.users_collection): c.objects.unlink(ob)
    outc.objects.link(ob); merged.append((root,ob))
def tris(ob): return sum(len(p.vertices)-2 for p in ob.data.polygons)
T=[tris(ob) for _,ob in merged]; B=int(os.environ.get("BUDGET","60000"))
lo,hi=0.0005,1.0
for _ in range(40):
    r=(lo+hi)/2; s=sum(min(t,max(min(t,150),t*r)) for t in T)
    if s>B: hi=r
    else: lo=r
r=lo; print("RATIO",r,"from",sum(T),flush=True)
for (root,ob),t in zip(merged,T):
    tgt=min(t,max(min(t,150),t*r))
    if tgt<t*0.98:
        bpy.context.view_layer.objects.active=ob; m=ob.modifiers.new("dec",'DECIMATE'); m.ratio=tgt/t; m.use_collapse_triangulate=True
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.ops.object.modifier_apply(modifier="dec")
# root empties for movable groups at their pivots
roots={}
for root,ob in merged:
    if root=='Static': continue
    if root not in roots:
        e=bpy.data.objects.new(root,None); outc.objects.link(e); e.location=Vector(meta.get(root,{}).get('pivot',(0,0,0))) if root in meta else O[root].matrix_world.translation; roots[root]=e
    ob.parent=roots[root]; ob.matrix_parent_inverse=Matrix.Translation(roots[root].location).inverted()
bpy.context.view_layer.update()
for root,e in roots.items():   # nest latch/drawer hierarchy
    par=meta.get(root,{}).get('parent')
    if par and par in roots: mw=e.matrix_world.copy(); e.parent=roots[par]; e.matrix_world=mw
for root,ob in merged:
    if root=='Static': ob.shade_smooth() if False else None
bpy.ops.object.select_all(action='DESELECT')
for o in outc.all_objects: o.select_set(True)
OUT=os.environ.get("OUTGLB","/workspace/wb/workbench.glb")
bpy.ops.export_scene.gltf(filepath=OUT,use_selection=True,export_format='GLB',export_apply=False,export_animations=False,export_draco_mesh_compression_enable=False,export_normals=True,export_texcoords=False,export_yup=True)
print("FINAL_TRIS",sum(tris(ob) for _,ob in merged),"GLB",os.path.getsize(OUT),flush=True)
json.dump(dict(meta=meta,ratio=r,tris_src=sum(T),tris=sum(tris(ob) for _,ob in merged),groups=sorted(roots)),open("/workspace/wb/workbench_meta.json","w"),indent=1)
bpy.ops.wm.save_as_mainfile(filepath="/workspace/wb/workbench_game.blend")
