#!/usr/bin/env python3
"""Gera o Smart Warehouse (site Vercel + Supabase) a partir do painel do claude.ai.
Uso: python3 make_sw.py <painel/index.html> <saida/index.html>"""
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    if old not in s:
        raise SystemExit('NAO ACHEI: ' + old[:80])
    s = s.replace(old, new, count)

SB_URL = 'https://qakaijyjbrrgmepwghmr.supabase.co'
SB_KEY = 'sb_publishable_rzHdLJk_X4WgbOPJOgvw3w_IhPEG2R9'

# 1. título, marca, biblioteca supabase
rep('<title>Painel de Ocupação de Estoque – TEMAR</title>', '<title>Smart Warehouse – Revenda TEMAR</title>\n<link rel="icon" type="image/png" href="favicon.png">')
rep('<div class="brand"><b>Painel de Ocupação de Estoque</b><span>Revenda TEMAR · Saldo real × Política × Capacidade do layout</span></div>',
    '<div class="brand" style="flex-direction:row;align-items:center;gap:10px"><img src="logo.png" alt="" style="height:36px;width:auto"><div style="display:flex;flex-direction:column;line-height:1.15"><b>Smart Warehouse</b><span>Revenda TEMAR · Painel de Ocupação de Estoque</span></div></div>')
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>')

