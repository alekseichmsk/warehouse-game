# v7.1 phone check: adhesive panel + action/take buttons near the station, overlap with other controls, touch-hold mixing
from playwright.sync_api import sync_playwright
import time,json
O='/workspace/warehouse_game/'; R={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
  for nm,(w,h) in {'portrait':(390,844),'landscape':(844,390)}.items():
    ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=2,is_mobile=True,has_touch=True,user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
    pg=ctx.new_page(); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
    pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!window.__adhReady',timeout=90000); time.sleep(1.5)
    pg.evaluate("__adhAim('pailA',[0,.13,0])"); time.sleep(.8); pg.tap('#action'); time.sleep(1.2)
    r=pg.evaluate("""(()=>{const ids=['adhPanel','action','btnTake','btnDrop','sawPanel','orderPill','holdPill'];const o={};for(const i of ids){const e=document.getElementById(i); if(!e)continue; const s=getComputedStyle(e); if(s.display==='none'||s.visibility==='hidden')continue; const r=e.getBoundingClientRect(); if(r.width<1)continue; o[i]=[r.left,r.top,r.right,r.bottom].map(Math.round);} return o;})()""")
    ov=[]; ks=list(r)
    for i in range(len(ks)):
      for j in range(i+1,len(ks)):
        a,c=r[ks[i]],r[ks[j]]
        if a[0]<c[2] and c[0]<a[2] and a[1]<c[3] and c[1]<a[3]: ov.append((ks[i],ks[j]))
    off=[k for k,v in r.items() if v[0]<0 or v[1]<0 or v[2]>w or v[3]>h]
    R[nm]={'lidA':pg.evaluate('__adhState().lidA'),'rects':r,'overlap':ov,'off':off,'errs':er}
    pg.screenshot(path=O+f'game_v71_phone_{nm}_adhesive.png'); ctx.close()
  print(json.dumps(R,ensure_ascii=False))
  b.close()
