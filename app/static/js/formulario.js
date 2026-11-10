document.addEventListener('DOMContentLoaded', function() {
    const inputFecha = document.getElementById('fecha_reserva');
    const radiosBarbero = document.querySelectorAll('input[name="barbero"]');
    const radiosHora = document.querySelectorAll('input[name="hora_reserva"]');

    let turnosOcupados = {};

    function aplicarLogicaBloqueo() {
        radiosHora.forEach(r => r.disabled = false);
        radiosBarbero.forEach(r => r.disabled = false);

        const barberoSeleccionado = document.querySelector('input[name="barbero"]:checked')?.value;
        const horaSeleccionada = document.querySelector('input[name="hora_reserva"]:checked')?.value;

       const cantidadTotalBarberos = radiosBarbero.length;

        radiosHora.forEach(radioHora => {
            const hora = radioHora.value;
            let barberosOcupadosEnEstaHora = 0;

            for (const nombre in turnosOcupados) {
                if (turnosOcupados[nombre].includes(hora)) {
                    barberosOcupadosEnEstaHora++;
                }
            }

            if (barberosOcupadosEnEstaHora >= cantidadTotalBarberos && cantidadTotalBarberos > 0) {
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

    function buscarDisponibilidad(fecha) {
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
                
                turnosOcupados = {};
                radiosBarbero.forEach(r => turnosOcupados[r.value] = []);
                
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