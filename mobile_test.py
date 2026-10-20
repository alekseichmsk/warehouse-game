import time,json
from playwright.sync_api import sync_playwright
OUT='/workspace/warehouse_game/'; res={}
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
    ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!window.__runUntil'); time.sleep(2)
    cdp=ctx.new_cdp_session(pg)
    def swipe(x,y0,y1,steps=14):
        cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y0}]})
        for i in range(1,steps+1): cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y0+(y1-y0)*i/steps}]}); time.sleep(.02)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    S=lambda:pg.evaluate('__wstate()')
    # pitch limits by touch
    for _ in range(4): swipe(300,250,700)
    time.sleep(.3); res['pitch_down_deg']=round(S()['pos'][3]*57.2958,1)
    for _ in range(5): swipe(320,600,260)
    time.sleep(.3); res['pitch_up_deg']=round(S()['pos'][3]*57.2958,1)
    res['step']=pg.evaluate("__runUntil('Возьми лист Батопласта')")
    pg.evaluate("__setHold('riveter')"); pg.evaluate("__aimAt('bato')"); time.sleep(1.2)
    st=S(); res['busy_take_btn']=st['take']; res['busy_action_btn']=st['act']
    pg.tap('#btnTake') if not st['takeDis'] else pg.evaluate("document.getElementById('btnTake').disabled=false;document.getElementById('btnTake').click()")
    time.sleep(.3); pg.screenshot(path=OUT+'game_v66_mobile_toast.png'); res['toast']=pg.evaluate("[document.getElementById('toast').textContent,getComputedStyle(document.getElementById('toast')).fontSize,document.getElementById('toast').getBoundingClientRect().toJSON()]")
    pg.tap('#btnDrop'); time.sleep(.5)
    pg.evaluate("__aimAt('bato')"); pg.evaluate('__walk(0.8)'); time.sleep(.3)
    for _ in range(4): swipe(300,250,750)
    time.sleep(1.0); st=S(); res['look_down']=[round(st['pos'][3]*57.2958,1),st['wAim'],st['take']]
    pg.screenshot(path=OUT+'game_v66_mobile_look_down.png')
    if not st['takeDis']: pg.tap('#btnTake')
    time.sleep(.6); res['holding_after']=S()['holdingW']; pg.screenshot(path=OUT+'game_v66_mobile_bato_hands.png')
    time.sleep(2.3); res['toast_hidden_after_2s']=pg.evaluate("getComputedStyle(document.getElementById('toast')).display")
    res['errs']=errs; print(json.dumps(res,ensure_ascii=False,indent=1)); b.close()
