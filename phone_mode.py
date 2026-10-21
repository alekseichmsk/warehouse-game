# v7.7 phone: tape works WITHOUT mode (tap A, walk, tap = fix, tap = reset, edge snap); no mode button; other modes auto on action with small ✖
from playwright.sync_api import sync_playwright
import time,json,math
R={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  ctx=b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=2); pg=ctx.new_page(); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&mobile&cb={time.time()}'); pg.wait_for_function('!!(window.__wstate&&window.__tm&&window.__tapeState&&window.__liftReady)',timeout=90000); time.sleep(2)
  E=pg.evaluate; S=lambda:E('__wstate()'); vis=lambda i:E(f"getComputedStyle(document.getElementById('{i}')).display")
  for _ in range(6):
    E("__aimAt('tape')"); time.sleep(.9)
    if S().get('wAim')=='tape': break
  pg.click('#btnTake'); time.sleep(.5); R['holding']=S()['holdingW']; R['enterBtn']=vis('tmEnterBtn')
  D=E('__liftDims()'); y=D['sheetY']; z=D['z']; x0,x1=D['min'][0],D['max'][0]
  # aim at a point 8 mm inside the rim edge -> snap to edge; A then walk, B near other point
  def look(c,t): E(f"__camAt({c[0]},{c[1]},{c[2]},{t[0]},{t[1]},{t[2]})"); time.sleep(1)
  def settle(c,T):
    t=list(T)
    for _ in range(8):
      look(c,t); h=E('__tapeState().hit'); q=h and h['p']
      if q and math.dist(q,T)<.006: return q
      if q: t=[t[i]+max(-.1,min(.1,T[i]-q[i])) for i in range(3)]
    return q
  A=[-4.3-.4,y,z]; B=[-4.3+.4,y,z]
  settle((-4.9,1.62,z+1.1),A); pg.tap('#action'); time.sleep(.4); R['tap1']=E('[__tapeTT(),__tapeState().A]'); R['tm_on_after_tap']=E('__tm.state().on')
  # walk with joystick: player moves (no mode), tape stays anchored
  p0=S()['pos']; bb=pg.locator('#joy').bounding_box(); cx,cy=bb['x']+bb['width']/2,bb['y']+bb['height']/2; cdp=ctx.new_cdp_session(pg)
  def tp(t,x,y): cdp.send('Input.dispatchTouchEvent',{'type':t,'touchPoints':[] if t=='touchEnd' else [{'x':x,'y':y}]})
  tp('touchStart',cx,cy)
  for i in range(8): tp('touchMove',cx+6*i,cy); time.sleep(.05)
  time.sleep(.6); tp('touchEnd',0,0); time.sleep(.3); p1=S()['pos']; R['player_walked']=round(math.dist(p0[:2],p1[:2]),3); R['A_kept']=E('__tapeState().A')==R['tap1'][1]
  settle((-3.7,1.62,z+1.1),B); time.sleep(.3); R['live']=E('[__tapeState().mm,window.__tapeSnap]')
  pg.tap('#action'); time.sleep(.3); R['tap2']=E('[__tapeTT(),__tapeState().mm,window.__tapeLast&&window.__tapeLast.mm]')
  look((-3.6,1.62,z+1.0),[-3.4,y,z-.2]); R['fixed_mm_after_look']=E('__tapeState().mm'); R['btn']=E("document.getElementById('action').textContent")
  look((-4.3,1.95,z+1.5),[-4.3,y,z-.35]); time.sleep(.5); R['blade']=E('__tapeState().blade')
  pg.screenshot(path='/workspace/warehouse_game/game_v77_phone_tape.png')
  pg.tap('#action'); time.sleep(.8); R['tap3']=E('[__tapeTT(),__tapeState().on]')
  # Alt-free exact: expected snapped length equals 800 mm between rim-inside points? report raw
  # other mode: auto on action only; small ✖
  E("__tm.enter()"); R['other_mode_note']='tape has no mode on phone'; R['exitBtn_hidden_no_mode']=vis('tmExitBtn')
  R['errs']=er
print(json.dumps(R,ensure_ascii=False,indent=1))
