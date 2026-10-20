import time,json
from playwright.sync_api import sync_playwright
O='/workspace/warehouse_game/'; R={}
with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1024,'height':576}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('window.__wbParts&&window.__wbParts().length>0&&window.__hammerGLB&&window.__cmpReady',timeout=90000); time.sleep(1.5)
  E=pg.evaluate; S=lambda id:E(f"__bodyState('{id}')")
  def settle(id,t=8):
    for _ in range(int(t/.25)):
      st=S(id)
      if st['asleep']: return st
      time.sleep(.25)
    return S(id)
  hideT="document.getElementById('toast').style.display='none'"
  # close-up of the bench items
  E("__look(0);window.demoCamY=1.25"); E("__aimAt('bench')"); E("__walk(.55);__look(-.75)"); time.sleep(2.5); E(hideT); pg.screenshot(path='/workspace/wb/phys_overview.png')
  E("window.demoCamY=null")
  # 1) drop hammer on the bench (aim at bench, real dropW)
  E("__aimAt('hammer')"); time.sleep(1.2); R['aim_h']=E('[__wstate().wAim,__wstate().take]'); pg.keyboard.press('e'); time.sleep(.6); R['hold1']=E('__wstate().holdingW')
  E("__aimAt('bench')"); time.sleep(.8); pg.keyboard.press('g'); R['bench']=settle('hammer')
  # 2) edge: drop the screwdriver just beyond the front edge with forward speed -> falls to the floor
  E("__aimAt('screwdriver')"); time.sleep(1.2); pg.keyboard.press('e'); time.sleep(.6); E("__walk(-.4)"); time.sleep(2)
  R['edge']=None; E("(()=>{const d=__benchDims(); return __dropAt(d.x+.3,d.top,d.z+d.D/2+.07,'screwdriver',true)})()"); R['edge']=settle('screwdriver')
  # 3) floor: drop the marker on the floor
  E("__aimAt('marker')"); time.sleep(.8); pg.keyboard.press('e'); time.sleep(.6); E("__look(-1.1)"); time.sleep(.6); pg.keyboard.press('g'); R['floor']=settle('marker')
  R['marker_pick']=None; E("__aimAt('floorTool','marker')") if False else None
  # 4) container: open Drawer_1, put pliers inside, close, open, still inside and pickable
  E("__aimAt('pliers')"); time.sleep(.8); pg.keyboard.press('e'); time.sleep(.6)
  E("__aimAt('wb:Drawer_1')"); time.sleep(.8); E("__wbToggle('Drawer_1')"); time.sleep(2.5)
  E("__aimAt('wb:Drawer_1')"); time.sleep(1.2); R['aim_drawer']=E('__wstate().wAim'); pg.keyboard.press('g'); R['in_drawer']=settle('pliers')
  E(hideT); pg.screenshot(path=O+'game_v71_item_in_drawer.png')
  E("__wbToggle('Drawer_1')"); time.sleep(2.5); R['closed']=S('pliers')
  E("__wbToggle('Drawer_1')"); time.sleep(2.5); R['reopened']=S('pliers')
  E("__aimAt('pliers')"); time.sleep(1.2); st=E('__wstate()'); R['aim_pick']=[st['wAim'],st['take']]
  pg.keyboard.press('e'); time.sleep(.6); R['picked']=E('__wstate().holdingW')
  # 5) riveter + hose: in hand, carried away, then dropped on the floor
  pg.keyboard.press('g'); time.sleep(.5)
  E("__aimAt('riveter')"); time.sleep(.8); pg.keyboard.press('e'); time.sleep(.6); R['riv']=E('__wstate().holdingW')
  E("__walk(-1.8);__look(-.45,.6)"); time.sleep(3); R['hose_hand']=E('__hoseInfo()'); E(hideT); pg.screenshot(path=O+'game_v71_hose_in_hand.png')
  E("__look(-1.0)"); time.sleep(.5); pg.keyboard.press('g'); R['riv_floor']=settle('riveter'); time.sleep(2); E("__look(-.6,-.6)"); time.sleep(1.5); E(hideT); pg.screenshot(path=O+'game_v71_hose_riveter_dropped.png')
  # put it back on the bench and shoot the coil lying near the outlet
  E("__aimAt('riveter')"); time.sleep(.8); pg.keyboard.press('e'); time.sleep(.6); E("__aimAt('bench')"); time.sleep(.8); pg.keyboard.press('g'); settle('riveter'); time.sleep(2.5)
  E("__aimAt('bench')"); E("__walk(-.4);__look(-.55,-.35)"); time.sleep(2); R['hose_bench']=E('__hoseInfo()'); E(hideT); pg.screenshot(path=O+'game_v71_hose_on_bench.png')
  # 5b) trestle snag: drop the riveter behind a trestle leg (leg between it and the outlet) -> pulled, stops at the leg
  E("__aimAt('riveter')"); time.sleep(1.2); pg.keyboard.press('e'); time.sleep(.6)
  R['snag_setup']=E("""(()=>{const legs=__goatLegs(); const A=__hoseInfo().anchor; let best=null; for(const [mn,mx] of legs){const c=[(mn[0]+mx[0])/2,(mn[2]+mx[2])/2]; const d=Math.hypot(A[0]-c[0],A[2]-c[1]); if(!best||d>best.d)best={c,d,mn,mx};} const dx=(A[0]-best.c[0])/best.d, dz=(A[2]-best.c[1])/best.d; const P=[best.c[0]-dx*.7,best.c[1]-dz*.7]; __dropAt(P[0],0,P[1],'riveter'); return {leg:best.c,P,anchorDist:best.d};})()""")
  time.sleep(9); st=S('riveter'); R['snag']=st; R['snag_tension']=E('__hoseTension()')
  E("(()=>{const r=__bodyState('riveter').pos; return 1})()"); E(f"__aimAt('goats')"); time.sleep(2); E(hideT); pg.screenshot(path=O+'game_v71_hose_snag_trestle.png')
  # 6) walk limit: hold riveter and walk away
  for _ in range(4):
    E("__aimAt('riveter')"); time.sleep(1.5); pg.keyboard.press('e'); time.sleep(.8)
    if E('__wstate().holdingW')=='riveter': break
  R['limit_hold']=E('__wstate().holdingW'); E("__look(0,Math.PI)"); pg.keyboard.down('w'); time.sleep(10); pg.keyboard.up('w'); time.sleep(.5)
  p=E('__wstate().pos'); R['limit']={'dist':E(f"Math.hypot({p[0]}-__hoseInfo().anchor[0],{p[1]}-__hoseInfo().anchor[2])"),'reach':E('__hoseReach()'),'toast':E("document.getElementById('toast').textContent"),'hose':E('__hoseInfo()')}
  E(hideT); pg.screenshot(path=O+'game_v71_hose_stretched.png')
  # 7) compressor + air line view
  E("__setHold(null)"); E("playerPos=null") if False else None
  E("__aimAt('bench')"); E("__walk(-2.5);__look(.05,-0.9)"); time.sleep(2.5); E(hideT); pg.screenshot(path=O+'game_v71_compressor_airline.png')
  # prompt label check
  E("__aimAt('wb:Drawer_2')"); time.sleep(1); st=E('__wstate()'); R['prompt']=[st['take'],st['aimLabel']]
  R['rivMax']=E('window.__rivMax'); R['errs']=errs
print(json.dumps(R,ensure_ascii=False,indent=0))
