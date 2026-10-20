# v7.2 tile laying test (order 1: 1000x1250, tiles 300x300): trowel scoop -> dabs -> notched trowel comb (coverage) -> place 4 tiles (snap/nudge)
# -> SVP clips + wedges + pliers -> mallet levelling -> quality. Also: order 3 plan + saw feasibility.
from playwright.sync_api import sync_playwright
import time,json,sys
O='/workspace/warehouse_game/'; R={}; P='game_v72_'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required'])
  pg=b.new_page(viewport={'width':1280,'height':720}); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&liftorder=1&cb={time.time()}'); pg.wait_for_function('!!(window.__layReady&&window.__adhReady&&window.__layState)',timeout=90000); time.sleep(2)
  E=pg.evaluate; L=lambda:E('__layState()'); shot=lambda n:pg.screenshot(path=O+P+n+'.png')
  def toast(): return E("document.getElementById('toast').textContent")
  def stand_take(id):
    for _ in range(5):
      E(f"__layStandAim('{id}')"); time.sleep(.8)
      if L()['aim']==id: break
    pg.keyboard.press('e'); time.sleep(.5); return L()['holding']
  def stand_put():
    for _ in range(5):
      E("__layStandAim('stand')"); time.sleep(.8)
      if L()['aim']=='layStand' or L()['aim'] in ('trowel','comb','mallet','svpPliers','svpClips','svpWedges'): break
    h=L()['holding']; 
    if L()['aim']!='layStand': E("__dropW()"); time.sleep(.5); return 'dropped'
    pg.keyboard.press('e'); time.sleep(.4); return L()['holding']
  def aimT(x,z,want_hit=True):
    tx,tz=x,z
    for _ in range(3):
      E(f"__layAim({tx},{tz})"); time.sleep(.45); h=L()['hit']
      if not h: break
      ex,ez=x-h[0],z-h[1]
      if abs(ex)<.0015 and abs(ez)<.0015: break
      tx+=ex; tz+=ez
  st=L(); R['slots']=[(s['id'],s['w'],s['h'],s['need'],s['feasible']) for s in st['slots']]
  S={s['id']:s for s in st['slots']}; blk=['s1_1','s2_1','s1_2','s2_2']; X0=S['s1_1']['cx']-.15; X1=S['s2_2']['cx']+.15; Z0=S['s1_1']['cz']-.15; Z1=S['s2_2']['cz']+.15
  E("__adhQuick()"); time.sleep(.5)
  E("__camAt(-4.0,1.35,-5.95,-4.0,.75,-5.15)"); time.sleep(1); shot('lay_tools_stand')
  R['take_trowel']=stand_take('trowel')
  for k in range(2):
    for _ in range(5):
      E("__adhAim('pailA',[0,0,0])"); time.sleep(.9)
      if L()['aim']=='pailA': break
    pg.keyboard.press('e'); time.sleep(.4); R.setdefault('scoop',[]).append([L()['load'],L()['kg']])
    for zz in ([Z0+.1,Z0+.3,Z0+.5] if True else []):
      xx=X0+.08 if k==0 else X0+.35
      for _ in range(3):
        aimT(xx,zz)
        if L()['hit']: break
      pg.keyboard.press(' '); time.sleep(.35)
  R['dabs']=[L()['dabs'],L()['load'],toast()]
  E(f"__camAt({-4.3+X0+.3},1.25,{-3.6+Z0-.55},{-4.3+X0+.3},.76,{-3.6+Z0+.3})"); time.sleep(1.2); shot('lay_dabs')
  R['put_trowel']=stand_put(); R['take_comb']=stand_take('comb')
  for zz in [Z0+.1,Z0+.3,Z0+.5]:
    aimT(X0-.03,zz); pg.keyboard.down(' ')
    x=X0-.03
    while x<X1+.06: x+=.012; E(f"__layAim({x},{zz-.029})"); time.sleep(.05)
    pg.keyboard.up(' '); time.sleep(.3)
  st=L()['stats']; R['comb']={'bed':st['bedCoverage'],'dabs_left':L()['dabs']}
  # coverage of the 4 block slots
  E(f"__camAt({-4.3+X0+.3},1.25,{-3.6+Z0-.55},{-4.3+X0+.3},.76,{-3.6+Z0+.3})"); time.sleep(1.2); shot('lay_comb_coverage')
  E("__layCmd('map')"); time.sleep(.6); shot('lay_comb_ribs'); E("__layCmd('map')")
  R['put_comb']=stand_put()
  # tiles: three near-perfect, one 8 mm off then nudged
  offs={'s1_1':(.002,.001),'s2_1':(-.001,.002),'s1_2':(.0,-.003),'s2_2':(.008,0)}
  for sid in blk:
    tid=E("__mkTile(300,300)"); time.sleep(.3); s=S[sid]; ox,oz=offs[sid]
    aimT(s['cx']+ox,s['cz']+oz); time.sleep(.3); st=L(); 
    if sid=='s2_2': E(f"__camAt({-4.3+s['cx']},1.2,{-3.6+s['cz']-.6},{-4.3+s['cx']},.77,{-3.6+s['cz']})"); time.sleep(1); shot('lay_tile_ghost_outline'); aimT(s['cx']+ox,s['cz']+oz); time.sleep(.3)
    R.setdefault('target',[]).append([sid,st['target'],st['take']])
    pg.keyboard.press('e'); time.sleep(.5); R.setdefault('place',[]).append([sid,toast()])
  st=L(); R['placed']={k:[v['slot'],v['misIn'],v['snapped'],v['cov'],v['dh']] for k,v in st['placed'].items()}
  # nudge the 8 mm tile (last placed is s2_1, so nudge must target it: re-pick s1_1 tile? LAY.last is the last placed) -> place s1_1 last instead
  un=[k for k,v in st['placed'].items() if not v['snapped']]
  R['unsnapped']=un
  if un:
    # re-pick it and place again with an offset, then nudge with the panel buttons
    tid=un[0]; v=st['placed'][tid]; s=S[v['slot']]
    for _ in range(5):
      aimT(v['x'],v['z']); time.sleep(.3)
      if L()['aim']==tid: break
    pg.keyboard.press('e'); time.sleep(.4); aimT(s['cx']+.008,s['cz']); pg.keyboard.press('e'); time.sleep(.4)
    aimT(s['cx'],s['cz'])
    for _ in range(3): pg.click('#layPanel button[data-l="L"]'); time.sleep(.15)
    R['nudge']=[toast(),L()['placed'][tid]['snapped']]
  # a cut piece 300x192.9 (ЗУБР fence 194 -> 194-1.1) for the 300x193 edge slot s1_0 (no adhesive there -> low coverage shown)
  E("__mkTile(300,192.9)"); s=S['s1_0']; aimT(s['cx'],s['cz']); time.sleep(.3); R['cut_piece_target']=L()['target']; pg.keyboard.press('e'); time.sleep(.5); R['cut_piece']=toast()
  E(f"__camAt({-4.3+X0+.3},1.15,{-3.6+Z0-.45},{-4.3+X0+.3},.77,{-3.6+Z0+.3})"); time.sleep(1.2); shot('lay_tiles_placed')
  st=L(); R['joints']=[(j['axis'],j['gap'],len(j['pts']),j['lip']) for j in st['joints']]; R['before_svp']={k:st['stats'][k] for k in ['seamDevMm','lipMaxMm','coverage','Q']}
  # SVP clips
  R['take_clips']=stand_take('svpClips')
  for j in st['joints']:
    for q in j['pts']: aimT(q[0],q[1]); pg.keyboard.press(' '); time.sleep(.35)
  R['clips']=L()['stats']['clips']; R['put_clips']=stand_put()
  R['take_wedges']=stand_take('svpWedges')
  for c in L()['clipsList']: aimT(c['x'],c['z']); pg.keyboard.press(' '); time.sleep(.35)
  R['wedges']=sum(1 for c in L()['clipsList'] if c['wedge']); R['put_wedges']=stand_put()
  E(f"__camAt({-4.3+X0+.3},1.05,{-3.6+Z0-.3},{-4.3+X0+.3},.78,{-3.6+Z0+.3})"); time.sleep(1.2); shot('lay_svp_clips_wedges')
  # mallet levelling
  R['take_mallet']=stand_take('mallet'); taps=0
  for it in range(40):
    st=L(); pl=st['placed']; hi=max(pl,key=lambda k:pl[k]['dh']-pl[k]['dhMin']); v=pl[hi]
    if v['dh']-v['dhMin']<.05: break
    aimT(v['x'],v['z']); time.sleep(.2); pg.keyboard.press(' '); time.sleep(.3); taps+=1
    if it==2: E(f"__layAim({v['x']},{v['z']})"); time.sleep(.5); R['mallet_indicator']=L()['aimTxt']; shot('lay_mallet_indicator')
  st=L(); R['after_mallet']={'taps':taps,'lipMax':st['stats']['lipMaxMm'],'dh':{k:[v['dh'],v['dhMin']] for k,v in st['placed'].items()}}; R['put_mallet']=stand_put()
  R['take_pliers']=stand_take('svpPliers')
  for c in L()['clipsList']:
    aimT(c['x'],c['z']); pg.keyboard.down(' '); time.sleep(1.6); pg.keyboard.up(' '); time.sleep(.2)
  st=L(); R['tight']=[c['tight'] for c in st['clipsList']]; R['final']=st['stats']
  E(f"__camAt({-4.3+X0+.3},1.15,{-3.6+Z0-.45},{-4.3+X0+.3},.77,{-3.6+Z0+.3})"); time.sleep(1.2); shot('lay_final_quality')
  R['put_pliers']=stand_put()
  # physics: drop a tile onto the laid floor -> lands on tile surface; plan for order 3 (1200x600)
  tid=E("__mkTile(300,300)"); aimT(S['s3_1']['cx'],S['s3_1']['cz']); E("__dropW()"); time.sleep(3.5); R['drop_on_tray']=[toast(), E(f"__layState().placed") and None]
  E("__liftOrder(3)"); time.sleep(1.5); st=L(); R['order3_slots']=[(s['id'],s['w'],s['h'],s['need'],s['feasible']) for s in st['slots']]
  E("__liftOrder(1)"); time.sleep(1)
  R['errs']=er
  print(json.dumps(R,ensure_ascii=False,indent=0))
  b.close()