# 2. CSS extra: tela de login, modo consulta
AUTH_CSS = r'''
#auth{position:fixed;inset:0;z-index:200;background:#0d1118;display:flex;align-items:center;justify-content:center;padding:20px;overflow:hidden;touch-action:none}
#auth #introCv{position:absolute;inset:0;width:100%;height:100%;display:block}
#auth .abox{position:relative;z-index:3;width:100%;max-width:360px;background:rgba(20,23,29,.82);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.12);border-radius:16px;padding:26px;transition:opacity .6s,transform .6s}
#auth.intro .abox{opacity:0;transform:scale(.96);pointer-events:none}
#introTxt{position:absolute;z-index:2;left:clamp(18px,5vw,64px);top:clamp(18px,9vh,90px);max-width:440px;color:#f2f2ef;transition:opacity .5s;pointer-events:none}
#introTxt .k{font-size:12px;letter-spacing:2px;color:#7fb3f0;font-weight:600}
#introTxt .h{font-size:clamp(24px,3.4vw,40px);font-weight:600;line-height:1.15;margin-top:8px}
#introTxt .p{font-size:clamp(13px,1.2vw,16px);color:#b5b4ad;margin-top:10px;line-height:1.55}
#introG{position:absolute;z-index:2;right:clamp(18px,5vw,64px);top:clamp(18px,9vh,90px);background:rgba(18,22,30,.88);border:1px solid #2b3445;border-radius:14px;padding:14px 18px;color:#f2f2ef;min-width:180px;opacity:0;transition:opacity .5s;pointer-events:none}
#introG .gl{font-size:12px;color:#85847d}#introG .gv{font-size:32px;font-weight:600;margin-top:2px}
#introG .gb{height:7px;border-radius:4px;background:#2a3140;margin-top:8px}#introG .gb i{display:block;height:7px;border-radius:4px;background:#3987e5;width:0}
#introSkip{position:absolute;z-index:4;right:20px;bottom:18px;width:auto!important;margin:0!important;padding:9px 16px!important;background:#3987e5;border:0;color:#fff;font-weight:600;border-radius:9px}
#introHint{position:absolute;z-index:2;left:50%;bottom:22px;transform:translateX(-50%);color:#b5b4ad;font-size:12px;text-align:center;transition:opacity .4s;pointer-events:none}
#introHint b{display:block;font-size:18px;animation:hintB 1.4s ease-in-out infinite}
@keyframes hintB{0%,100%{transform:translateY(0)}50%{transform:translateY(5px)}}
#introDots{position:absolute;z-index:2;right:22px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:9px}
#introDots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.25);transition:background .3s,transform .3s}
#introDots i.on{background:#3987e5;transform:scale(1.3)}
#auth:not(.intro) #introSkip,#auth:not(.intro) #introHint{display:none}
@media (max-width:760px){ #introG{top:auto;bottom:70px;right:16px;min-width:140px;padding:10px 14px} #introG .gv{font-size:24px} #introDots{display:none} }
#auth .alogo{display:flex;align-items:center;gap:10px;margin-bottom:4px}
#auth .alogo i{width:38px;height:38px;border-radius:10px;background:rgba(57,135,229,.18);display:flex;align-items:center;justify-content:center;font-size:20px;font-style:normal}
#auth .alogo b{font-size:19px;letter-spacing:.3px;color:#f2f2ef}
#auth .asub{color:#9a998f;font-size:12.5px;margin:0 0 20px 0}
#auth .acred{margin-top:18px;text-align:center;font-size:10.5px;line-height:1.35;color:#85847d;letter-spacing:.3px}
#auth label{display:block;font-size:12px;color:#b5b4ad;margin:12px 0 5px}
#auth input{width:100%;background:rgba(255,255,255,.07);color:#f2f2ef;border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:10px 12px;font:inherit}
#auth button{width:100%;margin-top:18px;padding:11px}
#auth .amsg{font-size:12.5px;margin-top:12px;min-height:18px;color:var(--neg)}
body.booting header,body.booting .shell{visibility:hidden}
#whoPill b{font-weight:600;color:var(--text-primary)}
.rtag{font-size:10.5px;padding:1px 7px;border-radius:999px;font-weight:700;margin-left:4px}
.rtag.admin{background:rgba(57,135,229,.18);color:var(--pos)}.rtag.consulta{background:var(--surface-3);color:var(--text-secondary)}
body.ro #tabs a[data-v=carga],body.ro #tabs a[data-v=users],body.ro [data-crit],body.ro #crAdd,body.ro #crAddBtn,body.ro #pzImp,body.ro #pzCode,body.ro #pzDias,body.ro #pzAdd,body.ro #pzSave,
body.ro #agFabBtn,body.ro #agCfgBtn,body.ro #agFab,body.ro #agCfg,body.ro #expAdd,body.ro #expCode,body.ro #expMot,body.ro #expName,body.ro #btnPalSave,body.ro #btnArmSave,
body.ro #tblExp button,body.ro #tblHist [data-del],body.ro #tblFab button,body.ro .adminonly{display:none!important}
body.ro #expAging,body.ro #expOcup,body.ro #armPal,body.ro #armHl,body.ro #tblPal input,body.ro #tblPz input,body.ro #tblFab input,body.ro #tblFab select{pointer-events:none;opacity:.6}
@media (max-width:760px){ #whoPill .wn{display:none} }
'''
rep('</style>\n</head>', AUTH_CSS + '</style>\n</head>')

# 3. tela de login + classe booting
rep('<body>\n', '''<body class="booting">
<div id="auth">
  <canvas id="introCv"></canvas>
  <div id="introTxt"><div class="k" id="itK"></div><div class="h" id="itH"></div><div class="p" id="itP"></div></div>
  <div id="introG"><div class="gl" id="igL">Ocupação do armazém</div><div class="gv" id="igV">0%</div><div class="gb"><i id="igB"></i></div></div>
  <div id="introDots"><i></i><i></i><i></i><i></i><i></i></div>
  <div id="introHint">role para conhecer<b>⌄</b></div>
  <button type="button" id="introSkip">Entrar ›</button>
  <div class="abox">
    <div class="alogo"><img src="logo.png" alt="" style="height:42px;width:auto"><b>Smart Warehouse</b></div>
    <p class="asub">Revenda TEMAR · Painel de Estoque</p>
    <form id="fLogin">
      <label>E-mail</label><input type="email" id="lEmail" autocomplete="username" required>
      <label>Senha</label><input type="password" id="lPass" autocomplete="current-password" required>
      <button class="primary" id="lBtn">Entrar</button>
      <div class="amsg" id="lMsg"></div>
    </form>
    <div class="acred">Douglas Henrique<br>God</div>
  </div>
</div>
''')

