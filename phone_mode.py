# v7.6 phone tool mode: take tape, enter mode by button, joystick moves camera (player stays), exit button
from playwright.sync_api import sync_playwright
import time,json,math
R={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  ctx=b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=2); pg=ctx.new_page(); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&mobile&cb={time.time()}'); pg.wait_for_function('!!(window.__wstate&&window.__tm&&window.__tapeState)',timeout=90000); time.sleep(2)
  E=pg.evaluate; S=lambda:E('__wstate()')
  for _ in range(6):
    E("__aimAt('tape')"); time.sleep(.9)
    if S().get('wAim')=='tape': break
  pg.click('#btnTake'); time.sleep(.5); R['holding']=S()['holdingW']
  R['enterBtn']=E("getComputedStyle(document.getElementById('tmEnterBtn')).display"); pg.click('#tmEnterBtn'); time.sleep(.3); t0=E('__tm.state()'); p0=S()['pos']
  E("joyVec.x=0;joyVec.y=-1") if E("typeof joyVec!=='undefined'") else None
  bb=pg.locator('#joy').bounding_box(); cx,cy=bb['x']+bb['width']/2,bb['y']+bb['height']/2
  cdp=ctx.new_cdp_session(pg)
  def tp(t,x,y): cdp.send('Input.dispatchTouchEvent',{'type':t,'touchPoints':[] if t=='touchEnd' else [{'x':x,'y':y}]})
  tp('touchStart',cx,cy); 
  for i in range(8): tp('touchMove',cx,cy-6*i); time.sleep(.05)
  time.sleep(.6); tp('touchEnd',0,0); time.sleep(.2)
  t1=E('__tm.state()'); p1=S()['pos']
  R['tm']={'on':t0['on'],'name':t0['name'],'cam_moved':round(math.dist(t0['pos'],t1['pos']),3),'player_moved':round(math.dist(p0[:2],p1[:2]),4),'exitBtn':E("getComputedStyle(document.getElementById('tmExitBtn')).display")}
  pg.screenshot(path='/workspace/warehouse_game/game_v76_phone_mode.png')
  pg.click('#tmExitBtn'); time.sleep(.8); R['tm']['off_after_exit']=not E('__tm.state()')['on']
  R['errs']=er
print(json.dumps(R,ensure_ascii=False,indent=1))
