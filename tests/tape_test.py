# v6.9 tape measure test: take the tape, hook on point A, stretch to B, read mm, release -> retracts. On the lift tray, the bench and the floor.
from playwright.sync_api import sync_playwright
import time,json,math
O='/workspace/warehouse_game/'; R={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!(window.__liftReady&&window.__camAt&&window.__tapeState)',timeout=90000); time.sleep(2)
  E=pg.evaluate; S=lambda:E('__wstate()')
  E("__aimAt('tape')"); time.sleep(1.2)
  for _ in range(4):
    if S().get('wAim')=='tape': break
    E("__aimAt('tape')"); time.sleep(.8)
  R['aim']=[S().get('wAim'),E("document.getElementById('aimLabel').textContent")]
  pg.keyboard.press('e'); time.sleep(.8); R['hold']=S().get('holdingW')
  R['btn']=E("document.getElementById('action').textContent")
  D=E('__liftDims()'); R['dims']=D; y=D['sheetY']
  def look(cx,cy,cz,tx,ty,tz,w=.9): E(f"__camAt({cx},{cy},{cz},{tx},{ty},{tz})"); time.sleep(w)
  def measure(name,P,A,B,shot=None):
    look(*P,*A); h=E('__tapeState().hit'); pg.keyboard.down(' '); time.sleep(.5)
    look(*P,*B,w=1.4); st=E('__tapeState()'); 
    if shot: pg.screenshot(path=O+shot)
    pg.keyboard.up(' '); time.sleep(.2); r1=E('__tapeState()'); time.sleep(2.5); r2=E('__tapeState()')
    exp=math.dist(st['A'],st['B'])*1000 if st['A'] and st['B'] else None
    R[name]={'mm':st['mm'],'A':st['A'],'B':st['B'],'expected_from_hits':round(exp) if exp else None,'targetA':A,'targetB':B,'errA_mm':round(math.dist(st['A'],A)*1000,1) if st['A'] else None,'errB_mm':round(math.dist(st['B'],B)*1000,1) if st['B'] else None,'onDuringHold':st['on'],'blade':st['blade'],'last':r1['last']['mm'] if r1['last'] else None,'retractedBlade':r2['blade'],'toast':E("document.getElementById('toast').textContent")}
  # 1) lift tray: length of the top sheet inside the rim (along x) from back rim to threshold riser
  x0,x1=D['min'][0],D['max'][0]; z=D['z']
  measure('tray_length',(D['x'],1.75,z+1.3),[x0+.05,y,z],[x1-.30,y,z],shot='game_v71_tape_in_use.png')
  # 2) tray width across (z)
  measure('tray_width',(D['x']+.6,1.7,z+1.2),[D['x']+.6,y,D['min'][2]+.05],[D['x']+.6,y,D['max'][2]-.05],shot='game_v71_tape_tray_width.png')
  # 3) on the workbench top
  bd=E('__benchDims()'); T=bd['top']
  measure('bench',(bd['x'],1.65,bd['z']+1.6),[bd['x']-.6,T,bd['z']+.85],[bd['x']+.4,T,bd['z']+.85],shot='game_v71_tape_bench.png')
  # 4) on the floor
  measure('floor',(0,1.6,3.0),[-1.0,0,1.8],[1.0,0,1.8])
  R['errs']=er
print(json.dumps(R,ensure_ascii=False,indent=1))
