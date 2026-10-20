import time
from playwright.sync_api import sync_playwright
O='/workspace/warehouse_game/'
with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720})
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__hammerGLB&&window.__pliersGLB&&window.__screwdriverGLB&&window.__camAt)',timeout=90000); time.sleep(2)
  pg.evaluate('window.noGlow=true'); E=pg.evaluate; d=E('__benchDims()'); X,Z,T=d['x'],d['z'],d['top']; F=Z+0.52
  def shot(n,cx,cy,cz,tx,tz,w=3):
    E(f"__camAt({cx},{cy},{cz},{tx},{T+.01},{tz})"); time.sleep(w); pg.screenshot(path=O+n)
  # whole bench row as laid out (no overlaps, all resting on the top)
  shot('game_v66_bench_items_closeup.png',X-.05,1.25,F+.75,X-.05,F-.05)
  # staged: the three hand tools put down next to each other (physics place, they settle by themselves)
  for id,dx,dz in [('hammer',.02,.10),('pliers',.17,.10),('screwdriver',.29,.08),('rivetbag',-.25,.30)]:
    E(f"__dropAt({X}+{dx},{T},{F}+{dz},'{id}',true)")
  time.sleep(4)
  shot('game_v66_tools_closeup.png',X+.15,1.08,F+.42,X+.15,F+.03)
  shot('game_v66_rivet_bag_closeup.png',X-.25,1.08,F+.68,X-.25,F+.30)
print('ok')