# 4. usuário logado + sair no cabeçalho
rep('<button id="btnTheme"', '<span class="pill" id="whoPill"></span>\n    <button id="btnOut" title="Sair do sistema">Sair</button>\n    <button id="btnTheme"')

# 5. item de menu e aba Usuários
rep('''<a data-v="carga" data-g="Cadastros e config." title="Carregar dados">''',
    '''<a data-v="users" data-g="Cadastros e config." title="Usuários"><span class="ic">👥</span><span class="lb">Usuários</span></a>
  <a data-v="carga" data-g="Cadastros e config." title="Carregar dados">''')
USERS_VIEW = '''  <!-- USUÁRIOS -->
  <section class="view" id="v-users">
    <div class="card" style="margin-bottom:12px">
      <h3>Cadastrar usuário <small>a pessoa entra na hora com o e-mail e a senha · Consulta só visualiza, Administrador tem acesso total</small></h3>
      <form class="toolbar" id="uNew" style="margin:0">
        <input id="uNome" placeholder="Nome" required style="min-width:200px">
        <input type="email" id="uEmail" placeholder="E-mail" required style="min-width:240px;background:var(--surface-2);color:var(--text-primary);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font:inherit;font-size:13px">
        <input id="uPass" placeholder="Senha (mín. 6)" minlength="6" required style="width:150px">
        <select id="uPapel"><option value="consulta">Consulta</option><option value="admin">Administrador</option></select>
        <button class="primary" id="uBtn">Cadastrar</button>
        <span class="note" id="uMsg"></span>
      </form>
    </div>
    <div class="tablewrap"><table id="tblUsers" data-nosort><thead><tr><th class="l">Nome</th><th class="l">E-mail</th><th class="l">Nível</th><th class="l">Status</th><th class="l">Nova senha</th><th></th></tr></thead><tbody></tbody></table></div>
  </section>

  <!-- CARGA -->'''
rep('  <!-- CARGA -->', USERS_VIEW)
s = s.replace('input#uNome', 'input#uNome')

# 6. cartão de migração -> importar backup
s = re.sub(r'    <div class="card" style="margin-bottom:12px;border-color:rgba\(57,135,229,.55\)">\n      <h3>💾 Migração para o Smart Warehouse</h3>.*?</div>\n    </div>\n',
'''    <div class="card adminonly" id="impCard" style="margin-bottom:12px;border-color:rgba(57,135,229,.55)">
      <h3>💾 Importar backup <small>use uma vez, com o arquivo exportado no painel antigo (claude.ai)</small></h3>
      <label class="drop" style="padding:10px 14px;display:inline-flex;gap:8px;align-items:center;margin:0" id="impDrop"><input type="file" accept=".json">📂 Escolher arquivo backup-painel-estoque-….json</label>
      <span class="note" id="impInfo" style="margin-left:10px"></span>
    </div>
''', s, count=1, flags=re.S)
if 'impDrop' not in s: raise SystemExit('cartao de migracao nao substituido')

