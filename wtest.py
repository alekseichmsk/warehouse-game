import time,json
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!window.__wtestRun'); time.sleep(1)
    print('pre',pg.evaluate('__wstate().wIndex')); r=pg.evaluate('__wtestRun()'); r.pop('log',None); print('WORKSHOP',json.dumps(r,ensure_ascii=False)); time.sleep(1)
    print('pay rows',pg.evaluate('__shieldRecs().length'), pg.evaluate("document.getElementById('payWin')?document.getElementById('payWin').style.display:'none'"))
    pg2=b.new_page(); pg2.on('pageerror',lambda e:errs.append('WH '+str(e))); pg2.goto(f'http://localhost:8765/index.html?mode=warehouse&cb={time.time()}'); time.sleep(4); pg2.keyboard.press('w'); time.sleep(1)
    print('ERRS',errs); b.close()
