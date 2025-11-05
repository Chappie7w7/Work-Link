/**
 * Sistema de notificaciones en tiempo real
 * Actualiza badges de mensajes y notificaciones sin recargar la página
 */

class NotificacionesTiempoReal {
    constructor() {
        this.intervalo = 5000; // Actualizar cada 5 segundos
        this.timerId = null;
        this.init();
    }

    init() {
        // Iniciar actualización automática
        this.actualizarContadores();
        this.timerId = setInterval(() => this.actualizarContadores(), this.intervalo);
        
        // Detener cuando el usuario sale de la página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.detener();
            } else {
                this.reanudar();
            }
        });
    }

    async actualizarContadores() {
        try {
            // Actualizar contador de mensajes
            await this.actualizarMensajes();
            
            // Actualizar contador de notificaciones
            await this.actualizarNotificaciones();
        } catch (error) {
            console.error('Error al actualizar contadores:', error);
        }
    }

    async actualizarMensajes() {
        try {
            const response = await fetch('/api/mensajes/contador');
            const data = await response.json();
            
            const badgeMensajes = document.getElementById('badge-mensajes');
            if (badgeMensajes) {
                if (data.count > 0) {
                    badgeMensajes.textContent = data.count;
                    badgeMensajes.style.display = 'flex';
                    
                    // Animación de pulso
                    badgeMensajes.classList.add('pulse-animation');
                    setTimeout(() => badgeMensajes.classList.remove('pulse-animation'), 1000);
                } else {
                    badgeMensajes.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error al actualizar mensajes:', error);
        }
    }

    async actualizarNotificaciones() {
        try {
            const response = await fetch('/api/notificaciones/contador');
            const data = await response.json();
            
            const badgeNotificaciones = document.getElementById('badge-notificaciones');
            if (badgeNotificaciones) {
                if (data.count > 0) {
                    badgeNotificaciones.textContent = data.count;
                    badgeNotificaciones.style.display = 'flex';
                    
                    // Animación de pulso
                    badgeNotificaciones.classList.add('pulse-animation');
                    setTimeout(() => badgeNotificaciones.classList.remove('pulse-animation'), 1000);
                } else {
                    badgeNotificaciones.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error al actualizar notificaciones:', error);
        }
    }

    detener() {
        if (this.timerId) {
            clearInterval(this.timerId);
            this.timerId = null;
        }
    }

    reanudar() {
        if (!this.timerId) {
            this.actualizarContadores();
            this.timerId = setInterval(() => this.actualizarContadores(), this.intervalo);
        }
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new NotificacionesTiempoReal();
    });
} else {
    new NotificacionesTiempoReal();
}
