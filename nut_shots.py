from playwright.sync_api import sync_playwright
import time,json
O='/workspace/warehouse_game/'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__setupRivet&&window.__camAt&&window.__rivState)',timeout=90000); time.sleep(2)
  E=pg.evaluate
  E("__camNear(.004)"); E("__setupRivet('shield')"); time.sleep(1); E("__rivState(1,'aim')"); E("__rivState(2,'done')"); E("__rivState(3,'done')")
  S=E("[0,1,2,3,4,5,6].map(i=>__rivSurf(i))"); print(json.dumps(S)[:400])
  def cam(i,side,dist,lat=.0,up=.03,name=''):
    s,n=S[i][side]['s'],S[i][side]['n']
    c=[s[0]+n[0]*dist+lat,s[1]+n[1]*dist+up,s[2]+n[2]*dist]
    E(f"__camAt({c[0]},{c[1]},{c[2]},{s[0]},{s[1]},{s[2]})"); time.sleep(2.5); pg.screenshot(path=O+name)
  # front: hole (1) next to inserted nut (0) and set nut (2)
  s0=S[1][0]['s']; n0=S[1][0]['n']
  E(f"__camAt({s0[0]+n0[0]*.22},{s0[1]+.06},{s0[2]+n0[2]*.22},{s0[0]},{s0[1]},{s0[2]})"); time.sleep(2.5); pg.screenshot(path=O+'game_v68_nut_holes_front.png')
  cam(1,0,.032,lat=.012,up=.012,name='game_v68_nut_hole_before.png')
  cam(0,0,.03,lat=.012,up=.012,name='game_v68_nut_inserted.png')
  cam(2,1,.035,lat=.014,up=.014,name='game_v68_nut_set_back_bulge.png')
  E("__camNear(.05)")
  # riveter on nut: player view, rivet 4 is 'in'
  E("__rivState(4,'in')"); E("__aimAt('rivet',4)"); time.sleep(1.5)
  for _ in range(5):
    if E('__wstate().wAim')=='rivet': break
    E("__aimAt('rivet',4)"); time.sleep(.8)
  E("document.getElementById('action').click()"); time.sleep(.3)
  s4=S[4][0]['s']; n4=S[4][0]['n']
  E(f"__camAt({s4[0]+n4[0]*.30+.22},{s4[1]+.12},{s4[2]+n4[2]*.30},{s4[0]},{s4[1]},{s4[2]})")
  ph=None
  for _ in range(80):
    time.sleep(.1); ph=E('window.__nutPhase')
    if ph=='thread-on': time.sleep(.3); pg.screenshot(path=O+'game_v68_riveter_on_nut.png'); break
  for _ in range(80):
    time.sleep(.1); ph=E('window.__nutPhase')
    if ph=='unscrew': pg.screenshot(path=O+'game_v68_riveter_unscrew.png'); break
  time.sleep(6); print(E('__nutInfo()'), er)
