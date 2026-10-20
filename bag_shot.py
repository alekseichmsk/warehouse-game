from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__camAt&&window.__rivState&&window.__bodyState)',timeout=90000); time.sleep(3)
  E=pg.evaluate; E('window.noGlow=true'); d=E('__benchDims()'); X,Z,T=d['x'],d['z'],d['top']; F=Z+0.52; E("__camNear(.01)")
  E(f"__dropAt({X}-.25,{T},{F}+.30,'rivetbag',true)"); time.sleep(4); bs=E("__bodyState('rivetbag')"); x,y,z=bs['pos']; print(bs)
  E(f"__camAt({x},{T+.30},{z+.26},{x},{T+.01},{z})"); time.sleep(3); pg.screenshot(path='/workspace/warehouse_game/game_v68_rivet_bag_closeup.png')
  E(f"__camAt({x+.02},{T+.13},{z+.11},{x+.02},{T+.01},{z})"); time.sleep(3); pg.screenshot(path='/workspace/warehouse_game/game_v68_rivet_nuts_in_bag_macro.png')
