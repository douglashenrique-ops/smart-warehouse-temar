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
rep('<title>Painel de Ocupação de Estoque – TEMAR</title>', '<title>Smart Warehouse – Revenda TEMAR</title>')
rep('<div class="brand"><b>Painel de Ocupação de Estoque</b><span>Revenda TEMAR · Saldo real × Política × Capacidade do layout</span></div>',
    '<div class="brand"><b>🏭 Smart Warehouse</b><span>Revenda TEMAR · Painel de Ocupação de Estoque</span></div>')
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js"></script>')

# 2. CSS extra: tela de login, modo consulta
AUTH_CSS = r'''
#auth{position:fixed;inset:0;z-index:200;background:var(--bg);display:flex;align-items:center;justify-content:center;padding:20px}
#auth .abox{width:100%;max-width:380px;background:var(--surface-1);border:1px solid var(--line);border-radius:14px;padding:26px}
#auth .alogo{display:flex;align-items:center;gap:10px;margin-bottom:4px}
#auth .alogo i{width:38px;height:38px;border-radius:10px;background:rgba(57,135,229,.18);display:flex;align-items:center;justify-content:center;font-size:20px;font-style:normal}
#auth .alogo b{font-size:19px;letter-spacing:.3px}
#auth .asub{color:var(--text-muted);font-size:12.5px;margin:0 0 20px 48px}
#auth label{display:block;font-size:12px;color:var(--text-secondary);margin:12px 0 5px}
#auth input{width:100%;background:var(--surface-2);color:var(--text-primary);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font:inherit}
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
  <div class="abox">
    <div class="alogo"><i>🏭</i><b>Smart Warehouse</b></div>
    <p class="asub">Revenda TEMAR · Painel de Estoque</p>
    <form id="fLogin">
      <label>E-mail</label><input type="email" id="lEmail" autocomplete="username" required>
      <label>Senha</label><input type="password" id="lPass" autocomplete="current-password" required>
      <button class="primary" id="lBtn">Entrar</button>
      <div class="amsg" id="lMsg"></div>
    </form>
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
  if(!session){ $('#auth').style.display='flex'; document.body.classList.remove('booting'); setTimeout(()=>$('#lEmail').focus(),50); return; }
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
authStart();
'''
i = s.rindex("</script>\n</body>")
s = s[:i] + AUTH_JS + s[i:]
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
