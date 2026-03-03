document.addEventListener("DOMContentLoaded", () => {

    function animateRegime(regime) {
        const tag = document.querySelector('.regime-tag');
        
        // Protección: Si no existe el tag, no hacemos nada
        if (!tag) {
            console.warn("⚠️ No se encontró .regime-tag en el HTML");
            return;
        }

        console.log(`🔄 Actualizando UI a régimen: ${regime}`);

        // Limpiamos clases viejas
        tag.classList.remove('RANGING', 'TRENDING', 'UNCERTAIN');
        
        // Agregamos la nueva clase
        tag.classList.add(regime);

        // Truco para reiniciar la animación CSS (reflow)
        tag.classList.remove('active');
        void tag.offsetWidth; 
        tag.classList.add('active');
    }

    // 1. Cargar estado inicial si Django lo mandó
    // Asegúrate de definir window.DASHBOARD_DATA en tu HTML si quieres esto
    if (window.DASHBOARD_DATA && window.DASHBOARD_DATA.regime) {
        animateRegime(window.DASHBOARD_DATA.regime);
    }

    // 2. Exponer la función para que websocket.js la pueda usar
    window.updateRegime = animateRegime;
});
