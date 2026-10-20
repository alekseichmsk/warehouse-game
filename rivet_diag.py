import time,json
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
    for kind in ['shield','floor','ceiling','plafond']:
        pg=b.new_page(viewport={'width':1280,'height':720})
        pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!window.__setupRivet'); time.sleep(1.5)
        pg.evaluate(f"__setupRivet('{kind}')"); pg.evaluate("__aimAt('rivet',0)"); time.sleep(1.2)
        for _ in range(5):
            if pg.evaluate('__wstate().wAim')=='rivet': break
            pg.evaluate("__aimAt('rivet',0)"); time.sleep(.8)
        pg.evaluate("document.getElementById('action').click()")
        for i in range(60):
            time.sleep(.2); d=pg.evaluate('__noseDiag()')
            if d['k'] and d['k']>=.55: break
        pg.evaluate("document.getElementById('toast').style.display='none'")
        pg.screenshot(path=f'/workspace/warehouse_game/game_v68_riveter_{kind}.png'); print(kind,json.dumps(d)); pg.close()
    b.close()
