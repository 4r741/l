<script>
/* Comprobación en directo del §8: mueve los tres supuestos que gobiernan la
   facturación y recalcula. Se localiza por clase y por data-calc, nunca por
   identificador, para seguir funcionando en el archivo único —donde los
   identificadores van prefijados— y aunque haya varias copias en la página. */
(function(){
  "use strict";
  var DIAS = 21, MESES = 12, BASE = 720;   // escenario base en miles de €

  function mil(n){
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  Array.prototype.forEach.call(document.querySelectorAll(".calc"), function(caja){
    function parte(nombre){ return caja.querySelector('[data-calc="' + nombre + '"]'); }
    var c = parte("c"), t = parte("t"), p = parte("p");
    if(!c || !t || !p) return;

    function pinta(){
      var conv = parseFloat(c.value) / 100,
          tick = parseFloat(t.value),
          pvd  = parseFloat(p.value);
      var pv = pvd * DIAS * MESES,
          casos = pv * conv,
          factur = casos * tick / 1000,      // miles de €
          delta = factur - BASE;

      parte("vc").textContent = c.value + " %";
      parte("vt").textContent = mil(tick) + " €";
      parte("vp").textContent = pvd.toFixed(1).replace(".", ",");

      parte("fact").textContent = mil(factur) + " k€";
      parte("pv").textContent = mil(pv);
      parte("casos").textContent = mil(casos);
      parte("mes").textContent = mil(casos / MESES);
      parte("comp").innerHTML = "Frente al escenario base de " + BASE + " k€: <strong>" +
        (delta >= 0 ? "+" : "\u2212") + " " + mil(Math.abs(delta)) + " k€</strong>";
    }

    [c, t, p].forEach(function(mando){ mando.addEventListener("input", pinta); });
    pinta();
  });
})();
</script>
