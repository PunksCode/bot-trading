document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');

    // Ajustar al tamaño de la pantalla
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Caracteres: 0 y 1 (Binario puro)
    const chars = '01';
    const charArray = chars.split('');

    const fontSize = 14;
    const columns = canvas.width / fontSize;

    // Array para las gotas (una por columna)
    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = 1;
    }

    function draw() {
        // Fondo negro semi-transparente para crear el efecto de estela
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#0F0'; // Verde Hacker
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            
            // Dibujar el caracter
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Reiniciar la gota al azar si sale de la pantalla
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            drops[i]++;
        }
    }

    // Loop de animación
    setInterval(draw, 33);

    // Redimensionar si cambia la ventana
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
});