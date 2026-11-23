<?php
mysqli_report(MYSQLI_REPORT_OFF);
$mysqli = new mysqli();
$svtTipo = 'activar';
$presLang = $_GET['lang'] === 'en' ? 'en' : 'es';
$O = $_GET['o'] === 'v' ? 'v' : 'h';
$DATA = file_get_contents("/home/claude/pres/data-$presLang.json");
?><!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
html,body{margin:0;background:#000;overflow:hidden}
.svt-open-wrap,#svtModal{display:none!important}
#S{position:absolute;width:1920px;height:1080px;aspect-ratio:auto;overflow:hidden;background:#f4f4f5}
#S .svt-scene{padding:10cqh 5cqw 8cqh}
.pzi{position:absolute;inset:0;padding:0!important;display:none}
.pzi.on{display:block}
#cam{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0}
#cam img.st{position:absolute;inset:0;width:100%;height:100%}
#tcov,#tbar{position:absolute;display:none}
#tbar{background:linear-gradient(90deg,#e10600,#ff3b30)}
#intro{position:absolute;inset:0;background:#e10600;z-index:20}
#ibar{position:absolute;top:0;bottom:0;width:18px;margin-left:-9px;background:#fff;z-index:21;box-shadow:0 0 30px rgba(255,255,255,.8)}
#oc{position:absolute;left:50%;top:50%;border-radius:50%;background:radial-gradient(circle,#ff3b30,#e10600 60%,#b10000);z-index:22;transform:translate(-50%,-50%)}
#ol{position:absolute;left:50%;top:50%;width:200px;height:200px;margin:-100px 0 0 -100px;border-radius:50%;background:#fff;z-index:23;display:flex;align-items:center;justify-content:center;box-shadow:0 20px 60px rgba(0,0,0,.35)}
#ol img{width:150px}
.pz-logo{position:absolute;top:4.5cqh;right:4cqw;height:5.4cqh;z-index:5}
.pz-note{position:absolute;left:0;right:0;margin:0 auto;bottom:5cqh;width:max-content;max-width:62cqw;text-align:center;background:#fff;color:#0a0a0a;font-weight:800;font-size:1.8cqw;border-radius:999px;padding:1.4cqh 2.6cqw;box-shadow:0 14px 34px rgba(0,0,0,.4);z-index:6}
.pz .sva-ben span{font-size:1.5cqw}
<?php if ($O === 'v'): ?>
#V{position:absolute;inset:0;width:1080px;height:1920px;background:radial-gradient(circle at 80% 10%,#5a0000,#0a0a0a 60%);font-family:Poppins,sans-serif;color:#fff;overflow:hidden}
#V .vlogo{position:absolute;top:110px;left:0;right:0;text-align:center}#V .vlogo img{height:120px}
#V .vtit{position:absolute;top:268px;left:0;right:0;text-align:center;color:#ff3b30;font-weight:800;letter-spacing:.32em;font-size:28px}
#V .vnum{position:absolute;top:318px;left:0;right:0;text-align:center;color:#d4d4d8;font-size:26px;font-weight:600}
#card{position:absolute;left:24px;top:400px;width:1032px;height:580.5px;border-radius:26px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.55);border:3px solid rgba(255,255,255,.12)}
#S{transform-origin:0 0;transform:scale(<?= 1032 / 1920 ?>)}
#sub{position:absolute;left:60px;right:60px;top:1010px;height:640px;display:flex;align-items:center;justify-content:center;text-align:center}
#sub .ln{overflow:hidden;padding:6px 0}
#sub .ln>div{font-size:58px;font-weight:800;line-height:1.28}
#sub .w{color:rgba(255,255,255,.28)}#sub .w.on{color:#fff}#sub .w.now{color:#ff3b30}
#V .vfoot{position:absolute;bottom:92px;left:0;right:0;text-align:center;font-weight:800;font-size:34px}#V .vfoot b{color:#ff3b30}
#V .vbar{position:absolute;left:0;bottom:0;height:12px;background:#e10600}
<?php endif; ?>
</style></head><body>
<?php include '/home/claude/binantrader/sumiago/app/includes/tutorial-rangos-video.php'; ?>
<?php if ($O === 'v'): ?>
<div id="V"><div class="vlogo"><img src="/sumiago/assets/img/logo-sumiago-light.png"></div>
<div class="vtit"><?= $presLang === 'en' ? 'BUSINESS PRESENTATION' : 'PRESENTACIÓN DE NEGOCIO' ?></div><div class="vnum" id="vnum"></div>
<div id="card">
<?php endif; ?>
<div class="svt-stage" id="S">
  <section class="pzi" id="pzi"><div id="cam"><div id="tcov"></div><div id="tbar"></div></div></section>
  <?php include __DIR__ . '/pres_scenes.php'; ?>
  <div id="intro"></div><div id="ibar"></div><div id="oc"></div><div id="ol"><img src="/sumiago/assets/img/icon-192.png"></div>
</div>
<?php if ($O === 'v'): ?>
</div>
<div id="sub"></div><div class="vfoot">sumiago<b>.com</b></div><div class="vbar" id="vbar"></div>
</div>
<?php endif; ?>
<script>
var DATA = <?= $DATA ?>, O = '<?= $O ?>', PRE = .5, W = 1920, H = 1080, cur = -1, curSub = -1;
var S = document.getElementById('S'), cam = document.getElementById('cam'), pzi = document.getElementById('pzi');
var intro = document.getElementById('intro'), ibar = document.getElementById('ibar'), oc = document.getElementById('oc'), ol = document.getElementById('ol');
var tcov = document.getElementById('tcov'), tbar = document.getElementById('tbar');
var TOT = DATA.reduce(function(a, s){ return a + s.L; }, 0);
function cl(x){ return Math.max(0, Math.min(1, x)); }
function sm(x){ x = cl(x); return x * x * (3 - 2 * x); }
function eo(x){ x = cl(x); return 1 - Math.pow(1 - x, 3); }
function setup(i){
  var s = DATA[i];
  document.querySelectorAll('#S .svt-scene').forEach(function(e){ e.classList.remove('on'); });
  pzi.classList.remove('on');
  cam.querySelectorAll('img.st').forEach(function(e){ e.remove(); });
  if (s.type === 'img') {
    s.imgs.forEach(function(u, j){ var im = new Image(); im.className = 'st'; im.src = u; im.style.opacity = j ? 0 : 1; cam.insertBefore(im, tcov); });
    pzi.classList.add('on');
    if (s.title) { var b = s.title; [tcov, tbar].forEach(function(e){ e.style.left = b[0] * W + 'px'; e.style.top = b[1] * H + 'px'; e.style.height = b[3] * H + 'px'; }); tcov.style.width = b[2] * W + 'px'; tcov.style.background = b[4]; }
  } else {
    var el = document.querySelector('#S .svt-scene[data-k="' + s.k + '"]'); void el.offsetWidth; el.classList.add('on');
  }
  if (O === 'v') { document.getElementById('vnum').textContent = (i + 1) + ' / ' + DATA.length; curSub = -1; }
}
function camAt(kf, t){
  if (t <= kf[0][0]) return kf[0].slice(1);
  for (var j = 1; j < kf.length; j++) if (t < kf[j][0]) { var a = kf[j - 1], b = kf[j], u = sm((t - a[0]) / (b[0] - a[0])); return [a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u]; }
  return kf[kf.length - 1].slice(1);
}
function subs(s, t){
  var tv = t - PRE, k = 0;
  for (var j = 0; j < s.sub.length; j++) if (tv >= s.sub[j].t0 - .15) k = j;
  var box = document.getElementById('sub');
  if (k !== curSub) {
    curSub = k;
    box.innerHTML = '<div class="ln"><div>' + s.sub[k].w.map(function(w){ return '<span class="w">' + w[0].replace(/</g, '&lt;') + '</span>'; }).join(' ') + '</div></div>';
  }
  var inner = box.querySelector('.ln>div'), st = s.sub[k];
  inner.style.transform = 'translateY(' + (1 - eo((tv - st.t0 + .15) / .4)) * 110 + '%)';
  var sp = box.querySelectorAll('.w');
  st.w.forEach(function(w, j){ var nx = j + 1 < st.w.length ? st.w[j + 1][1] : st.t1; sp[j].className = 'w' + (tv >= w[1] ? (tv < nx ? ' on now' : ' on') : ''); });
}
function seek(i, t){
  if (i !== cur) { setup(i); cur = i; }
  var s = DATA[i];
  if (s.type === 'img') {
    var c = camAt(s.cam, t), z = c[0];
    cam.style.transform = 'translate(' + (W / 2 - c[1] * W * z) + 'px,' + (H / 2 - c[2] * H * z) + 'px) scale(' + z + ')';
    var ims = cam.querySelectorAll('img.st');
    for (var j = 1; j < ims.length; j++) ims[j].style.opacity = cl((t - s.steps[j - 1]) / .45);
    if (s.title) {
      var b = s.title, p1 = eo((t - .45) / .4), p2 = sm((t - .85) / .4);
      tcov.style.display = t < .85 ? 'block' : 'none';
      tbar.style.display = (p1 > 0 && p2 < 1) ? 'block' : 'none';
      tbar.style.left = (b[0] + b[2] * p2) * W + 'px'; tbar.style.width = b[2] * (p1 - p2) * W + 'px';
    }
  } else {
    var ms = (t - PRE) * 1000;
    document.getAnimations().forEach(function(a){ a.pause(); a.currentTime = ms; });
    var el = document.querySelector('#S .svt-scene.on');
    el.querySelectorAll('.svt-num').forEach(function(n){ var u = cl(((t - PRE) - (+n.dataset.at)) / .6); n.textContent = Math.round(+n.dataset.from + (+n.dataset.to - +n.dataset.from) * u); });
  }
  // apertura: barrido rojo con borde blanco
  if (s.intro && t < .6) { var e = sm(t / .55); intro.style.display = 'block'; intro.style.clipPath = 'inset(0 0 0 ' + (e * 100) + '%)'; ibar.style.display = (e > 0 && e < 1) ? 'block' : 'none'; ibar.style.left = e * W + 'px'; }
  else { intro.style.display = 'none'; ibar.style.display = 'none'; }
  // cierre: el logo aparece y se transforma en un círculo rojo que cubre todo
  if (s.outro && t > s.L - .97) {
    var a = (t - (s.L - .97)) / .22, g = (t - (s.L - .78)) / .78;
    ol.style.display = 'flex'; ol.style.transform = 'scale(' + (eo(a) * (1 + Math.max(0, g) * 1.2)) + ')'; ol.style.opacity = 1 - cl((g - .55) / .3);
    var r = g > 0 ? 100 + Math.pow(cl(g), 2.2) * 2300 : 0; oc.style.display = r ? 'block' : 'none'; oc.style.width = oc.style.height = 2 * r + 'px';
  } else { ol.style.display = 'none'; oc.style.display = 'none'; }
  if (O === 'v') { subs(s, t); var before = 0; for (var q = 0; q < i; q++) before += DATA[q].L; document.getElementById('vbar').style.width = ((before + t) / TOT * 100) + '%'; }
}
window.__ready = true;
</script>
</body></html>
