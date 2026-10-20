from playwright.sync_api import sync_playwright
import time,json
O='/workspace/warehouse_game/'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  pg=b.new_page(viewport={'width':960,'height':600}); pg.goto(f'http://localhost:8765/index.html?mode=workshop&nohud=1&cb={time.time()}'); pg.wait_for_function('!!(window.__liftReady&&window.__camAt&&window.__sawReady)',timeout=90000); time.sleep(2)
  E=pg.evaluate; E('window.noGlow=true'); print(json.dumps(E('__liftOrders().map(o=>[o.n,o.W,o.D,o.kg,o.finish,o.tile||"",o.plan.list.join("; "),o.plan.total])'),ensure_ascii=False))
  for i in range(1,6):
    E(f'__liftOrder({i})'); time.sleep(1); x,z=-4.3,-3.6
    E(f"__camAt({x-.2},2.3,{z+2.1},{x},.72,{z})"); time.sleep(2.5); pg.screenshot(path=f'/tmp/var{i}.png')
  ctxs=[]
  for n,(w,h) in {'portrait':(390,844),'landscape':(844,390)}.items():
    c=b.new_context(viewport={'width':w,'height':h},device_scale_factor=2,is_mobile=True,has_touch=True); q=c.new_page(); q.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); q.wait_for_function('!!(window.__sawReady&&window.__aimAt)',timeout=90000); time.sleep(2)
    q.evaluate("__aimAt('saw')"); time.sleep(2.5); q.screenshot(path=O+f'game_v70_phone_{n}_saw_panel.png')
    print(n,q.evaluate("(()=>{const ids=['sawPanel','joy','btns','hud','rotBtns','cross'];const R=ids.map(i=>{const e=document.getElementById(i);if(!e||getComputedStyle(e).display==='none')return null;const r=e.getBoundingClientRect();return [i,r.x|0,r.y|0,r.right|0,r.bottom|0]}).filter(Boolean);const ov=[];for(const a of R)for(const b of R){if(a[0]<b[0]&&Math.min(a[3],b[3])-Math.max(a[1],b[1])>4&&Math.min(a[4],b[4])-Math.max(a[2],b[2])>4)ov.push(a[0]+'/'+b[0]);}return {R,ov,off:R.filter(r=>r[1]<0||r[2]<0||r[3]>innerWidth||r[4]>innerHeight).map(r=>r[0])}})()"))
    c.close()
