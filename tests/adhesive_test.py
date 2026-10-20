# v7.1 two-component adhesive test: open lids, take pouch, knife (extend), cut along the dashed line, pour, insert mixer, mix (before/after), pot life.
from playwright.sync_api import sync_playwright
import time,json,sys
O='/workspace/warehouse_game/'; R={}; P=sys.argv[1] if len(sys.argv)>1 else 'game_v72_'
X,Z=-5.3,-6.55
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required'])
  pg=b.new_page(viewport={'width':1280,'height':720}); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!(window.__adhReady&&window.__camAt&&window.__adhState)',timeout=90000); time.sleep(2)
  E=pg.evaluate; A=lambda:E('__adhState()')
  def aim(w,off=None,want=None,d=None):
    for _ in range(5):
      E(f"__adhAim('{w}',{json.dumps(off or [0,0,0])},{d or 'null'})"); time.sleep(.6)
      if A()['aim']==(want or w): return True
    return False
  shot=lambda n:pg.screenshot(path=O+P+n+'.png')
  E(f"__camAt({X+.35},1.15,{Z+1.05},{X+.15},.22,{Z})"); time.sleep(1); shot('adh_buckets')
  R['aimA']=aim('pailA',[0,.13,0]); R['actA']=A()['act']; pg.keyboard.press(' '); time.sleep(1.5)
  R['aimB']=aim('pailB',[0,.03,0]); pg.keyboard.press(' '); time.sleep(1.5); R['lids']=[A()['lidA'],A()['lidB']]
  E(f"__camAt({X+.1},1.05,{Z+.8},{X-.15},.1,{Z})"); time.sleep(.8); shot('adh_open_paste')
  aim('pailB',[0,0,0],'pailB'); R['take_bag_btn']=A()['take']; pg.keyboard.press('e'); time.sleep(.6); R['bag']=A()['bag']
  aim('bag',[0,0,0],'adhBag'); pg.keyboard.press('e'); time.sleep(.4); R['sealed_take']=[A()['holding'],E("document.getElementById('toast').textContent")]
  aim('uknife',None,'uknife'); pg.keyboard.press('e'); time.sleep(.6); R['knife']=A()['holding']
  pg.keyboard.press(' '); time.sleep(.8); R['blade']=[A()['bladeOut'],A()['bladeZ']]
  # cut gesture: hold action, sweep along the dashed line (local z -.072)
  aim('bag',[-.075,0,-.072],'adhBag',.55); pg.keyboard.down(' ')
  for i in range(40):
    x=-.075+i*.004; E(f"__adhAim('bag',[{x},0,-.072],.55)"); time.sleep(.08)
    if i==18: time.sleep(.3); shot('adh_knife_cut'); R['knife_ov']=E("(()=>{const k=__adhState(); return [k.cutPct,k.cutHit]})()")
    if A()['cut']: break
  pg.keyboard.up(' '); time.sleep(.5); st=A(); R['cut']=[st['cut'],st['cutPct']]
  E(f"__camAt({X+.39},.85,{Z+.42},{X+.39},.38,{Z-.05})"); time.sleep(.6); shot('adh_bag_cut')
  aim('crate',[.1,0,.12],'adhCrate'); pg.keyboard.press('e'); time.sleep(.4); R['knife_back']=A()['holding']
  aim('bag',[0,0,0],'adhBag'); pg.keyboard.press('e'); time.sleep(.6); R['bag_hold']=A()['holding']
  aim('pailA',[0,0,0],'pailA'); pg.keyboard.down(' '); s=False
  for i in range(60):
    time.sleep(.15); st=A()
    if not s and st['pour']>.4: E(f"__camAt({X-.05},.95,{Z+.75},{X-.35},.25,{Z})"); time.sleep(.5); shot('adh_pour'); s=True; aim('pailA',[0,0,0],'pailA')
    if st['pour']>=1: break
  pg.keyboard.up(' '); time.sleep(.4); st=A(); R['pour']=[st['pour'],st['started'],st['potLeftMin']]
  E("__dropW()"); time.sleep(1.5)
  E(f"__camAt({X-.35},.80,{Z+.42},{X-.35},.10,{Z})"); time.sleep(1); shot('adh_mix_before')
  aim('mixer',None,'mixer'); pg.keyboard.press('e'); time.sleep(.6); R['mixer_hold']=A()['holding']
  aim('pailA',[0,0,0],'pailA'); R['ins_btn']=A()['take']; pg.keyboard.press('e'); time.sleep(.6); R['mixer']=A()['mixer']
  aim('pailA',[0,0,.05],'pailA'); pg.keyboard.down(' '); m=False
  for i in range(120):
    time.sleep(.15); st=A()
    if not m and st['mix']>.4: E(f"__camAt({X-.2},1.0,{Z+.55},{X-.35},.12,{Z})"); time.sleep(.4); shot('adh_mixing'); m=True; aim('pailA',[0,0,.05],'pailA')
    if st['mix']>=1.1: break
  pg.keyboard.up(' '); time.sleep(.4); st=A(); R['mixed']=[st['mixMin'],st['quality'],st['verdict']]
  E(f"__camAt({X-.30},.80,{Z+.42},{X-.35},.10,{Z})"); time.sleep(1); shot('adh_mix_after'); aim('pailA',[0,0,.05],'pailA')
  aim('pailA',[0,0,.05],'pailA'); pg.keyboard.press('e'); time.sleep(.6); R['result']=A()['result']; R['holding_after']=A()['holding']
  E(f"__camAt({X+.4},1.35,{Z+1.25},{X+.1},.25,{Z})"); time.sleep(.6); shot('adh_overview')
  # quality curve + pot life (hooks)
  R['q_curve']={str(v):E(f"(__adhMix({v}),__adhState().quality)") for v in [.4,.85,1.0,1.5,2.0,2.5]}
  E("__adhMix(1.05)"); E("__adhPot(3500)"); time.sleep(.6); R['pot_near']=A()['potLeftMin']; time.sleep(5.5); st=A(); R['pot_set']=[st['set'],st['potLeftMin']]
  R['panel']=E("document.getElementById('adhPanel').innerText")
  R['errs']=er
  print(json.dumps(R,ensure_ascii=False,indent=1))
  b.close()
