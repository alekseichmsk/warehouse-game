import sys,json,time
from playwright.sync_api import sync_playwright
page=sys.argv[1]; tag=sys.argv[2]; O='/workspace/warehouse_game/'
AUD="""(()=>{const vw=innerWidth,vh=innerHeight;const els=[...document.querySelectorAll('body *')].filter(e=>{const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0)return false;if(!(cs.position==='fixed'||cs.position==='absolute'))return false;if(e.tagName==='CANVAS')return false;const r=e.getBoundingClientRect();return r.width>8&&r.height>8&&e.id;});
const R=els.map(e=>{const r=e.getBoundingClientRect();return {id:e.id,x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),fs:getComputedStyle(e).fontSize}});
const off=R.filter(r=>r.x<0||r.y<0||r.x+r.w>vw+1||r.y+r.h>vh+1).map(r=>r.id);
const ov=[];for(let i=0;i<R.length;i++)for(let j=i+1;j<R.length;j++){const a=R[i],b=R[j];const ix=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),iy=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(ix>4&&iy>4){const A=document.getElementById(a.id),B=document.getElementById(b.id);if(A.contains(B)||B.contains(A))continue;ov.push([a.id,b.id,ix,iy]);}}
const c=document.querySelector('canvas');const cr=c.getBoundingClientRect();const ch=document.getElementById('crosshair')||document.getElementById('cross');let chc=null;if(ch){const r=ch.getBoundingClientRect();chc=[Math.round(r.x+r.width/2-vw/2),Math.round(r.y+r.height/2-vh/2)];}
return {vw,vh,dpr:devicePixelRatio,canvas:[c.width,c.height,Math.round(cr.width),Math.round(cr.height)],cross:chc,off,ov,els:R};})()"""
res={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  for name,(w,h) in {'portrait':(390,844),'landscape':(844,390)}.items():
    ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=3,is_mobile=True,has_touch=True,user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(f'http://localhost:8765/{page}?mode=workshop&cb={time.time()}'); time.sleep(12)
    # dismiss start screen if any by tapping center
    pg.screenshot(path=O+f'game_v67_phone_{name}_{tag}_start.png')
    for sel in ['#startBtn','#start','#play','button:has-text("Играть")','button:has-text("Начать")']:
      try:
        if pg.locator(sel).first.is_visible(): pg.locator(sel).first.tap(); time.sleep(3); break
      except Exception: pass
    time.sleep(3); pg.screenshot(path=O+f'game_v67_phone_{name}_{tag}.png')
    res[name]=pg.evaluate(AUD); res[name]['errs']=errs; ctx.close()
print(json.dumps(res,ensure_ascii=False))
# real touch check: drag joystick + tap action button in both orientations
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  for name,(w,h) in {'portrait':(390,844),'landscape':(844,390)}.items():
    ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=3,is_mobile=True,has_touch=True)
    pg=ctx.new_page(); pg.goto(f'http://localhost:8765/{page}?mode=workshop&cb={time.time()}'); time.sleep(12)
    cdp=ctx.new_cdp_session(pg); r=pg.evaluate("(()=>{const r=joy.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,r.width]})()")
    p0=pg.evaluate('__wstate().pos')
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':r[0],'y':r[1]}]})
    for k in range(12): cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':r[0],'y':r[1]-r[2]*.04*k}]}); time.sleep(.08)
    time.sleep(1.5); st=pg.evaluate("(()=>{const s=stick.getBoundingClientRect(),j=joy.getBoundingClientRect();return [s.x-j.x,s.y-j.y]})()")
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]}); time.sleep(.3)
    p1=pg.evaluate('__wstate().pos'); print(name,'touch-walk moved',round(((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)**.5,2),'stick inside',st)
    ctx.close()
