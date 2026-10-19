import numpy as np, json, math
from skimage import measure
def V(*a): return np.array(a,float)
F={'index':(V(-.029,0,.086),[.043,.025,.021],.0094,-5),'middle':(V(-.009,0,.090),[.047,.029,.022],.0097,-1),
   'ring':(V(.0105,0,.087),[.044,.027,.021],.0092,3),'little':(V(.0285,0,.078),[.034,.020,.019],.0080,8)}
chains={}; rads={}
for n,(b,L,r,ang) in F.items():
    d=V(math.sin(math.radians(ang)),0,math.cos(math.radians(ang))); p=b.copy(); pts=[p.copy()]
    for l in L:
        d=d+V(0,.06,0); d/=np.linalg.norm(d); p=p+d*l; pts.append(p.copy())
    chains[n]=pts; rads[n]=[r,r*.9,r*.82,r*.72]
chains['thumb']=[V(-.043,.014,.040),V(-.059,.021,.064),V(-.069,.025,.086),V(-.074,.026,.104)]; rads['thumb']=[.0128,.0114,.0106,.0088]
tmeta=(V(-.017,.006,.006),V(-.043,.014,.040),.018,.0135)
x=np.arange(-.10,.065,.0011); y=np.arange(-.035,.045,.0011); z=np.arange(-.10,.2,.0011)
X,Y,Z=np.meshgrid(x,y,z,indexing='ij'); P=np.stack([X,Y,Z],-1)
def cone(a,b,r1,r2):
    ba=b-a; pa=P-a; h=np.clip((pa@ba)/(ba@ba),0,1); d=np.linalg.norm(pa-h[...,None]*ba,axis=-1); return d-(r1+(r2-r1)*h)
def ell(c,r): q=(P-c)/r; k=np.linalg.norm(q,axis=-1); return (k-1)*min(r)
def rbox(c,hs,rr): q=np.abs(P-c)-hs; return np.linalg.norm(np.maximum(q,0),axis=-1)+np.minimum(np.max(q,axis=-1),0)-rr
def smin(a,b,k): h=np.clip(.5+.5*(b-a)/k,0,1); return b*(1-h)+a*h-k*h*(1-h)
# palm (slightly wider toward knuckles), wrist, forearm (oval)
palm=rbox(V(0,.0,.049),V(.027,.0015,.031),.0135)
palm=smin(palm,ell(V(0,0,.03),V(.034,.0135,.035)),.01)
palm=smin(palm,rbox(V(-.002,0,.078),V(.030,.001,.006),.0125),.01)
fore=cone(V(0,0,-.10),V(0,0,-.004),.0235,.0215); 
Ps=P.copy(); P[...,1]*=1.45; wrist=ell(V(0,0,.004),V(.027,.017,.02)); fore=cone(V(0,0,-.10),V(0,0,.0),.026,.024); P[...]=Ps
D=smin(palm,smin(fore,wrist,.012),.014)
D=smin(D,ell(V(-.023,.010,.028),V(.021,.0125,.028)),.012)   # thenar
D=smin(D,ell(V(.023,.007,.038),V(.013,.008,.028)),.010)    # hypothenar
# thumb metacarpal + chain
D=smin(D,cone(*tmeta),.012)
for n,pts in chains.items():
    r=rads[n]; fd=None
    for i in range(3):
        c=cone(pts[i],pts[i+1],r[i],r[i+1]); fd=c if fd is None else smin(fd,c,.003)
        if i<2: fd=smin(fd,ell(pts[i+1]+V(0,-.001,0),V(r[i+1]*.97,r[i+1]*.9,r[i+1]*.9)),.004) # joint, no band
    a,b=pts[2],pts[3]; dd=(b-a)/np.linalg.norm(b-a)
    fd=smin(fd,ell(a+(b-a)*.55+V(0,r[2]*.32,0),V(r[2]*.72,r[2]*.62,np.linalg.norm(b-a)*.42)),.003) # soft pad
    if n!='thumb': fd=smin(fd,ell(pts[0]+V(0,-.004,-.002),V(r[0]*.9,r[0]*.7,r[0]*.9)),.004) # MCP knuckle
    D=smin(D,fd,.007 if n!='thumb' else .006)
vs,fs,_,_=measure.marching_cubes(D,0,spacing=(.0011,.0011,.0011)); vs+=V(x[0],y[0],z[0])
np.savez('/workspace/hand/hand_sdf.npz',v=vs,f=fs)
json.dump({'chains':{k:[list(map(float,p)) for p in v] for k,v in chains.items()},'rads':rads,'tmeta':[list(map(float,tmeta[0])),list(map(float,tmeta[1]))]},open('/workspace/hand/chains.json','w'))
print(len(vs),len(fs))