# 7. Store -> Supabase
a = s.index("const Store={mode:'init',db:null,")
b = s.index("/* ===================== estado")
STORE = '''const SB=supabase.createClient('%s','%s');
let ME=null, _roWarned=0;
function roWarn(){ if(Date.now()-_roWarned>4000){ _roWarned=Date.now(); toast('Seu acesso é de Consulta: não é possível alterar dados.',3500); } }
const Store={mode:'init',ro:false,_ch:null,
  async init(){ this.mode='cloud'; },
  async get(path){ const {data,error}=await SB.from('docs').select('data').eq('key',path).maybeSingle(); if(error) throw error; return data?data.data:null; },
  async set(path,obj){ if(this.ro){ roWarn(); return; }
    let r=await SB.from('docs').upsert({key:path,data:obj});
    if(r.error){ await new Promise(x=>setTimeout(x,900)); r=await SB.from('docs').upsert({key:path,data:obj}); }
    if(r.error) throw r.error; },
  async del(path){ if(this.ro){ roWarn(); return; } const {error}=await SB.from('docs').delete().eq('key',path); if(error) throw error; },
  async list(coll){ const out=[]; for(let from=0;;from+=200){ const {data,error}=await SB.from('docs').select('data').like('key',coll+'/%%').order('key').range(from,from+199); if(error) throw error; out.push(...data.map(r=>r.data)); if(data.length<200) break; } return out; },
  watchHist(cb,onErr){
    const load=async()=>{ try{ cb(await this.list('hist'),{fromCache:false}); }catch(e){ onErr&&onErr(e); } };
    load(); this._localHist=load; let t=null;
    this._ch=SB.channel('docs-watch').on('postgres_changes',{event:'*',schema:'public',table:'docs'},p=>{ const k=(p.new&&p.new.key)||(p.old&&p.old.key)||''; if(!k||k.startsWith('hist/')){ clearTimeout(t); t=setTimeout(load,700); } }).subscribe();
    return ()=>SB.removeChannel(this._ch);
  }
};

''' % (SB_URL, SB_KEY)
s = s[:a] + STORE + s[b:]

# 8. sem importações embutidas (os dados vêm do backup)
rep("if(first){ importSaldos(); importValidade().then(importValidadeAdd).then(()=>setTimeout(updateVlBadge,1500)); }",
    "if(first){ setTimeout(updateVlBadge,1500); }")

# 9. init só depois do login
rep("(async function init(){", "async function appInit(){")
i = s.rindex("})();\n</script>")
s = s[:i] + "}\n" + s[i+len("})();\n"):]
rep("['geral','sku','disp','pareto','hist','crit','vld','vlc','pzc','hs','val','aging','expurgo','palet','arm','carga'].includes(h)",
    "['geral','sku','disp','pareto','hist','crit','vld','vlc','pzc','hs','val','aging','expurgo','palet','arm','carga','users'].includes(h)&&!(Store.ro&&['carga','users'].includes(h))")
rep("function renderView(v){ ", "function renderView(v){ if(v==='users') return renderUsers(); ")
rep("$('#btnBackup').onclick=exportBackup;\n", "")

