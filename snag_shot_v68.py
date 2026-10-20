import time,json
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); E=pg.evaluate
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__hammerGLB&&window.__camAt)',timeout=90000); time.sleep(1.5)
  E("window.noGlow=true"); E("__aimAt('riveter')"); time.sleep(1.5); pg.keyboard.press('e'); time.sleep(1); print('held',E('__wstate().holdingW'),E('__hoseInfo()'))
  print(E("""(()=>{const legs=__goatLegs(); const A=__hoseInfo().anchor; let best=null; for(const [mn,mx] of legs){const c=[(mn[0]+mx[0])/2,(mn[2]+mx[2])/2]; const d=Math.hypot(A[0]-c[0],A[2]-c[1]); if(!best||d>best.d)best={c,d};} const dx=(A[0]-best.c[0])/best.d, dz=(A[2]-best.c[1])/best.d; __dropAt(best.c[0]-dx*.7,0,best.c[1]-dz*.7,'riveter'); return 1})()"""))
  for i in range(8): time.sleep(.4); print(E("__bodyState('riveter')"), E('__hoseTension()'))
  time.sleep(6); r=E("__bodyState('riveter')"); print(r)
  x,_,z=r['pos']; E(f"__camAt({x}-1.6,2.3,{z}+1.9,{x}+.3,0,{z}-.3)"); time.sleep(3)
  pg.screenshot(path='/workspace/warehouse_game/game_v68_hose_snag_trestle.png')
