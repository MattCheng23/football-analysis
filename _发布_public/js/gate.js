/* gate.js · 网站访问密码门（群友/朋友共享用）——防普通访客，懂技术的可绕过（静态站限制）
   用法：各页面 </body> 前加 <script src="js/gate.js?vXXXX"></script>；密码：{PW}
   记住登录 localStorage(pwok=1)；右上角🔒退出可清除 */
(function(){
  var PW = "t8ftz";
  var PW_VER = "v1";   /* 密码版本号：换密码时必须同步改（如 v2/v3），旧记住状态自动失效需重输 */
  var KEY = "pwok";
  if (localStorage.getItem(KEY) === PW_VER || sessionStorage.getItem(KEY) === PW_VER) return;
  var css = "#pwGate{position:fixed;inset:0;z-index:99999;background:#0e1c2e;display:flex;align-items:center;justify-content:center;flex-direction:column;color:#fff;font-family:system-ui,-apple-system,'PingFang SC','Microsoft YaHei';}"+
    "#pwGate .box{background:linear-gradient(160deg,#1b3a5c,#12293f);border:1px solid #2e5a86;border-radius:18px;padding:28px 30px;width:min(90vw,340px);text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.45);}"+
    "#pwGate h2{margin:0 0 6px;font-size:20px}"+
    "#pwGate p{margin:0 0 16px;font-size:12.5px;color:#a8c3dd}"+
    "#pwGate input{width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid #3d6b99;background:#0d1f33;color:#fff;font-size:17px;letter-spacing:4px;text-align:center;outline:none}"+
    "#pwGate input:focus{border-color:#5aa0e8}"+
    "#pwGate button{margin-top:12px;width:100%;padding:12px;border-radius:10px;border:0;background:#3d7d5b;color:#fff;font-size:15px;font-weight:700;cursor:pointer}"+
    "#pwGate button:hover{background:#4a966e}"+
    "#pwGate .err{color:#ff8f8f;font-size:12px;min-height:16px;margin-top:8px}"+
    "#pwGate .tip{font-size:11px;color:#7f9ab8;margin-top:14px}"+
    "#pwGate .rm{display:flex;align-items:center;gap:7px;margin-top:10px;font-size:12.5px;color:#a8c3dd;justify-content:center;cursor:pointer}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var d = document.createElement("div"); d.id = "pwGate";
  d.innerHTML = '<div class="box"><h2>🔒 本站仅限受邀访问</h2><p>请输入访问密码（群友/朋友请向 Matt 索取）</p>'+
    '<input id="pwInput" type="password" autocomplete="off" placeholder="•••••"/>'+
    '<button id="pwBtn">进入</button><div class="err" id="pwErr"></div>'+
    '<label class="rm"><input type="checkbox" id="pwRemember" checked>记住我（下次自动进入）</label>'+
    '<div class="tip">密码区分字母与小写 · 选"记住我"输入一次即可</div></div>';
  document.body.appendChild(d);
  var inp = d.querySelector("#pwInput"), btn = d.querySelector("#pwBtn"), err = d.querySelector("#pwErr"), rm = d.querySelector("#pwRemember");
  function saveOk(){ var key = rm.checked ? localStorage : sessionStorage; key.setItem(KEY, PW_VER); }
  function tryGo(){ if (inp.value === PW){ saveOk(); d.remove(); } else { err.textContent = "密码不对，再试试"; inp.value = ""; inp.focus(); } }
  btn.addEventListener("click", tryGo);
  inp.addEventListener("keydown", function(e){ if (e.key === "Enter") tryGo(); });
  inp.focus();
})();
