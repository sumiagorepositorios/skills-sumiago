<?php
/* Video "Membresía Anual" — 8 escenas. Tiempos (s) relativos al inicio de la voz de cada escena. */
$L = $presLang;
$C = [
 'es' => [
  'intro' => ['crown'=>2.2,'t'=>2.4,'sub'=>3.9,'team'=>5.2,'earn'=>6.6],
  'ahorro' => ['h'=>.2,'tiles'=>1.7,'n20'=>2.5,'sum'=>4.3,'a'=>6.6,'n100'=>7.5,'once'=>8.5,'stamp'=>9.7],
  'beneficios' => ['h'=>.4,'c'=>[2.5,5.6,8.0,11.2,12.7,14.3],'out'=>15.3],
  'recibes' => ['h'=>2.0,'yo'=>2.3,'m'=>5.0,'c20'=>7.2,'a'=>8.8,'c100'=>10.2,'cmp'=>11.6],
  'ejemplo' => ['h'=>.1,'pop'=>1.0,'p'=>[3.0,3.4,3.8,4.5,4.8],'ta'=>7.6,'tm'=>8.5,'c300'=>9.9,'c340'=>12.2,'tot'=>15.3],
  'red' => ['h'=>.2,'dir'=>3.4,'ind'=>4.4,'ca'=>5.6,'n2000'=>7.2,'cm'=>9.4,'n400'=>10.9,'both'=>13.8],
  'frenos' => ['h'=>.1,'yo'=>1.3,'ref'=>2.2,'lock'=>3.6,'lose'=>5.0,'an'=>6.6,'go'=>7.4],
  'cierre' => ['h'=>.1,'c'=>[2.2,4.5,6.5],'disc'=>8.7,'logo'=>13.7]],
 'en' => [
  'intro' => ['crown'=>2.5,'t'=>2.6,'sub'=>3.5,'team'=>4.8,'earn'=>5.8],
  'ahorro' => ['h'=>.2,'tiles'=>1.8,'n20'=>3.0,'sum'=>4.9,'a'=>7.1,'n100'=>8.3,'once'=>9.6,'stamp'=>10.5],
  'beneficios' => ['h'=>.4,'c'=>[2.6,5.4,7.0,9.6,10.8,12.4],'out'=>13.2],
  'recibes' => ['h'=>2.2,'yo'=>2.5,'m'=>5.5,'c20'=>7.5,'a'=>9.0,'c100'=>10.4,'cmp'=>12.3],
  'ejemplo' => ['h'=>.2,'pop'=>1.6,'p'=>[4.2,4.6,5.0,5.5,6.1],'ta'=>8.3,'tm'=>9.4,'c300'=>11.0,'c340'=>13.1,'tot'=>15.7],
  'red' => ['h'=>.2,'dir'=>4.9,'ind'=>6.0,'ca'=>8.9,'n2000'=>10.1,'cm'=>12.6,'n400'=>14.9,'both'=>16.7],
  'frenos' => ['h'=>.1,'yo'=>1.5,'ref'=>2.4,'lock'=>3.9,'lose'=>5.6,'an'=>7.9,'go'=>9.3],
  'cierre' => ['h'=>.1,'c'=>[2.2,4.6,6.4],'disc'=>9.7,'logo'=>14.8]],
][$L];
$T = [
 'es' => ['ti'=>'Membresía <b>ANUAL</b>','sub'=>'La mejor decisión para ti y tu equipo','earn'=>'💰 ¿Cuánto puedes ganar?',
   'ah'=>'El <b>ahorro</b>','men'=>'🗓️ MENSUAL','ano'=>'al año','anu'=>'👑 ANUAL','once'=>'un solo pago · 12 meses','save'=>'AHORRAS 140 USDT',
   'bh'=>'12 meses de <b>beneficios</b>','ben'=>[['🛒','Marketplace','Tu tienda y anuncios destacados'],['💼','Contrátame','Publica ofertas de empleo'],['🤖','Videos Virales','Herramientas con inteligencia artificial'],['🏪','Portada PRO','Tu negocio en un solo link'],['🎓','Gana con Marketing','Todos los cursos'],['✨','¡Y mucho más!','Todas las herramientas nuevas que salgan']],
   'pase'=>'👑 Pase anual',
   'rh'=>'Recibes de <b>las dos</b> membresías','tu'=>'TÚ','tan'=>'👑 ANUAL','gm'=>'🗓️ Mensual','ga'=>'👑 Anual','cmp'=>'🔒 Con la mensual solo recibes pagos de 20',
   'eh'=>'Ejemplo: tus <b>10 directos</b>','paga'=>'TE PAGA','tot'=>'Recibes','totb'=>'TOTAL',
   'nh'=>'Tu equipo <b>crece</b>','nd'=>'5 directos','ni'=>'15 indirectos','ca'=>'👑 Si todos eligen la anual','cau'=>'USDT por adelantado','cm'=>'🗓️ Si eligen la mensual','cmu'=>'USDT cada mes que renueven','both'=>'✓ Con la anual recibes de las dos',
   'fh'=>'Con la mensual hay un <b>freno</b>','fh2'=>'Con la anual, tu equipo avanza <b>sin frenos</b>','bm'=>'🗓️ MENSUAL','ba'=>'👑 ANUAL','want'=>'Quiero la 👑 anual','lose'=>'−100 USDT','refe'=>'Referido',
   'ch'=>'Cámbiate hoy a la <b>ANUAL</b>','cc'=>['💸 Ahorras 140 USDT','🎁 12 meses de beneficios','💰 Recibes pagos de 20 y de 100'],'disc'=>'Ejemplos ilustrativos: dependen de que tu equipo crezca y mantenga su membresía.'],
 'en' => ['ti'=>'<b>ANNUAL</b> Membership','sub'=>'The best decision for you and your team','earn'=>'💰 How much can you earn?',
   'ah'=>'The <b>savings</b>','men'=>'🗓️ MONTHLY','ano'=>'a year','anu'=>'👑 ANNUAL','once'=>'one payment · 12 months','save'=>'SAVE 140 USDT',
   'bh'=>'12 months of <b>benefits</b>','ben'=>[['🛒','Marketplace','Your store and featured listings'],['💼','Contrátame','Post job offers'],['🤖','Videos Virales','Artificial intelligence tools'],['🏪','PRO Page','Your business in one link'],['🎓','Gana con Marketing','All the courses'],['✨','And much more!','Every new tool we release']],
   'pase'=>'👑 Annual pass',
   'rh'=>'You receive from <b>both</b> memberships','tu'=>'YOU','tan'=>'👑 ANNUAL','gm'=>'🗓️ Monthly','ga'=>'👑 Annual','cmp'=>'🔒 With the monthly plan you only receive 20 USDT payments',
   'eh'=>'Example: your <b>10 direct referrals</b>','paga'=>'PAYS YOU','tot'=>'You receive','totb'=>'TOTAL',
   'nh'=>'Your team <b>grows</b>','nd'=>'5 direct','ni'=>'15 indirect','ca'=>'👑 If all choose annual','cau'=>'USDT in advance','cm'=>'🗓️ If they choose monthly','cmu'=>'USDT every month they renew','both'=>'✓ With the annual plan you receive from both',
   'fh'=>'With the monthly plan there is a <b>limit</b>','fh2'=>'With the annual plan, your team moves <b>without limits</b>','bm'=>'🗓️ MONTHLY','ba'=>'👑 ANNUAL','want'=>'I want the 👑 annual','lose'=>'−100 USDT','refe'=>'Referral',
   'ch'=>'Switch to the <b>ANNUAL</b> today','cc'=>['💸 Save 140 USDT','🎁 12 months of benefits','💰 Receive 20 and 100 USDT payments'],'disc'=>'Illustrative examples: they depend on your team growing and keeping their membership.'],
][$L];
$mask = fn(string $html, float $d) => '<span class="a-mask" style="--d:' . $d . 's"><i>' . $html . '</i></span>';
$rise = fn(string $html, float $d) => '<span class="a-rise" style="--d:' . $d . 's"><i>' . $html . '</i></span>';
$x = $C['intro'];
?>
      <!-- 1. INTRO -->
      <section class="svt-scene svt-dark sva-col pz" data-k="a-intro">
        <img class="an-logo a-zoom" src="/sumiago/assets/img/logo-sumiago-light.png" alt="" style="--d:.2s">
        <div class="an-crown a-spin" style="--d:<?= $x['crown'] ?>s">👑</div>
        <div class="an-big"><?= $mask($T['ti'], $x['t']) ?></div>
        <div class="an-sub"><?= $rise($T['sub'], $x['sub']) ?></div>
        <div class="an-team"><?php foreach (['w','g','r','g','w'] as $i => $c): ?><div class="a-pop" style="--d:<?= $x['team'] + $i * .15 ?>s"><?= $fig($c . ($c === 'r' ? ' yay' : ''), '') ?></div><?php endforeach; ?></div>
        <div class="an-earn a-pop" style="--d:<?= $x['earn'] ?>s"><?= $T['earn'] ?></div>
      </section>

      <?php $x = $C['ahorro']; ?>
      <!-- 2. AHORRO: los 12 pagos de 20 se transforman en un solo pago de 100 -->
      <section class="svt-scene sva-col pz" data-k="a-ahorro">
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago.png" alt="">
        <div class="sva-h"><?= $mask($T['ah'], $x['h']) ?></div>
        <div class="an-ah">
          <div class="an-mens">
            <div class="an-mt a-pop" style="--d:<?= $x['tiles'] - .3 ?>s"><?= $T['men'] ?></div>
            <div class="an-tiles">
              <?php for ($i = 0; $i < 12; $i++): $c = $i % 4; $r = intdiv($i, 4); ?>
                <span class="an-tile" style="--d:<?= $x['tiles'] + $i * .17 ?>s;--d2:<?= $x['a'] + .1 + $i * .05 ?>s;--dx:<?= 47 - $c * 7.2 ?>cqw;--dy:<?= 4 - $r * 9 ?>cqh">20</span>
              <?php endfor; ?>
            </div>
            <div class="an-sum a-up" style="--d:<?= $x['sum'] - .2 ?>s"><b><span class="svt-num" data-from="0" data-to="240" data-at="<?= $x['sum'] ?>">0</span> USDT</b> <?= $T['ano'] ?></div>
          </div>
          <div class="an-yr a-pop" style="--d:<?= $x['a'] + .75 ?>s">
            <small><?= $T['anu'] ?></small>
            <b><span class="svt-num" data-from="0" data-to="100" data-at="<?= $x['n100'] ?>">0</span><em>USDT</em></b>
            <span><?= $rise($T['once'], $x['once']) ?></span>
            <span class="sva-stamp a-stamp an-st" style="--d:<?= $x['stamp'] ?>s"><?= $T['save'] ?></span>
          </div>
        </div>
      </section>

      <?php $x = $C['beneficios']; $n = count($T['ben']); $tot = $x['out'] + 1.4;
        // la cámara sigue el pase anual de tarjeta en tarjeta y al final se aleja
        $kf = ['0%' => [-0, 1]]; $pos = fn($i) => 50 + $i * 46; // centro de cada tarjeta en cqw dentro del mundo
        $cam = []; $tok = [];
        $cam[] = [0, 50 - $pos(0), 1]; $tok[] = [0, $pos(0)];
        foreach ($x['c'] as $i => $t) { $a = max(0, $t - .7); $cam[] = [$a, 50 - $pos(max(0, $i - 1)), 1]; $cam[] = [$t, 50 - $pos($i), 1]; $tok[] = [$a, $pos(max(0, $i - 1))]; $tok[] = [$t, $pos($i)]; }
        $wd = $pos($n - 1) + 50; $sc = round(100 / $wd, 3);
        $cam[] = [$x['out'], 50 - $pos($n - 1), 1]; $cam[] = [$x['out'] + 1.2, 0, $sc]; $tok[] = [$x['out'], $pos($n - 1)];
        $cam[] = [$tot, 0, $sc]; $tok[] = [$tot, $pos($n - 1)];
        $kcam = ''; foreach ($cam as [$t, $dx, $s]) $kcam .= round($t / $tot * 100, 2) . '%{transform:translateX(' . round($dx, 2) . 'cqw) scale(' . $s . ')}';
        $ktok = ''; foreach ($tok as [$t, $lx]) $ktok .= round($t / $tot * 100, 2) . '%{left:' . round($lx, 2) . 'cqw}';
      ?>
      <!-- 3. BENEFICIOS: la cámara sigue el pase anual -->
      <style>@keyframes anCam_<?= $L ?>{<?= $kcam ?>}@keyframes anTok_<?= $L ?>{<?= $ktok ?>}
      .svt-scene.on .an-world.<?= $L ?>{animation:anCam_<?= $L ?> <?= $tot ?>s cubic-bezier(.65,0,.35,1) 0s both}
      .svt-scene.on .an-world.<?= $L ?> .an-tok{animation:anTok_<?= $L ?> <?= $tot ?>s cubic-bezier(.65,0,.35,1) 0s both}</style>
      <section class="svt-scene svt-dark pz an-cam" data-k="a-beneficios">
        <div class="an-world <?= $L ?>" style="width:<?= $wd ?>cqw">
          <?php foreach ($T['ben'] as $i => $b): ?>
            <div class="an-bn a-pop" style="left:<?= $pos($i) ?>cqw;--d:<?= max(.1, $x['c'][$i] - .5) ?>s"><span><?= $b[0] ?></span><b><?= $b[1] ?></b><small><?= $b[2] ?></small></div>
          <?php endforeach; ?>
          <div class="an-tok"><?= $T['pase'] ?></div>
        </div>
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago-light.png" alt="">
        <div class="sva-h sva-h-d sva-h-top"><?= $mask($T['bh'], $x['h']) ?></div>
      </section>

      <?php $x = $C['recibes']; ?>
      <!-- 4. RECIBES DE LAS DOS -->
      <section class="svt-scene sva-col pz" data-k="a-recibes">
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago.png" alt="">
        <div class="sva-h"><?= $mask($T['rh'], $x['h']) ?></div>
        <div class="an-rc">
          <div class="an-grp m a-pop" style="--d:<?= $x['m'] ?>s"><div class="an-fs"><?= $fig('w', '') ?><?= $fig('w', '') ?></div><span><?= $T['gm'] ?></span></div>
          <div class="an-yo a-pop" style="--d:<?= $x['yo'] ?>s"><?= $fig('r big yay', $T['tu']) ?><span class="an-badge"><?= $T['tan'] ?></span>
            <span class="an-plus m a-pop" style="--d:<?= $x['c20'] + .9 ?>s">+20</span><span class="an-plus a a-pop" style="--d:<?= $x['c100'] + .9 ?>s">+100</span></div>
          <div class="an-grp a a-pop" style="--d:<?= $x['a'] ?>s"><div class="an-fs"><?= $fig('g', '') ?><?= $fig('g', '') ?></div><span><?= $T['ga'] ?></span></div>
          <span class="an-coin l" style="--d:<?= $x['c20'] ?>s">💵 20</span>
          <span class="an-coin r" style="--d:<?= $x['c100'] ?>s">💵 100</span>
        </div>
        <div class="an-cmp a-up" style="--d:<?= $x['cmp'] ?>s"><?= $T['cmp'] ?></div>
      </section>

      <?php $x = $C['ejemplo']; $pag = [2 => 0, 4 => 1, 6 => 2, 8 => 3, 9 => 4]; $anu = [2, 4, 6]; ?>
      <!-- 5. EJEMPLO 10 DIRECTOS -->
      <section class="svt-scene sva-col pz" data-k="a-ejemplo">
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago.png" alt="">
        <div class="sva-h"><?= $mask($T['eh'], $x['h']) ?></div>
        <div class="an-row">
          <?php for ($p = 1; $p <= 10; $p++): $pg = isset($pag[$p]); $an = in_array($p, $anu, true); ?>
            <div class="an-pos a-pop" style="--d:<?= $x['pop'] + $p * .08 ?>s">
              <div class="an-c<?= $pg ? ' pay' : '' ?>" style="--d:<?= $pg ? $x['p'][$pag[$p]] : 0 ?>s"><?= $p ?></div>
              <?php if ($pg): ?>
                <small class="a-up" style="--d:<?= $x['p'][$pag[$p]] + .1 ?>s"><?= $T['paga'] ?></small>
                <span class="an-tag <?= $an ? 'a' : 'm' ?> a-pop" style="--d:<?= ($an ? $x['ta'] : $x['tm']) + ($an ? array_search($p, $anu) * .15 : ($p - 8) * .15) ?>s"><?= $an ? '👑 100' : '🗓️ 20' ?></span>
                <span class="an-drop" style="--d:<?= ($an ? $x['c300'] + array_search($p, $anu) * .2 : $x['c340'] + ($p - 8) * .2) ?>s">💵</span>
              <?php endif; ?>
            </div>
          <?php endfor; ?>
        </div>
        <div class="an-tot a-pop" style="--d:<?= $x['c300'] - .4 ?>s"><small><?= $T['tot'] ?></small><b><span class="svt-num" data-from="0" data-to="300" data-at="<?= $x['c300'] + .5 ?>" data-to2="340" data-at2="<?= $x['c340'] + .5 ?>">0</span> USDT</b>
          <span class="sva-stamp a-stamp an-st2" style="--d:<?= $x['tot'] ?>s"><?= $T['totb'] ?> 340 USDT</span></div>
      </section>

      <?php $x = $C['red']; ?>
      <!-- 6. RED: la cámara se aleja y muestra a las 20 personas que te pagan -->
      <section class="svt-scene svt-dark pz" data-k="a-red">
        <div class="an-net" style="--d:<?= $x['dir'] - .6 ?>s">
          <div class="an-nyo"><?= $fig('r big', $T['tu']) ?></div>
          <svg class="an-nl a-draw" viewBox="0 0 100 100" preserveAspectRatio="none" style="--d:<?= $x['dir'] - .3 ?>s"><path d="M50 14 V30 M10 30 H90 M10 30 V40 M30 30 V40 M50 30 V40 M70 30 V40 M90 30 V40"/></svg>
          <div class="an-nd"><?php for ($i = 0; $i < 5; $i++): ?><div class="a-pop" style="--d:<?= $x['dir'] + $i * .12 ?>s"><?= $fig('w', '') ?><span class="an-pay">💵</span></div><?php endfor; ?></div>
          <div class="an-ni"><?php for ($i = 0; $i < 15; $i++): ?><div class="a-pop" style="--d:<?= $x['ind'] + $i * .05 ?>s"><?= $fig('g sm', '') ?><span class="an-pay">💵</span></div><?php endfor; ?></div>
          <div class="an-lab a-up" style="--d:<?= $x['dir'] + .3 ?>s;top:46%"><?= $T['nd'] ?></div>
          <div class="an-lab a-up" style="--d:<?= $x['ind'] + .5 ?>s;top:80%"><?= $T['ni'] ?></div>
        </div>
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago-light.png" alt="">
        <div class="sva-h sva-h-d sva-h-top"><?= $mask($T['nh'], $x['h']) ?></div>
        <div class="an-opts">
          <div class="an-op a a-pop" style="--d:<?= $x['ca'] ?>s"><small><?= $T['ca'] ?></small><b><span class="svt-num" data-from="0" data-to="2000" data-at="<?= $x['n2000'] ?>">0</span></b><em><?= $T['cau'] ?></em></div>
          <div class="an-op m a-pop" style="--d:<?= $x['cm'] ?>s"><small><?= $T['cm'] ?></small><b><span class="svt-num" data-from="0" data-to="400" data-at="<?= $x['n400'] ?>">0</span></b><em><?= $T['cmu'] ?></em></div>
          <div class="an-both a-pop" style="--d:<?= $x['both'] ?>s"><?= $T['both'] ?></div>
        </div>
      </section>

      <?php $x = $C['frenos']; ?>
      <!-- 7. SIN FRENOS: el candado se transforma y el equipo avanza -->
      <section class="svt-scene svt-dark sva-col pz" data-k="a-frenos">
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago-light.png" alt="">
        <div class="an-fh">
          <div class="sva-h sva-h-d an-fh1" style="--d2:<?= $x['an'] - .1 ?>s"><?= $mask($T['fh'], $x['h']) ?></div>
          <div class="sva-h sva-h-d an-fh2"><?= $mask($T['fh2'], $x['an']) ?></div>
        </div>
        <div class="an-fr">
          <div class="an-fyo a-pop" style="--d:<?= $x['yo'] ?>s"><?= $fig('r big', $T['tu']) ?>
            <span class="sva-flip" style="--d:<?= $x['an'] ?>s"><span class="f"><?= $T['bm'] ?></span><span class="b"><?= $T['ba'] ?></span></span></div>
          <div class="an-lock" style="--d:<?= $x['lock'] ?>s;--d2:<?= $x['an'] ?>s"><span class="c">🔒</span><span class="o">🔓</span></div>
          <span class="an-lose" style="--d:<?= $x['lose'] ?>s"><?= $T['lose'] ?></span>
          <div class="an-fref a-pop" style="--d:<?= $x['ref'] ?>s"><span class="svr-say a-pop" style="--d:<?= $x['ref'] + .4 ?>s"><?= $T['want'] ?></span><?= $fig('w big', $T['refe']) ?></div>
          <span class="an-flow" style="--d:<?= $x['an'] + .7 ?>s">💵 100</span>
        </div>
        <div class="an-ups"><?php for ($i = 0; $i < 7; $i++): ?><div class="a-pop" style="--d:<?= $x['go'] + $i * .12 ?>s"><?= $fig($i % 2 ? 'g sm yay' : 'w sm', '') ?><span>⬆</span></div><?php endfor; ?></div>
      </section>

      <?php $x = $C['cierre']; ?>
      <!-- 8. CIERRE -->
      <section class="svt-scene svt-dark sva-col pz" data-k="a-cierre">
        <div class="an-big"><?= $mask($T['ch'], $x['h']) ?></div>
        <div class="an-cc"><?php foreach ($T['cc'] as $i => $c): ?><span class="a-pop" style="--d:<?= $x['c'][$i] ?>s"><?= $c ?></span><?php endforeach; ?></div>
        <div class="an-disc"><?= $rise($T['disc'], $x['disc']) ?></div>
        <img class="an-endlogo a-zoom" src="/sumiago/assets/img/logo-sumiago-light.png" alt="" style="--d:<?= $x['logo'] ?>s">
        <?php for ($i = 0; $i < 14; $i++): ?><span class="svt-conf a-fall" style="left:<?= 4 + $i * 7 ?>%;--d:<?= $x['c'][0] + ($i % 5) * .3 ?>s;background:<?= ['#e10600', '#fff', '#facc15', '#a1a1aa'][$i % 4] ?>"></span><?php endfor; ?>
      </section>

