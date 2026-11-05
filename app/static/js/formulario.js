document.addEventListener('DOMContentLoaded', function() {
    const inputFecha = document.getElementById('fecha_reserva');
    const radiosBarbero = document.querySelectorAll('input[name="barbero"]');
    const radiosHora = document.querySelectorAll('input[name="hora_reserva"]');

    let turnosOcupados = { "Nacho": [], "Luciano": [] };

    function aplicarLogicaBloqueo() {
        radiosHora.forEach(r => r.disabled = false);
        radiosBarbero.forEach(r => r.disabled = false);

        const barberoSeleccionado = document.querySelector('input[name="barbero"]:checked')?.value;
        const horaSeleccionada = document.querySelector('input[name="hora_reserva"]:checked')?.value;

        radiosHora.forEach(radioHora => {
            const hora = radioHora.value;
            const ocupadoNacho = turnosOcupados["Nacho"]?.includes(hora);
            const ocupadoLuciano = turnosOcupados["Luciano"]?.includes(hora);

            if (ocupadoNacho && ocupadoLuciano) {
                radioHora.disabled = true;
                if (radioHora.checked) radioHora.checked = false; 
            }
        });

        if (barberoSeleccionado) {
            const ocupadosDelBarbero = turnosOcupados[barberoSeleccionado] || [];
            radiosHora.forEach(radioHora => {
                if (ocupadosDelBarbero.includes(radioHora.value)) {
                    radioHora.disabled = true;
                    if (radioHora.checked) radioHora.checked = false;
                }
            });
        }

        if (horaSeleccionada) {
            radiosBarbero.forEach(radioBarbero => {
                const nombre = radioBarbero.value;
                if (turnosOcupados[nombre]?.includes(horaSeleccionada)) {
                    radioBarbero.disabled = true;
                    if (radioBarbero.checked) radioBarbero.checked = false;
                }
            });
        }
    }

    // --- 2. COMUNICACIÓN CON EL BACKEND (AJAX) ---
    function buscarDisponibilidad(fecha) {
        // Hacemos una petición silenciosa a nuestra nueva API
        fetch(`/api/disponibilidad/${fecha}`)
            .then(response => response.json())
            .then(data => {
                turnosOcupados = data;
                aplicarLogicaBloqueo(); 
            })
            .catch(error => console.error("Error al buscar disponibilidad:", error));
    }

    if (inputFecha) {
        inputFecha.addEventListener('change', function(e) {
            const date = new Date(e.target.value + 'T00:00:00'); 
            const day = date.getDay();
            if (day === 0 || day === 1) { 
                alert('La barbería permanece cerrada los días domingo y lunes.');
                e.target.value = ''; 
                turnosOcupados = { "Nacho": [], "Luciano": [] };
                aplicarLogicaBloqueo();
                return;
            }
            buscarDisponibilidad(e.target.value);
        });
    }

    radiosBarbero.forEach(r => r.addEventListener('change', aplicarLogicaBloqueo));
    radiosHora.forEach(r => r.addEventListener('change', aplicarLogicaBloqueo));

    const carrusel = document.getElementById('carrusel-horarios');
    const btnIzq = document.getElementById('btn-izq');
    const btnDer = document.getElementById('btn-der');

    if (carrusel && btnIzq && btnDer) {
        btnIzq.addEventListener('click', (e) => { e.preventDefault(); carrusel.scrollBy({ left: -250, behavior: 'smooth' }); });
        btnDer.addEventListener('click', (e) => { e.preventDefault(); carrusel.scrollBy({ left: 250, behavior: 'smooth' }); });
    }
});