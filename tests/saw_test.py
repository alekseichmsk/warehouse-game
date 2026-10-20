# v7.0 tile saw test: take a 300x300 tile, measure it with the tape, put it on the saw, set fence from the tape / buttons, power on, push head -> split.
from playwright.sync_api import sync_playwright
import time,json,math
O='/workspace/warehouse_game/'; R={}
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required'])
  pg=b.new_page(viewport={'width':1280,'height':720}); er=[]; pg.on('pageerror',lambda e:er.append(str(e)))
  pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('!!(window.__sawReady&&window.__camAt&&window.__sawState)',timeout=90000); time.sleep(2)
  E=pg.evaluate; S=lambda:E('__wstate()')
  def aimw(w,tries=5):
    for _ in range(tries):
      E(f"__aimAt('{w}')"); time.sleep(.8)
      if S().get('wAim')==w: return True
    return False
  R['aim_stock']=aimw('tileStock300'); pg.keyboard.press('e'); time.sleep(.6); h=S()['holdingW']; R['hold']=[h,E(f"TOOL_LABELS_SAFE='';1")]
  R['aim_saw']=aimw('saw'); R['take_btn']=E("document.getElementById('btnTake').textContent"); pg.keyboard.press('e'); time.sleep(.8)
  st=E('__sawState()'); R['on_saw']={'tile':st['tile'],'dims':st['tileDims'],'panel':st['panel']}
  # set fence: buttons +10 x2, -1 x5  (150 -> 165)
  for s_ in ['+10','+10','-1','-1','-1','-1','-1']: pg.click(f'#sawPanel button[data-s="{s_}"]'); time.sleep(.05)
  R['fence_buttons']=E('__sawState().fence')
  E("__sawCmd('-10')"); E("__sawCmd('-10')"); E("__sawCmd('-10')"); E("__sawCmd('-10')"); E("__sawCmd('-10')") ; E("__sawCmd('-10')"); E("__sawCmd('+5')")
  R['fence_set']=E('__sawState().fence')
  # push without power -> warning, no cut
  aimw('saw'); pg.keyboard.down(' '); time.sleep(1.0); pg.keyboard.up(' '); R['no_power']={'toast':E("document.getElementById('toast').textContent"),'headX':E('__sawState().headX'),'cuts':E('__sawState().cuts')}
  pg.click('#sawPanel button[data-s="pow"]'); time.sleep(.5); R['power']=E('__sawState().on')
  aimw('saw'); pg.keyboard.down(' ')
  shot=False
  for i in range(200):
    time.sleep(.15); st=E('__sawState()')
    if not shot and st['kerf']>.12:
      E(f"__camAt({-7.3+.75},1.25,{-4.55+.85},{-7.3},.72,{-4.55})"); time.sleep(.6); pg.screenshot(path=O+'game_v72_saw_cutting.png'); shot=True; aimw('saw',2)
    if st['cuts']>0: break
  pg.keyboard.up(' '); time.sleep(3.5); st=E('__sawState()'); R['after']={'cuts':st['cuts'],'last':st['last'],'pieces':st['pieces'],'tile':st['tile']}
  E(f"__camAt({-7.3+.45},1.15,{-4.55+.75},{-7.3},.70,{-4.45})"); time.sleep(1.2); pg.screenshot(path=O+'game_v72_cut_pieces.png')
  # take the offcut (physical object) and drop it on the floor
  off=st['last']['offcut'] if st['last'] else None
  if off:
    for _ in range(5):
      E(f"__aimAt('{off}')"); time.sleep(.8)
      if S().get('wAim')==off: break
    pg.keyboard.press('e'); time.sleep(.6); R['took_offcut']=S()['holdingW']==off
    E("__look(-1.2)"); time.sleep(.3); pg.keyboard.press('g'); time.sleep(3); R['offcut_drop']=E(f"__bodyState('{off}')")
    part=st['last']['part']
    for _ in range(5):
      E(f"__aimAt('{part}')"); time.sleep(.8)
      if S().get('wAim')==part: break
    pg.keyboard.press('e'); time.sleep(.6); R['took_part']=S()['holdingW']==part; E("__look(-1.2)"); time.sleep(.3); pg.keyboard.press('g'); time.sleep(2)
  # 1200x600: lengthwise 1200 > cut length 1020 -> warning; rotate -> cut 300 from 600-wide side
  aimw('tileStock1200'); pg.keyboard.press('e'); time.sleep(.6); aimw('saw'); pg.keyboard.press('e'); time.sleep(.6)
  R['big_on_saw']=E('__sawState().tileDims')
  aimw('saw'); pg.keyboard.down(' '); time.sleep(1.2); pg.keyboard.up(' '); R['big_warn']=E("document.getElementById('toast').textContent")
  E("__sawCmd('rot')"); E("__sawCmd('+10')"); time.sleep(.3); R['big_rot']=E('__sawState().tileDims'); R['big_fence']=E('__sawState().fence')
  for _ in range(2): E("(()=>{return 1})()")
  aimw('saw'); pg.keyboard.down(' ')
  for i in range(260):
    time.sleep(.15)
    if E('__sawState().cuts')>1: break
    if i%40==39: pg.keyboard.up(' '); aimw('saw',2); pg.keyboard.down(' ')
  pg.keyboard.up(' '); time.sleep(3); R['big_after']=E('__sawState().last'); R['big_pieces']=E('__sawState().pieces')
  E(f"__camAt({-7.3+1.3},1.5,{-4.55+1.7},{-7.3},.5,{-4.2})"); time.sleep(1.2); pg.screenshot(path=O+'game_v72_cut_1200x600.png')
  R['errs']=er
print(json.dumps(R,ensure_ascii=False,indent=1))