<style>
.an-logo{height:8cqh;margin-bottom:3cqh}
.an-crown{font-size:10cqw;line-height:1;filter:drop-shadow(0 0 3cqw rgba(250,204,21,.55))}
.an-big{font-size:5cqw;font-weight:900;color:#fff;text-align:center;line-height:1.1}.an-big b{color:#ffd76a}
.an-sub{font-size:2.2cqw;font-weight:700;color:#e4e4e7;margin-top:1.4cqh}
.an-team{display:flex;gap:2cqw;margin-top:3cqh}.an-team .svt-fig svg{width:5cqw}
.an-earn{margin-top:3cqh;background:linear-gradient(135deg,#ffe28a,#f5b400);color:#1a1200;font-weight:900;font-size:2cqw;border-radius:999px;padding:1.4cqh 2.6cqw;box-shadow:0 12px 30px rgba(245,180,0,.45)}
/* ahorro */
.an-ah{display:grid;grid-template-columns:1.2fr 1fr;gap:5cqw;width:80cqw;align-items:center}
.an-mens{background:#fff;border:2px solid #e4e4e7;border-radius:24px;padding:3cqh 2cqw;text-align:center;box-shadow:0 16px 40px rgba(0,0,0,.08)}
.an-mt{font-weight:900;color:#e10600;font-size:1.8cqw;letter-spacing:.12em;margin-bottom:2cqh}
.an-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:1cqw}
.an-tile{display:flex;align-items:center;justify-content:center;height:7cqh;border-radius:12px;background:#fef2f2;border:2px solid #fecaca;color:#e10600;font-weight:900;font-size:2.2cqw;opacity:0}
.svt-scene.on .an-tile{animation:svtPop .45s cubic-bezier(.2,.9,.3,1.4) var(--d) both,anFly .9s cubic-bezier(.6,0,.4,1) var(--d2) forwards}
@keyframes anFly{0%{opacity:1;transform:none}100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.3) rotate(25deg)}}
.an-sum{margin-top:2.4cqh;font-size:2cqw;font-weight:700;color:#52525b}.an-sum b{color:#0a0a0a;font-size:3cqw}
.an-yr{position:relative;background:radial-gradient(circle at 80% -10%,rgba(255,215,106,.35),transparent 45%),linear-gradient(140deg,#0a0a0a,#2b0000 55%,#b10000);color:#fff;border:3px solid #f5b400;border-radius:26px;padding:5cqh 2cqw;text-align:center;display:flex;flex-direction:column;gap:1cqh;box-shadow:0 24px 60px rgba(225,6,0,.4)}
.an-yr small{font-weight:900;letter-spacing:.14em;color:#ffd76a;font-size:1.9cqw}
.an-yr b{font-size:8cqw;line-height:1;font-weight:900}.an-yr b em{font-style:normal;font-size:2cqw;margin-left:.6cqw}
.an-yr>span{font-size:1.8cqw;font-weight:700;color:#fde68a}
.an-st{left:auto;right:-3cqw;top:-4cqh;font-size:2cqw;background:#16a34a!important;color:#fff!important;border-color:#fff!important;box-shadow:0 10px 26px rgba(22,163,74,.5)}
/* beneficios con cámara */
.an-cam{padding:0!important}
.an-world{position:absolute;left:0;top:0;height:100cqh;transform-origin:0 50%}
.an-bn{position:absolute;top:50cqh;width:36cqw;margin-left:-18cqw;transform-origin:50% 50%;translate:0 -50%;background:#fff;color:#0a0a0a;border-radius:28px;padding:5cqh 2cqw;display:flex;flex-direction:column;align-items:center;gap:1.4cqh;text-align:center;box-shadow:0 30px 70px rgba(0,0,0,.45)}
.an-bn span{font-size:9cqw;line-height:1}.an-bn b{font-size:3.4cqw;color:#e10600}.an-bn small{font-size:2cqw;color:#3f3f46;font-weight:600}
.an-tok{position:absolute;top:80cqh;transform:translateX(-50%);background:linear-gradient(135deg,#ffe28a,#f5b400);color:#1a1200;font-weight:900;font-size:2.2cqw;border-radius:999px;padding:1.4cqh 2.4cqw;white-space:nowrap;box-shadow:0 0 3cqw rgba(245,180,0,.6)}
/* recibes */
.an-rc{position:relative;display:grid;grid-template-columns:1fr 1fr 1fr;align-items:center;width:84cqw;height:48cqh}
.an-grp{display:flex;flex-direction:column;align-items:center;gap:1.4cqh}
.an-fs{display:flex;gap:1cqw}.an-fs .svt-fig svg{width:6.6cqw}
.an-grp span{font-weight:900;font-size:2cqw;border-radius:999px;padding:1cqh 2cqw}
.an-grp.m span{background:#e4e4e7;color:#3f3f46}.an-grp.a span{background:linear-gradient(135deg,#ffe28a,#f5b400);color:#1a1200}
.an-yo{position:relative;display:flex;flex-direction:column;align-items:center;gap:1.4cqh}.an-yo .svt-fig svg{width:10cqw}
.an-badge{background:linear-gradient(135deg,#ffe28a,#f5b400);color:#1a1200;font-weight:900;font-size:1.9cqw;border-radius:999px;padding:.9cqh 1.8cqw}
.an-plus{position:absolute;top:2cqh;font-weight:900;font-size:3cqw;border-radius:999px;padding:.8cqh 1.6cqw;color:#fff}
.an-plus.m{left:-7cqw;background:#52525b}.an-plus.a{right:-8cqw;background:#16a34a}
.an-coin{position:absolute;top:44%;font-size:2.6cqw;font-weight:900;background:#fff;border-radius:999px;padding:1cqh 1.6cqw;box-shadow:0 0 0 .6cqw rgba(74,222,128,.35),0 10px 24px rgba(0,0,0,.25);opacity:0}
.an-coin.l{left:14%}.an-coin.r{left:76%}
.svt-scene.on .an-coin.l{animation:anCoinL 1s cubic-bezier(.5,0,.3,1) var(--d) both}
.svt-scene.on .an-coin.r{animation:anCoinR 1s cubic-bezier(.5,0,.3,1) var(--d) both}
@keyframes anCoinL{0%{opacity:0;transform:none}15%{opacity:1}60%{transform:translate(18cqw,-10cqh) scale(1.1)}100%{opacity:0;transform:translate(30cqw,0) scale(.4)}}
@keyframes anCoinR{0%{opacity:0;transform:none}15%{opacity:1}60%{transform:translate(-18cqw,-10cqh) scale(1.1)}100%{opacity:0;transform:translate(-28cqw,0) scale(.4)}}
.an-cmp{margin-top:3cqh;background:#f4f4f5;border:2px dashed #a1a1aa;color:#52525b;font-weight:800;font-size:1.9cqw;border-radius:999px;padding:1.4cqh 2.6cqw}
/* ejemplo */
.an-row{display:grid;grid-template-columns:repeat(10,1fr);gap:1.2cqw;width:86cqw}
.an-pos{position:relative;display:flex;flex-direction:column;align-items:center;gap:1cqh;height:30cqh}
.an-c{width:6.6cqw;height:6.6cqw;border-radius:50%;background:#d4d4d8;color:#fff;font-weight:900;font-size:3cqw;display:flex;align-items:center;justify-content:center}
.svt-scene.on .an-c.pay{animation:anPay .6s cubic-bezier(.2,.9,.3,1.4) var(--d) both}
@keyframes anPay{from{background:#d4d4d8;transform:scale(1)}50%{transform:scale(1.25)}to{background:#e10600;transform:scale(1.08);box-shadow:0 0 0 .6cqw rgba(225,6,0,.2)}}
.an-pos small{font-weight:900;font-size:1.1cqw;color:#e10600;letter-spacing:.06em}
.an-tag{font-weight:900;font-size:1.3cqw;border-radius:999px;padding:.6cqh .8cqw;white-space:nowrap}
.an-tag.a{background:linear-gradient(135deg,#ffe28a,#f5b400);color:#1a1200}.an-tag.m{background:#e4e4e7;color:#3f3f46}
.an-drop{position:absolute;top:14cqh;font-size:3cqw;opacity:0}
.svt-scene.on .an-drop{animation:anDrop 1s cubic-bezier(.5,0,.6,1) var(--d) both}
@keyframes anDrop{0%{opacity:0;transform:none}15%{opacity:1}100%{opacity:0;transform:translateY(26cqh) scale(.5)}}
.an-tot{position:relative;margin-top:2cqh;background:#0a0a0a;color:#fff;border-radius:24px;padding:2.4cqh 4cqw;text-align:center;box-shadow:0 20px 50px rgba(0,0,0,.25)}
.an-tot small{display:block;color:#a1a1aa;font-weight:800;letter-spacing:.12em;font-size:1.4cqw}.an-tot b{font-size:5cqw;color:#4ade80}
.an-st2{left:auto;right:-10cqw;top:-3cqh;font-size:1.8cqw;background:#16a34a!important;color:#fff!important;border-color:#fff!important}
/* red */
.an-net{position:absolute;left:4cqw;top:16cqh;width:52cqw;height:76cqh;transform-origin:50% 8%}
.svt-scene.on .an-net{animation:anZoomOut 1.6s cubic-bezier(.65,0,.35,1) var(--d) both}
@keyframes anZoomOut{from{transform:scale(2.1)}to{transform:none}}
.an-nyo{position:absolute;left:50%;top:0;transform:translateX(-50%)}.an-nyo .svt-fig svg{width:6cqw}
.an-nl{position:absolute;left:0;top:0;width:100%;height:100%}.an-nl path{fill:none;stroke:rgba(255,255,255,.3);stroke-width:2px;vector-effect:non-scaling-stroke}
.an-nd{position:absolute;left:0;right:0;top:32%;display:flex;justify-content:space-between;padding:0 3%}
.an-nd>div,.an-ni>div{position:relative;display:flex;flex-direction:column;align-items:center}.an-nd .svt-fig svg{width:5cqw}
.an-ni{position:absolute;left:0;right:0;top:62%;display:grid;grid-template-columns:repeat(15,1fr)}.an-ni .svt-fig svg{width:3cqw}
.an-pay{position:absolute;top:-2.6cqh;font-size:1.6cqw}
.an-lab{position:absolute;left:0;right:0;text-align:center;font-weight:900;font-size:1.8cqw;color:#ffd76a}
.an-opts{position:absolute;right:4cqw;top:20cqh;width:36cqw;display:flex;flex-direction:column;gap:2.2cqh}
.an-op{border-radius:22px;padding:2.2cqh 2cqw;text-align:center}
.an-op.a{background:linear-gradient(135deg,#ffe28a,#f5b400);color:#1a1200}.an-op.m{background:#fff;color:#0a0a0a}
.an-op small{display:block;font-weight:900;font-size:1.6cqw}.an-op b{display:block;font-size:5.4cqw;line-height:1.1;font-weight:900}.an-op em{font-style:normal;font-weight:700;font-size:1.5cqw}
.an-op.m b{color:#e10600}
.an-both{background:#16a34a;color:#fff;font-weight:900;font-size:1.7cqw;border-radius:999px;padding:1.4cqh 1.6cqw;text-align:center}
/* frenos */
.an-fh{position:relative;width:90cqw;height:12cqh}
.an-fh .sva-h{position:absolute;left:0;right:0;top:0}
.svt-scene.on .an-fh1{animation:svtFade .4s ease var(--d2) forwards}
.an-fr{position:relative;display:flex;align-items:center;justify-content:space-between;width:74cqw;height:44cqh}
.an-fyo,.an-fref{display:flex;flex-direction:column;align-items:center;gap:1.4cqh;z-index:2}
.an-fyo .sva-flip{width:22cqw}
.an-lock{position:absolute;left:50%;top:38%;width:12cqw;height:12cqw;margin:-6cqw 0 0 -6cqw;perspective:60cqw;opacity:0}
.an-lock span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:10cqw;backface-visibility:hidden}
.an-lock .o{transform:rotateY(180deg)}
.svt-scene.on .an-lock{animation:svtPop .5s cubic-bezier(.2,.9,.3,1.4) var(--d) both,anLockAway .9s ease calc(var(--d2) + .7s) forwards}
.svt-scene.on .an-lock .c{animation:svaFlipF .6s ease var(--d2) both}
.svt-scene.on .an-lock .o{animation:svaFlipB .6s ease var(--d2) both}
@keyframes anLockAway{to{opacity:0;transform:translateY(-30cqh) scale(.4) rotate(-30deg)}}
.an-lose{position:absolute;left:50%;top:70%;transform:translateX(-50%);background:#e10600;color:#fff;font-weight:900;font-size:2.4cqw;border-radius:999px;padding:1cqh 2cqw;opacity:0}
.svt-scene.on .an-lose{animation:svtPop .5s cubic-bezier(.2,.9,.3,1.4) var(--d) both,svaShake .6s ease calc(var(--d) + .5s) both,svtFade .4s ease calc(var(--d) + 1.6s) forwards}
.an-flow{position:absolute;left:70%;top:36%;font-size:2.4cqw;font-weight:900;background:#fff;color:#16a34a;border-radius:999px;padding:1cqh 1.6cqw;opacity:0}
.svt-scene.on .an-flow{animation:anFlow 1.2s cubic-bezier(.5,0,.3,1) var(--d) both}
@keyframes anFlow{0%{opacity:0;transform:none}15%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateX(-50cqw) scale(.6)}}
.an-ups{display:flex;gap:2.4cqw;margin-top:1cqh}.an-ups>div{display:flex;flex-direction:column;align-items:center}.an-ups span{color:#4ade80;font-weight:900;font-size:2.6cqw}.an-ups .svt-fig svg{width:4cqw}
/* cierre */
.an-cc{display:flex;gap:1.6cqw;margin-top:4cqh;flex-wrap:wrap;justify-content:center;width:90cqw}
.an-cc span{background:#fff;color:#0a0a0a;font-weight:900;font-size:2.1cqw;border-radius:999px;padding:1.6cqh 2.4cqw;box-shadow:0 14px 34px rgba(0,0,0,.35)}
.an-disc{margin-top:4cqh;font-size:1.5cqw;color:#d4d4d8;font-weight:600;max-width:70cqw;text-align:center}
.an-endlogo{height:12cqh;margin-top:4cqh}
</style>
