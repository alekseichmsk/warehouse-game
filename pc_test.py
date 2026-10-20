# v7.5 PC mode test with real keyboard/mouse events (pointer lock emulated by ?plemu): HUD hidden, mouse-look, WASD, settings menu rebind, FOV,
# LMB hold tape measurement with edge snapping on a 300x300 tile (exact within 1 mm), Alt disables snap. Shield cycle: pc_test_cycle.py.
from playwright.sync_api import sync_playwright
import time,json,math,atexit
O='/workspace/warehouse_game/'; R={}; P='game_v75_'
atexit.register(lambda: print(json.dumps(R,ensure_ascii=False,indent=1)))
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&pc&plemu&cb={time.time()}'); pg.wait_for_function('!!(window.__wstate&&window.__pc&&window.__sawReady&&window.__tapeState)',timeout=90000); time.sleep(2)
  E=pg.evaluate; S=lambda:E('__wstate()'); PS=lambda:E('__pc.state()'); shot=lambda n:pg.screenshot(path=O+P+n+'.png')
  E("localStorage.removeItem('wg_pc')")
  st=PS(); R['hud']={'isPC':st['isPC'],'joy':st['joyVisible'],'btns':st['btnsVisible']}
  # mouse look (emulated pointer lock) + WASD + Shift run
  pg.mouse.move(640,400); E('window.__plLook=true'); y0=PS()['yaw']; pg.mouse.move(740,400,steps=5); time.sleep(.2); y1=PS()['yaw']; pg.mouse.move(640,400,steps=5); E('window.__plLook=false'); R['mouselook_dyaw']=round(y1-y0,3)
  p0=S()['pos']; pg.keyboard.down('KeyW'); time.sleep(.8); pg.keyboard.up('KeyW'); p1=S()['pos']; pg.keyboard.down('ShiftLeft'); pg.keyboard.down('KeyW'); time.sleep(.8); pg.keyboard.up('KeyW'); pg.keyboard.up('ShiftLeft'); p2=S()['pos']
  R['walk']=round(math.dist(p0[:2],p1[:2]),2); R['run']=round(math.dist(p1[:2],p2[:2]),2)
  tid=E("(()=>{const keep=__wstate().holdingW; const id=__mkTile(300,300); return id})()"); time.sleep(.3)
  for _ in range(5):
    E("__aimAt('saw')"); time.sleep(.9)
    if S().get('wAim')=='saw': break
  pg.keyboard.press('KeyE'); time.sleep(.6); ss=E('__sawState()'); R['tile_on_saw']=[ss['tile'],ss['tileDims'],ss['fence']]
  # aim at the tape -> prompt shows key hints
  for _ in range(5):
    E("__aimAt('tape')"); time.sleep(.9)
    if S().get('wAim')=='tape': break
  R['prompt']=PS()['prompt']; shot('pc_hud')
  # settings menu: rebind take E -> T
  pg.keyboard.press('Escape'); time.sleep(.4); R['menu_open']=PS()['menu']
  pg.click('#pcMenu .kb[data-a="take"][data-i="0"]'); time.sleep(.2); R['rebind_wait']=PS()['rebind']; shot('settings_rebind')
  pg.keyboard.press('KeyT'); time.sleep(.3); R['take_bind']=E("__pc.settings().binds.take")
  E("(()=>{const f=document.getElementById('pcFov'); f.value=80; f.dispatchEvent(new Event('input'));})()"); R['fov']=PS()['fov']
  pg.keyboard.press('Escape'); time.sleep(.3); R['menu_closed']=not PS()['menu']
  for _ in range(5):
    E("__aimAt('tape')"); time.sleep(.9)
    if S().get('wAim')=='tape': break
  pg.keyboard.press('KeyE'); time.sleep(.4); R['E_unbound_holding']=S()['holdingW']
  pg.keyboard.press('KeyT'); time.sleep(.5); R['T_take_holding']=S()['holdingW']; R['prompt_after_rebind']=PS()['prompt']
  # put a 300x300 tile on the saw table (known pose) and measure it with edge snap
  # (hold tape: drop it temporarily? -> keep tape in hand; tile created by hook goes straight onto the saw)
  E("(()=>{const h=__wstate().holdingW; return h})()")
  for _ in range(5):
    E("__aimAt('tape')"); time.sleep(.9)
    if S().get('wAim')=='tape': break
  R['tape_held']=S()['holdingW']
  f=ss['fence']/1000; zc=-4.55-f+.15+.07; y=.70+.009
  A=[-7.3-.15+.008,y,zc]; B=[-7.3+.15-.008,y,zc]; CAM=(-7.3,1.45,zc+.55)
  def look(T,w=1.0): E(f"__camAt({CAM[0]},{CAM[1]},{CAM[2]},{T[0]},{T[1]},{T[2]})"); time.sleep(w)
  def settle(T):
    t=list(T)
    for _ in range(8):
      look(t); h=E('__tapeState().hit')
      if not h: continue
      q=h['p']
      R.setdefault('hits',[]).append([h.get('obj'),[round(v,4) for v in q],E('window.__tapeSnap')])
      if math.dist(q,T)<.02 and E('window.__tapeSnap'): return q
      t=[t[i]+max(-.05,min(.05,T[i]-q[i])) for i in range(3)]
    return E('__tapeState().hit')
  def measure(alt=False):
    if alt: pg.keyboard.down('AltLeft')
    a=settle(A); pg.mouse.move(640,430); pg.mouse.down(); time.sleep(.4); bb=settle(B); time.sleep(.4); st=E('__tapeState()'); sn=E('window.__tapeSnap')
    shot_ok=None
    if not alt: shot('tape_edge_snap')
    pg.mouse.up(); time.sleep(.3); last=E('__tapeState()').get('last')
    if alt: pg.keyboard.up('AltLeft')
    return {'mm':st['mm'],'A':st['A'],'B':st['B'],'snapB':sn,'last':last,'on':st['on']}
  R['tape_snap']=measure(False); R['tape_alt']=measure(True); time.sleep(2.5)
  # reset bindings
  pg.keyboard.press('Escape'); time.sleep(.3); pg.click('#pcReset'); time.sleep(.3); R['reset_take']=E("__pc.settings().binds.take"); pg.keyboard.press('Escape'); time.sleep(.3)
  # mobile override keeps buttons
  pg2=b.new_page(viewport={'width':1280,'height':720}); pg2.goto(f'http://localhost:8765/index.html?mode=workshop&mobile&cb={time.time()}'); pg2.wait_for_function('!!window.__pc',timeout=90000); time.sleep(2)
  R['mobile_override']={k:pg2.evaluate('__pc.state()')[k] for k in ['isPC','joyVisible','btnsVisible']}
  R['errs']=er
# shield cycle with real mouse/keyboard (same driver as play_test, PC bindings)
import subprocess
out=subprocess.run(['python3','/workspace/pc_test_cycle.py'],capture_output=True,text=True,timeout=900).stdout
d=json.loads(out[out.index('{'):]); R['cycle']={'fails':d['fails'],'errs':d['errs'],'wIndex':d['final'].get('wIndex'),'shields_paid':[r['pay']['sum'] for r in json.loads(d['log'][-1])] if d['log'] and d['log'][-1].startswith('[') else None}
