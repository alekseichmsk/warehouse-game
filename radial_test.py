# v7.8 phone radial menu: tap = main action (take), hold -> ring, slide to sector (drop) -> executed; release in center = cancel; ring stays on-screen (portrait+landscape)
from playwright.sync_api import sync_playwright
import time,json,math
R={}
def run(b,vw,vh,tag,shot=None):
  ctx=b.new_context(viewport={'width':vw,'height':vh},is_mobile=True,has_touch=True,device_scale_factor=2); pg=ctx.new_page(); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&mobile&cb={time.time()}'); pg.wait_for_function('!!(window.__wstate&&window.__radial)',timeout=90000); time.sleep(2)
  E=pg.evaluate; S=lambda:E('__wstate()'); cdp=ctx.new_cdp_session(pg); r={}
  def tp(t,x=0,y=0): cdp.send('Input.dispatchTouchEvent',{'type':t,'touchPoints':[] if t=='touchEnd' else [{'x':x,'y':y,'id':1}]})
  vis=lambda i:E(f"(()=>{{const e=document.getElementById('{i}');return !!e&&getComputedStyle(e).display!=='none'}})()")
  r['hidden_old']={i:vis(i) for i in ['btnTake','btnDrop','btnLever','rotBtns']}; r['kept']={i:vis(i) for i in ['action','joy','radBtn']}
  bb=E('__radial.btn()'); bx,by=bb['x']+bb['width']/2,bb['y']+bb['height']/2; r['btn']=[round(bb['x']),round(bb['y']),round(bb['width'])]
  ab=E("document.getElementById('action').getBoundingClientRect().toJSON()"); r['btn_above_action']=bb['y']+bb['height']<=ab['y']+1
  for _ in range(6):
    E("__aimAt('tape')"); time.sleep(.9)
    if S().get('wAim')=='tape': break
  r['tries']=[]
  for _ in range(4):
    tp('touchStart',bx,by); time.sleep(.08); tp('touchEnd'); time.sleep(.5); r['tap_main']=[E('__radial.state().last'),S()['holdingW']]; r['tries'].append([S()['wAim']]+r['tap_main'])
    if r['tap_main'][1]=='tape': break
    E("__aimAt('tape')"); time.sleep(1.2)
  # hold -> ring
  tp('touchStart',bx,by); time.sleep(.65); st=E('__radial.state()'); r['ring']=st; cx,cy=st['c']; Rr=st['R']
  ring_ok=cx-Rr-26>=0 and cy-Rr-26>=0 and cx+Rr+26<=vw and cy+Rr+26<=vh; r['item_px']=E("document.querySelector('#radRing .it').getBoundingClientRect().width"); r['gap_px']=round(2*math.pi*Rr/len(st['items']),1); r['ring_on_screen']=ring_ok
  i=st['items'].index('drop'); n=len(st['items']); a=-math.pi/2+i*2*math.pi/n
  for k in range(1,9): tp('touchMove',bx+(cx+Rr*math.cos(a)-bx)*k/8,by+(cy+Rr*math.sin(a)-by)*k/8); time.sleep(.03)
  time.sleep(.2); r['sel']=E('__radial.state().sel')==i; r['label']=E("document.querySelector('#radRing .lb').textContent"); r['labels_visible']=E("[...document.querySelectorAll('#radRing .lb')].filter(e=>getComputedStyle(e).display!=='none').length")
  if shot: pg.screenshot(path=shot)
  tp('touchEnd'); time.sleep(.8); r['after_drop']=[E('__radial.state().last'),S()['holdingW']]
  # cancel: hold, release in center
  tp('touchStart',bx,by); time.sleep(.65); st=E('__radial.state()'); cx,cy=st['c']; tp('touchMove',cx,cy); time.sleep(.3); tp('touchEnd'); time.sleep(.3); r['cancel']=E('__radial.state().last')
  r['errs']=er; ctx.close()
  r['ok']=r['tap_main'][1]=='tape' and r['after_drop']==['drop',None] and r['cancel']=='cancel' and ring_ok and r['sel'] and not any(r['hidden_old'].values()) and all(r['kept'].values())
  R[tag]=r
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  run(b,844,390,'landscape','/workspace/warehouse_game/game_v79_radial.png'); run(b,390,844,'portrait')
print(json.dumps(R,ensure_ascii=False,indent=1))
