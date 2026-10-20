from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  for n,(w,h),css in [('portrait',(390,844),':root{--st:47px!important;--sb:34px!important}'),('landscape',(844,390),':root{--sl:47px!important;--sr:47px!important;--sb:21px!important}')]:
    ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=3,is_mobile=True,has_touch=True); pg=ctx.new_page()
    pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); time.sleep(12); pg.add_style_tag(content=css); time.sleep(1)
    pg.screenshot(path=f'/workspace/warehouse_game/game_v67_phone_{n}_notch_sim.png'); print(n,pg.evaluate("['hud','joy','btns'].map(i=>{const r=document.getElementById(i).getBoundingClientRect();return [i,Math.round(r.x),Math.round(r.y),Math.round(r.right),Math.round(r.bottom)]})")); ctx.close()
