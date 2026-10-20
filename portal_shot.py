from playwright.sync_api import sync_playwright
import time
O='/workspace/warehouse_game/'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':1280,'height':720}); pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__hammerGLB&&window.__camAt&&window.__cmpReady)',timeout=90000); time.sleep(3)
  pg.evaluate("__camAt(1.6,1.7,-0.4,3.0,1.1,-2.5)"); time.sleep(3); pg.screenshot(path=O+'game_v67_hose_from_portal.png')
  pg.evaluate("__camAt(5.5,2.6,0.5,4.5,2.4,-5.5)"); time.sleep(2); pg.screenshot(path=O+'game_v67_airline_to_portal.png')
