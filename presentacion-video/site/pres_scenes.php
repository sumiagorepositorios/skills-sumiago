<?php
/* Escenas nuevas de la Presentación (2 membresías, regla, cámbiate). Tiempos relativos al inicio de la voz. */
$L = $presLang;
$C = [
 'es' => ['planes' => ['h'=>.6,'m'=>2.1,'n20'=>3.0,'d30'=>4.4,'a'=>5.5,'n100'=>6.2,'m12'=>7.5,'once'=>8.5,'save'=>10.0,'b'=>[13.0,14.8,16.7,18.2,20.7],'morph'=>22.75],
          'regla' => ['lock'=>1.6,'h'=>1.8,'yo'=>5.9,'badge'=>6.8,'ref'=>7.7,'line'=>7.9,'say'=>8.7,'btn'=>9.0,'cur'=>8.8,'press'=>9.6,'x'=>10.3,'dim'=>11.3,'alert'=>11.4,'at'=>12.9,'wa'=>14.4],
          'cambiate' => ['h'=>.3,'flip'=>1.0,'down'=>2.4,'ups'=>2.8,'coin'=>4.2,'plus'=>7.0,'out'=>7.7,'com'=>8.2,'crown'=>8.0,'any'=>9.4,'anyt'=>9.6,'small'=>11.1,'note'=>13.2]],
 'en' => ['planes' => ['h'=>.6,'m'=>1.6,'n20'=>2.4,'d30'=>3.8,'a'=>4.6,'n100'=>5.4,'m12'=>7.0,'once'=>7.9,'save'=>9.3,'b'=>[12.6,14.2,16.3,18.2,21.0],'morph'=>23.3],
          'regla' => ['lock'=>1.6,'h'=>1.8,'yo'=>5.5,'badge'=>6.1,'ref'=>7.6,'line'=>7.8,'say'=>8.6,'btn'=>8.9,'cur'=>8.7,'press'=>9.5,'x'=>10.5,'dim'=>11.7,'alert'=>11.8,'at'=>12.6,'wa'=>14.1],
          'cambiate' => ['h'=>.3,'flip'=>1.4,'down'=>3.0,'ups'=>3.4,'coin'=>4.7,'plus'=>7.5,'out'=>8.3,'com'=>8.8,'crown'=>8.6,'any'=>10.0,'anyt'=>10.2,'small'=>11.2,'note'=>14.0]],
][$L];
$T = [
 'es' => ['dos'=>'Dos <b>membresías</b>','men'=>'MENSUAL','anu'=>'ANUAL','d30'=>'dura 30 días','m12'=>'dura 12 meses','once'=>'💳 Pagas una sola vez','save'=>'AHORRAS 140 USDT','rib'=>'MEJOR VALOR',
   'ben'=>['🎓 Cursos Gana con Marketing','🔗 Tu enlace para invitar','🤝 Recibes Sumiagos de tu red','🌳 Tu panel: árbol, pagos y rango','🏆 Rangos y Sueldo Mensual'],
   'rh'=>'Solo la <b>ANUAL</b> recibe pagos de la <b>ANUAL</b>','tu'=>'TÚ','bm'=>'🗓️ 20 · MENSUAL','refe'=>'Referido','say'=>'Quiero la de 👑 100','btn'=>'👑 QUIERO LA ANUAL',
   'at'=>'Tu patrocinador debe cambiarse a la <b>ANUAL</b>','ap'=>'Para obtener la anual de <b>100 USDT</b>, tu patrocinador tiene que cambiarse primero.','wa'=>'🟢 CONTACTAR POR WHATSAPP',
   'ch'=>'Cámbiate a la <b>ANUAL</b>','ff'=>'🗓️ 20 MENSUAL','fb'=>'👑 100 ANUAL','com'=>'💰 Tu equipo avanza · <b>más comisiones</b> para ti','any'=>'Cámbiate <b>en cualquier momento</b>','small'=>'sin esperar a que venza tu mensual','note'=>'📊 Los ejemplos que siguen usan la mensual de 20 USDT'],
 'en' => ['dos'=>'Two <b>memberships</b>','men'=>'MONTHLY','anu'=>'ANNUAL','d30'=>'lasts 30 days','m12'=>'lasts 12 months','once'=>'💳 Pay only once','save'=>'SAVE 140 USDT','rib'=>'BEST VALUE',
   'ben'=>['🎓 Gana con Marketing courses','🔗 Your invitation link','🤝 Receive Sumiagos from your network','🌳 Dashboard: tree, payments, rank','🏆 Ranks & Monthly Salary'],
   'rh'=>'Only <b>ANNUAL</b> members receive <b>ANNUAL</b> payments','tu'=>'YOU','bm'=>'🗓️ 20 · MONTHLY','refe'=>'Referral','say'=>'I want the 👑 100','btn'=>'👑 I WANT THE ANNUAL',
   'at'=>'Your sponsor must switch to the <b>ANNUAL</b>','ap'=>'To get the <b>100 USDT</b> annual plan, your sponsor has to switch first.','wa'=>'🟢 CONTACT VIA WHATSAPP',
   'ch'=>'Switch to the <b>ANNUAL</b>','ff'=>'🗓️ 20 MONTHLY','fb'=>'👑 100 ANNUAL','com'=>'💰 Your team moves forward · <b>more commissions</b> for you','any'=>'Switch <b>at any time</b>','small'=>'no need to wait for your monthly to expire','note'=>'📊 The examples that follow use the 20 USDT monthly plan'],
][$L];
$mask = fn(string $html, float $d) => '<span class="a-mask" style="--d:' . $d . 's"><i>' . $html . '</i></span>';
$rise = fn(string $html, float $d) => '<span class="a-rise" style="--d:' . $d . 's"><i>' . $html . '</i></span>';
$p = $C['planes']; $r = $C['regla']; $c = $C['cambiate'];
?>
      <section class="svt-scene sva-col pz" data-k="p-planes">
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago.png" alt="">
        <div class="sva-h"><?= $mask($T['dos'], $p['h']) ?></div>
        <div class="sva-planes">
          <div class="sva-pl m a-pop" style="--d:<?= $p['m'] ?>s">
            <span class="sva-pl-i">🗓️</span><small><?= $T['men'] ?></small>
            <b><span class="svt-num" data-from="0" data-to="20" data-at="<?= $p['n20'] ?>">0</span><em>USDT</em></b>
            <span class="sva-pl-p a-up" style="--d:<?= $p['d30'] ?>s"><?= $T['d30'] ?></span>
          </div>
          <div class="sva-pl a a-pop" style="--d:<?= $p['a'] ?>s">
            <span class="sva-rib"><?= $T['rib'] ?></span>
            <span class="sva-pl-i">👑</span><small><?= $T['anu'] ?></small>
            <b><span class="svt-num" data-from="0" data-to="100" data-at="<?= $p['n100'] ?>">0</span><em>USDT</em></b>
            <span class="sva-pl-p a-up" style="--d:<?= $p['m12'] ?>s"><?= $T['m12'] ?></span>
            <span class="sva-once"><?= $rise($T['once'], $p['once']) ?></span>
            <span class="sva-stamp a-stamp" style="--d:<?= $p['save'] ?>s"><?= $T['save'] ?></span>
          </div>
          <div class="sva-morph" style="--d:<?= $p['morph'] - 1.15 ?>s"><span>👑</span></div>
        </div>
        <div class="sva-ben">
          <?php foreach ($T['ben'] as $i => $b): ?><span class="a-pop" style="--d:<?= $p['b'][$i] ?>s"><?= $b ?></span><?php endforeach; ?>
        </div>
      </section>

      <section class="svt-scene svt-dark sva-col pz" data-k="p-regla">
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago-light.png" alt="">
        <div class="sva-lock" style="--d:<?= $r['lock'] ?>s"><span class="c">👑</span><span class="l">🔒</span></div>
        <div class="sva-h sva-h-d"><?= $mask($T['rh'], $r['h']) ?></div>
        <div class="svr">
          <div class="svr-yo a-pop" style="--d:<?= $r['yo'] ?>s"><?= $fig('r big', $T['tu']) ?><span class="svr-badge a-pop" style="--d:<?= $r['badge'] ?>s"><?= $T['bm'] ?></span></div>
          <svg class="svr-line a-draw" viewBox="0 0 100 10" preserveAspectRatio="none" style="--d:<?= $r['line'] ?>s"><path d="M98 5 H6"/><path d="M12 1 L4 5 L12 9"/></svg>
          <div class="svr-x a-stamp" style="--d:<?= $r['x'] ?>s">✕</div>
          <div class="svr-ref a-pop" style="--d:<?= $r['ref'] ?>s">
            <span class="svr-say a-pop" style="--d:<?= $r['say'] ?>s"><?= $T['say'] ?></span>
            <?= $fig('w big', $T['refe']) ?>
            <span class="svr-btn" style="--d:<?= $r['btn'] ?>s;--d2:<?= $r['press'] ?>s"><?= $T['btn'] ?></span>
          </div>
          <div class="sva-cur svr-cur" style="--d:<?= $r['cur'] ?>s">👆</div>
        </div>
        <div class="svr-dim" style="--d:<?= $r['dim'] ?>s"></div>
        <div class="svr-alert" style="--d:<?= $r['alert'] ?>s">
          <div class="svr-alert-top"><div>👑</div><?= $mask($T['at'], $r['at']) ?></div>
          <div class="svr-alert-b"><p><?= $T['ap'] ?></p><span class="svr-wa a-pop" style="--d:<?= $r['wa'] ?>s"><?= $T['wa'] ?></span></div>
        </div>
      </section>

      <section class="svt-scene svt-dark sva-cam-scene pz" data-k="p-cambiate">
        <div class="sva-view">
          <div class="sva-world" style="--d1:<?= $c['down'] ?>s;--d2:<?= $c['coin'] ?>s;--d3:<?= $c['out'] ?>s">
            <svg class="sva-tree" viewBox="0 0 100 300" preserveAspectRatio="none" aria-hidden="true"><path d="M50 40 V250 M22 110 H78 M22 180 H78 M22 250 H78 M22 110 V102 M78 110 V102 M22 180 V172 M78 180 V172 M22 250 V242 M78 250 V242"/></svg>
            <div class="sva-n yo" style="top:40cqh">
              <?= $fig('r big', $T['tu']) ?>
              <span class="sva-flip" style="--d:<?= $c['flip'] ?>s"><span class="f"><?= $T['ff'] ?></span><span class="b"><?= $T['fb'] ?></span></span>
              <span class="sva-plus a-pop" style="--d:<?= $c['plus'] ?>s">+100 USDT</span>
            </div>
            <?php foreach ([110 => 0, 180 => .35, 250 => .7] as $y => $t): ?>
              <?php foreach ([22, 50, 78] as $j => $x): ?>
              <div class="sva-n" style="top:<?= $y ?>cqh;left:<?= $x ?>%">
                <?= $fig(($j === 1 ? 'g' : 'w') . ' sm' . ($y === 250 && $j === 1 ? ' yay' : ''), '') ?>
                <span class="sva-up a-pop" style="--d:<?= $c['ups'] + $t + $j * .08 ?>s">⬆</span>
                <span class="sva-cr a-pop" style="--d:<?= $c['crown'] + ($y - 110) / 140 + $j * .12 ?>s">👑</span>
              </div>
              <?php endforeach; ?>
            <?php endforeach; ?>
            <div class="sva-coin" style="--d:<?= $c['coin'] ?>s">💵<b>100</b></div>
          </div>
        </div>
        <img class="pz-logo" src="/sumiago/assets/img/logo-sumiago-light.png" alt="">
        <div class="sva-h sva-h-d sva-h-top"><?= $mask($T['ch'], $c['h']) ?></div>
        <div class="sva-com a-pop" style="--d:<?= $c['com'] ?>s"><?= $T['com'] ?></div>
        <div class="sva-any a-pop" style="--d:<?= $c['any'] ?>s">⚡ <?= $rise($T['any'], $c['anyt']) ?><small class="a-up" style="--d:<?= $c['small'] ?>s"><?= $T['small'] ?></small></div>
        <div class="pz-note a-pop" style="--d:<?= $c['note'] ?>s"><?= $T['note'] ?></div>
      </section>
