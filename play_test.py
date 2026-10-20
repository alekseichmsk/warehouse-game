import json,time,sys
from playwright.sync_api import sync_playwright
OUT='/workspace/warehouse_game/'
log=[];fails=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader'])
    pg=b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(f'http://localhost:8765/index.html?mode=workshop&cb={time.time()}'); pg.wait_for_function('window.__wstate',timeout=60000); time.sleep(2)
    S=lambda:pg.evaluate('__wstate()')
    def aim(w,i=None):
        pg.evaluate(f'__aimAt({json.dumps(w)},{json.dumps(i)})'); time.sleep(.3)
        for _ in range(20):
            st=S()
            if st['wAim'] and (w!='rivet' or st['wAimIdx']==i): break
            time.sleep(.15)
        time.sleep(.2)
    def waitanim():
        for _ in range(100):
            if not S()['anim']: return
            time.sleep(.15)
    def press(btn,what):
        st=S(); key='actDis' if btn=='action' else 'takeDis'
        if st[key]: fails.append((st['title'],what,st['act'] if btn=='action' else st['take'],st['wAim'],st['holdingW'])); return False
        pg.evaluate(f"document.getElementById('{btn}').click()"); time.sleep(.25); waitanim(); return True
    def shot(n): pg.evaluate("document.getElementById('toast').style.display='none'"); time.sleep(.15); pg.screenshot(path=OUT+f'game_v63_{n}.png'); log.append('shot '+n)
    aim('gateA'); press('action','gate'); time.sleep(.3); waitanim()
    log.append(pg.evaluate('__teleportHaul()'))
    shots=set(); seen=0; it=0
    def free_hands(where='drop'):
        h=S()['holdingW']
        if not h: return
        if where=='bench': aim('bench'); press('btnTake','put on bench '+h)
        else:
            pg.evaluate('__look(-1.25,2.2)'); time.sleep(.4); pg.keyboard.press('g'); time.sleep(.4)
            if h=='riveter' and 'dropped' not in shots:
                aim('floorTool','riveter'); shot('dropped_tool'); shots.add('dropped')
    def take(tool):
        if S()['holdingW']==tool: return
        free_hands('bench' if tool!='riveter' else 'drop')
        aim(tool); press('btnTake','take '+tool)
    while it<160:
        it+=1; st=S(); t=st['title'] or ''; i0=st['wIndex']
        if t.startswith('Возьми щит с поддона'):
            seen+=1
            if seen==3: break
            free_hands(); aim('supply'); time.sleep(.6); aim('supply'); press('btnTake','take shield')
            if 'shield_hands' not in shots: time.sleep(.4); shot('shield_hands'); shots.add('shield_hands')
        elif t.startswith('Положи щит на козлы'): aim('goats'); press('btnTake','put shield')
        elif t.startswith('Возьми пакет'):
            free_hands('bench'); aim('rivetbag')
            if 'bag' not in shots: shot('rivet_bag'); shots.add('bag')
            press('btnTake','take bag')
        elif t.startswith('Вставь заклёпки'):
            for k,v in enumerate(S()['rivets']):
                if v=='aim': aim('rivet',k); press('action',f'insert {k}')
        elif t.startswith('Возьми пневмо'):
            if S()['holdingW']!='riveter':
                free_hands('bench')
                aim('floorTool','riveter') ; press('btnTake','take riveter')
        elif t.startswith('Проклепай'):
            for k,v in enumerate(S()['rivets']):
                if v=='in':
                    aim('rivet',k)
                    if k==2 and 'aim_rivet' not in shots: shot('aim_rivet'); shots.add('aim_rivet'); log.append(S()['aimLabel']+' | '+S()['act'])
                    press('action',f'rivet {k}')
        elif t.startswith('Переверни'): aim('part'); press('action','flip')
        elif t.startswith('Возьми лист Батопласта'):
            free_hands(); aim('bato'); press('btnTake','take bato')
            if 'bato_hands' not in shots: time.sleep(.3); shot('bato_hands'); shots.add('bato_hands')
        elif t.startswith('Наклей полосу'):
            n=int(t.split('шумки ')[1].split('/')[0]); x=-1.05+(n-1)*.6+min(.6,1.05-(-1.05+(n-1)*.6))/2
            # imperfect human placement: small offsets
            dz=[.004,-.006,.003,.008][n-1]; dx=[0.01,0.02,0.015,0.0][n-1]
            if seen==2 and n==2: pg.keyboard.press('x'); pg.keyboard.press('x')
            aim('trough',[x+dx,dz/0.75])
            if 'dash' not in shots and n==2: time.sleep(.4); shot('bato_preview_dashed'); shots.add('dash')
            press('action',f'strip {n}')
            if n==4 and 'trough' not in shots: aim('trough',[0.4,0]); shot('bato_in_trough'); shots.add('trough')
        elif t.startswith('Прокатай шумку'):
            take('roller')
            xs=[-1.0+i*0.04 for i in range(51)] if seen==1 else [-1.0+i*0.04 for i in range(40)]
            pg.keyboard.down(' ')
            for j,x in enumerate(xs):
                for dz in ([-.09,.09] if j%2==0 else [.09,-.09]):
                    pg.evaluate(f"__aimAt('trough',[{x},{dz}])"); time.sleep(.07)
                if j==30 and 'roll' not in shots: shot('rolling_partial'); shots.add('roll')
            pg.keyboard.up(' '); time.sleep(.3)
            log.append('roll '+S()['take'])
            if not S()['takeDis']: press('btnTake','finish roll')
        elif t.startswith('Подпиши щит'):
            take('marker'); aim('trough',[0.6,0]); press('action','open sign')
            cv=pg.locator('#signCv').bounding_box()
            if cv:
                X,Y,W,H=cv['x'],cv['y'],cv['width'],cv['height']
                for stroke in [[(.15,.25),(.2,.8)],[(.3,.25),(.45,.25),(.45,.5),(.3,.5),(.3,.8),(.45,.8)],[(.6,.25),(.75,.25),(.65,.5),(.75,.75),(.6,.8)]]:
                    pg.mouse.move(X+stroke[0][0]*W,Y+stroke[0][1]*H); pg.mouse.down()
                    for a_,b_ in stroke[1:]: pg.mouse.move(X+a_*W,Y+b_*H,steps=8)
                    pg.mouse.up()
                if 'sign' not in shots: shot('sign_window'); shots.add('sign')
                pg.click('#signOk'); time.sleep(.4)
        elif t.startswith('Возьми готовый'):
            free_hands('bench'); aim('part'); press('btnTake','take done shield')
        elif t.startswith('Положи щит на выходной'): aim('output'); press('btnTake','put on output')
        else: log.append('unknown '+t); break
        if S()['wIndex']==i0: fails.append(('NO ADVANCE',t))
        else: log.append(f'{i0} {t} -> ok')
        if len(fails)>6: break
    pg.evaluate('__showPay()'); time.sleep(.5); shot('pay_window')
    log.append(json.dumps(pg.evaluate('__shieldRecs().map(r=>({n:r.n,t:+r.t.toFixed(1),rivets:r.rivets,bato:{c:+r.bato.coverage.toFixed(3),o:+r.bato.overlap.toFixed(3),out:+r.bato.outside.toFixed(3),off:+r.bato.offset_mm.toFixed(1),skew:+r.bato.skew_deg.toFixed(2),q:+r.bato.q.toFixed(3)},roll:+r.roll.toFixed(3),signed:r.signed,pay:r.pay}))'),ensure_ascii=False))
    print(json.dumps({'log':log,'fails':fails,'errs':errs,'final':S()},ensure_ascii=False,indent=0))
    b.close()