# 10. auth, usuários, importar backup
AUTH_JS = r'''
/* ===================== login e acesso ===================== */
async function ufn(action,payload){ const {data,error}=await SB.functions.invoke('admin-users',{body:Object.assign({action},payload||{})});
  if(error){ let m=error.message; try{ const j=await error.context.json(); m=j.error||m; }catch(e){} throw new Error(m); } if(data&&data.error) throw new Error(data.error); return data; }
async function authStart(){
  const {data:{session}}=await SB.auth.getSession();
  if(!session){ $('#auth').style.display='flex'; document.body.classList.remove('booting'); startIntro(); return; }
  const {data:p,error}=await SB.from('profiles').select('*').eq('id',session.user.id).maybeSingle();
  if(error||!p||!p.ativo){ await SB.auth.signOut(); $('#auth').style.display='flex'; document.body.classList.remove('booting'); $('#lMsg').textContent='Seu acesso não está liberado. Fale com o administrador.'; return; }
  ME=p; Store.ro=p.papel!=='admin'; document.body.classList.toggle('ro',Store.ro);
  $('#whoPill').innerHTML=`<span class="wn"><b>${esc((p.nome||p.email).split(' ').slice(0,2).join(' '))}</b></span><span class="rtag ${p.papel}">${p.papel==='admin'?'Administrador':'Consulta'}</span>`;
  $('#auth').style.display='none'; document.body.classList.remove('booting'); setHH();
  appInit();
}
$('#fLogin').onsubmit=async e=>{ e.preventDefault(); const b=$('#lBtn'); b.disabled=true; $('#lMsg').textContent='';
  const {error}=await SB.auth.signInWithPassword({email:$('#lEmail').value.trim().toLowerCase(),password:$('#lPass').value});
  b.disabled=false; if(error){ $('#lMsg').textContent=/banned/i.test(error.message)?'Usuário bloqueado. Fale com o administrador.':'E-mail ou senha incorretos.'; return; }
  location.reload(); };
$('#btnOut').onclick=async()=>{ await SB.auth.signOut(); location.hash=''; location.reload(); };
SB.auth.onAuthStateChange(ev=>{ if(ev==='SIGNED_OUT'&&ME) location.reload(); });

async function renderUsers(){ if(Store.ro) return go('geral');
  $('#tblUsers tbody').innerHTML='<tr><td class="l" colspan="6">Carregando…</td></tr>';
  try{ const {users}=await ufn('list');
    $('#tblUsers tbody').innerHTML=users.map(u=>`<tr data-id="${u.id}"><td class="l"><b>${esc(u.nome||'–')}</b>${u.id===ME.id?' <span class="tag st-info">você</span>':''}</td><td class="l">${esc(u.email)}</td>
      <td class="l"><select data-a="papel" ${u.id===ME.id?'disabled':''} style="padding:4px 8px"><option value="consulta" ${u.papel==='consulta'?'selected':''}>Consulta</option><option value="admin" ${u.papel==='admin'?'selected':''}>Administrador</option></select></td>
      <td class="l"><span class="tag ${u.ativo?'st-good':'st-critical'}">${u.ativo?'Ativo':'Bloqueado'}</span></td>
      <td class="l"><input data-a="np" placeholder="nova senha" style="width:130px;padding:4px 8px"> <button data-a="pass" style="padding:4px 9px;font-size:12px">Trocar</button></td>
      <td class="l">${u.id===ME.id?'':`<button data-a="ativo" style="padding:4px 9px;font-size:12px">${u.ativo?'Bloquear':'Desbloquear'}</button>`}</td></tr>`).join('');
  }catch(e){ $('#tblUsers tbody').innerHTML=`<tr><td class="l" colspan="6">Erro: ${esc(e.message)}</td></tr>`; } }
$('#uNew').onsubmit=async e=>{ e.preventDefault(); const b=$('#uBtn'); b.disabled=true; $('#uMsg').textContent='Cadastrando…';
  try{ await ufn('create',{nome:$('#uNome').value.trim(),email:$('#uEmail').value,password:$('#uPass').value,papel:$('#uPapel').value});
    $('#uMsg').textContent='✓ Usuário cadastrado. Já pode entrar com o e-mail e a senha.'; $('#uNew').reset(); renderUsers(); }catch(err){ $('#uMsg').textContent='⚠ '+err.message; } b.disabled=false; };
$('#tblUsers').addEventListener('change',async e=>{ const s=e.target.closest('select[data-a=papel]'); if(!s) return;
  try{ await ufn('update',{id:s.closest('tr').dataset.id,papel:s.value}); toast('Nível atualizado ✓'); }catch(err){ toast(err.message,4000); renderUsers(); } });
$('#tblUsers').addEventListener('click',async e=>{ const b=e.target.closest('button[data-a]'); if(!b) return; const tr=b.closest('tr'), id=tr.dataset.id;
  try{
    if(b.dataset.a==='pass'){ const p=tr.querySelector('[data-a=np]').value; if(!p||p.length<6) return toast('Digite a nova senha (mínimo 6 caracteres).',3500); await ufn('password',{id,password:p}); tr.querySelector('[data-a=np]').value=''; toast('Senha alterada ✓'); }
    if(b.dataset.a==='ativo'){ const bloq=b.textContent==='Bloquear'; await ufn('update',{id,ativo:!bloq}); toast(bloq?'Usuário bloqueado ✓':'Usuário desbloqueado ✓'); renderUsers(); }
  }catch(err){ toast(err.message,4000); } });

$('#impDrop input').addEventListener('change',async e=>{ const f=e.target.files[0]; if(!f) return; e.target.value='';
  const info=$('#impInfo');
  try{ info.textContent='Lendo arquivo…'; const j=JSON.parse(await f.text()); const ents=Object.entries((j&&j.docs)||{});
    if(!ents.length) throw new Error('arquivo sem dados');
    if(!(await confirmBox(`Importar <b>${ents.length}</b> registros do backup de ${j.at?new Date(j.at).toLocaleString('pt-BR'):'?'}?<br>Registros com o mesmo nome serão substituídos.`))) { info.textContent=''; return; }
    let done=0, batch=[], size=0;
    const flush=async()=>{ if(!batch.length) return; let r=await SB.from('docs').upsert(batch); if(r.error){ await new Promise(x=>setTimeout(x,1200)); r=await SB.from('docs').upsert(batch); } if(r.error) throw r.error; done+=batch.length; batch=[]; size=0; info.textContent=`Importando… ${done}/${ents.length}`; };
    for(const [key,data] of ents){ const sz=JSON.stringify(data).length; if(size+sz>2500000) await flush(); batch.push({key,data}); size+=sz; if(batch.length>=25) await flush(); }
    await flush();
    info.textContent=`✓ ${done} registros importados. Recarregando…`; setTimeout(()=>location.reload(),1500);
  }catch(err){ info.textContent='⚠ Erro: '+(err.message||err); }
});

/* ===================== abertura 3D da tela de entrada ===================== */
function startIntro(){
  const A=$('#auth'); const seen=(()=>{ try{ return localStorage.getItem('sw:introSeen')==='1'; }catch(e){ return false; } })();
  const focusLogin=()=>setTimeout(()=>$('#lEmail').focus(),80);
  if(!window.THREE){ A.classList.remove('intro'); focusLogin(); return; }
  A.classList.add('intro');
  const cv=$('#introCv'); let R;
  try{ R=new THREE.WebGLRenderer({canvas:cv,antialias:true}); }catch(e){ A.classList.remove('intro'); focusLogin(); return; }
  R.setPixelRatio(Math.min(2,window.devicePixelRatio));
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x0d1118); scene.fog=new THREE.Fog(0x0d1118,30,70);
  const cam=new THREE.PerspectiveCamera(40,1,0.1,200);
  scene.add(new THREE.HemisphereLight(0xcfe0ff,0x1a1f28,0.75));
  const sun=new THREE.DirectionalLight(0xffffff,0.9); sun.position.set(10,18,12); scene.add(sun);
  const M=c=>new THREE.MeshStandardMaterial({color:c,roughness:.75,metalness:.1});
  const box=(w,h,d,m,x,y,z,p)=>{ const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m); o.position.set(x,y,z); (p||scene).add(o); return o; };
  box(60,.1,30,M(0x161b23),0,-.05,0);
  for(let i=-28;i<=28;i+=4) box(.04,.01,30,M(0x1f2631),i,.01,0);
  const orange=M(0xd8622a), steel=M(0x3a4250); const slots=[];
  function rack(z){ for(let x=-6;x<=6;x+=3){ box(.12,6,.12,steel,x,3,z-.6); box(.12,6,.12,steel,x,3,z+.6); }
    for(let l=0;l<4;l++){ const y=.25+l*1.5; box(12.2,.1,.12,orange,0,y,z-.6); box(12.2,.1,.12,orange,0,y,z+.6);
      for(let b=0;b<4;b++) slots.push({x:-4.5+b*3,y:y+.6,z}); } }
  rack(-3); rack(3);
  const palC=[0xe0a01e,0xc8a060,0x3987e5,0x1d9e75];
  const pals=slots.map((s,i)=>{ const g=new THREE.Group(); box(1.1,.15,1.1,M(0x8a6a3a),0,-.45,0,g); const m=M(palC[i%4]); box(1.0,.8,1.0,m,0,0,0,g); g.position.set(s.x,s.y,s.z); g.visible=false; g.userData={m,base:palC[i%4]}; scene.add(g); return g; });
  const order=pals.map((_,i)=>i).sort((a,b)=>((a*7)%11)-((b*7)%11));
  const truck=new THREE.Group(); box(6,2.2,2.2,M(0xd9d9d9),0,1.6,0,truck); box(1.8,1.8,2.1,M(0x2f6fbe),4,1.4,0,truck);
  [-2,0,3.8].forEach(x=>{ [-1,1].forEach(z=>{ const w=new THREE.Mesh(new THREE.CylinderGeometry(.4,.4,.3,16),M(0x222222)); w.rotation.x=Math.PI/2; w.position.set(x,.4,z*1.05); truck.add(w); }); });
  truck.position.set(-30,0,9); scene.add(truck);
  const fork=new THREE.Group(); box(1.6,1,1.1,M(0xe0a01e),0,.7,0,fork); box(.12,3,.12,M(0x888888),.9,1.7,-.35,fork); box(.12,3,.12,M(0x888888),.9,1.7,.35,fork);
  const carriage=new THREE.Group(); box(.9,.08,.9,M(0x999999),1.4,0,0,carriage); box(.8,.6,.8,M(0xe0a01e),1.4,.35,0,carriage); carriage.position.y=.3; fork.add(carriage); scene.add(fork);
  const steps=[
   {k:'01 · RECEBIMENTO',t:'Do caminhão à prateleira',s:'Cada entrada de fábrica registrada, com data e quantidade.',cam:[-14,7,18],look:[-4,1.5,4]},
   {k:'02 · OCUPAÇÃO',t:'Ocupação × Política × Capacidade',s:'Paletes, caixas, hecto e R$ comparados ao aprovado e ao layout.',cam:[0,9,17],look:[0,2.5,0]},
   {k:'03 · VALIDADE',t:'Controle de validade e PEPS',s:'Lotes que vencem antes de vender ficam em destaque.',cam:[8,6,12],look:[0,3,0]},
   {k:'04 · VALORIZAÇÃO',t:'Valorização e estoque parado',s:'Quanto vale o estoque e onde o dinheiro está parado.',cam:[14,11,10],look:[0,2,0]},
   {k:'05 · SMART WAREHOUSE',t:'',s:'',cam:[0,14,22],look:[0,1,0]}];
  const L=(a,b,t)=>a+(b-a)*t, E=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
  let prog=seen?4.6:0, target=prog, last=performance.now(), time=0, alive=true, shown=-1, auto=!seen, idle=0;
  const tx=$('#introTxt'), dots=[...document.querySelectorAll('#introDots i')];
  const toLogin=()=>{ target=4.6; auto=false; try{ localStorage.setItem('sw:introSeen','1'); }catch(e){} };
  $('#introSkip').onclick=toLogin;
  A.addEventListener('wheel',e=>{ if(e.target.closest('.abox')) return; e.preventDefault(); auto=false; idle=0; target=Math.max(0,Math.min(4.6,target+e.deltaY*0.0025)); },{passive:false});
  let ty=null; A.addEventListener('touchstart',e=>{ ty=e.touches[0].clientY; },{passive:true});
  A.addEventListener('touchmove',e=>{ if(ty==null||e.target.closest('.abox')) return; const y=e.touches[0].clientY; auto=false; idle=0; target=Math.max(0,Math.min(4.6,target+(ty-y)*0.008)); ty=y; },{passive:true});
  addEventListener('keydown',e=>{ if(!A.classList.contains('intro')) return; if(['ArrowDown','PageDown',' ','Enter'].includes(e.key)){ auto=false; target=Math.min(4.6,Math.floor(target)+1); } if(['ArrowUp','PageUp'].includes(e.key)){ auto=false; target=Math.max(0,Math.ceil(target)-1); } });
  function setText(i){ if(i===shown) return; shown=i; tx.style.opacity=0; dots.forEach((d,k)=>d.classList.toggle('on',k===i));
    setTimeout(()=>{ const s=steps[i]; $('#itK').textContent=s.k; $('#itH').textContent=s.t; $('#itP').textContent=s.s; tx.style.opacity=i===4?0:1; },350); }
  function resize(){ const w=A.clientWidth,h=A.clientHeight; R.setSize(w,h,false); cam.aspect=w/h; cam.updateProjectionMatrix(); }
  addEventListener('resize',resize); resize();
  let wasLogin=false;
  function frame(now){ if(!alive) return; const dt=Math.min(.05,(now-last)/1000); last=now; time+=dt;
    if(auto){ idle+=dt; if(idle>1.2) target=Math.min(4.6,target+dt*0.16); }
    prog+=(target-prog)*Math.min(1,dt*3.2);
    const p=Math.min(prog,4.999), i=Math.floor(p), f=E(p-i), a=steps[i], b=steps[Math.min(4,i+1)];
    const bb=Math.min(1,i<4?f*Math.max(0,(p-i-0.55)/0.45):0);
    cam.position.set(L(a.cam[0],b.cam[0],bb),L(a.cam[1],b.cam[1],bb),L(a.cam[2],b.cam[2],bb));
    if(i===4){ const r=Math.hypot(cam.position.x,cam.position.z), o=time*0.08; cam.position.x=Math.sin(o)*r; cam.position.z=Math.cos(o)*r; }
    cam.lookAt(L(a.look[0],b.look[0],bb),L(a.look[1],b.look[1],bb),L(a.look[2],b.look[2],bb));
    setText(i);
    truck.position.x=L(-30,-9,Math.min(1,E(Math.min(1,p/0.8))));
    const fx=Math.sin(time*0.9); fork.position.set(-5+fx*4,0,7); fork.rotation.y=fx>0?0:Math.PI; carriage.position.y=.3+Math.max(0,Math.sin(time*1.8))*1.6;
    const fillN=Math.round(pals.length*Math.min(.87,Math.max(.25,(p-0.6)/1.2*.87)));
    order.forEach((idx,k)=>{ pals[idx].visible=k<fillN; });
    const occ=Math.round(fillN/pals.length*100);
    $('#introG').style.opacity=(p>1&&p<4.05)?1:0;
    if(p>=3&&p<4.05){ $('#igL').textContent='Valor em estoque'; $('#igV').textContent='R$ '+(occ*0.21).toFixed(1).replace('.',',')+' mi'; $('#igB').style.background='#1d9e75'; }
    else { $('#igL').textContent='Ocupação do armazém'; $('#igV').textContent=occ+'%'; $('#igB').style.background=occ>85?'#e0a01e':'#3987e5'; }
    $('#igB').style.width=occ+'%';
    const red=p>=2&&p<4.05; pals.forEach((pl,k)=>{ const risk=red&&(k%7===2||k%11===5); pl.userData.m.color.setHex(risk?(k%2?0xe24b4a:0xef9f27):pl.userData.base); });
    $('#introHint').style.opacity=p<0.4?1:0;
    const login=p>=4.15; A.classList.toggle('intro',!login);
    if(login&&!wasLogin){ try{ localStorage.setItem('sw:introSeen','1'); }catch(e){} focusLogin(); } wasLogin=login;
    if(A.style.display==='none'){ alive=false; R.dispose(); return; }
    R.render(scene,cam); requestAnimationFrame(frame); }
  requestAnimationFrame(frame);
}
authStart();
'''
i = s.rindex("</script>\n</body>")
s = s[:i] + AUTH_JS + s[i:]
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
