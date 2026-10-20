from playwright.sync_api import sync_playwright
import time
O='/workspace/warehouse_game/'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__liftReady&&window.__camAt)',timeout=90000); time.sleep(3)
  E=pg.evaluate; E('window.noGlow=true'); D=E('__liftDims()'); x,z,y=D['x'],D['z'],D['sheetY']; E("__camNear(.01)")
  E(f"__camAt({x-2.2},{1.9},{z+2.0},{x},{y},{z})"); time.sleep(3); pg.screenshot(path=O+'game_v69_lift_floor_tray.png')
  E(f"__camAt({x+1.55},{1.05},{z+.55},{x+1.0},{y},{z})"); time.sleep(3); pg.screenshot(path=O+'game_v69_checker_threshold_closeup.png')
  E(f"__camAt({x-.2},{1.2},{z+1.05},{x-.2},{.35},{z+.3})"); time.sleep(3); pg.screenshot(path=O+'game_v69_tray_frame_rim.png')
