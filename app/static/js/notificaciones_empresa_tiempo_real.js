/**
 * Sistema de notificaciones en tiempo real para empresas
 * Actualiza contadores de mensajes y notificaciones sin recargar la página
 */

class NotificacionesEmpresaTiempoReal {
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
            
            // Actualizar contador de notificaciones (si existe)
            await this.actualizarNotificaciones();
        } catch (error) {
            console.error('Error al actualizar contadores:', error);
        }
    }

    async actualizarMensajes() {
        try {
            const response = await fetch('/empresa/api/mensajes/contador');
            const data = await response.json();
            
            // Actualizar badge en header si existe
            const badgeMensajesHeader = document.getElementById('badge-mensajes-header');
            if (badgeMensajesHeader) {
                if (data.count > 0) {
                    badgeMensajesHeader.textContent = data.count;
                    badgeMensajesHeader.style.display = 'inline-flex';
                    badgeMensajesHeader.classList.add('pulse-animation');
                    setTimeout(() => badgeMensajesHeader.classList.remove('pulse-animation'), 1000);
                } else {
                    badgeMensajesHeader.style.display = 'none';
                }
            }
            
            // Actualizar card en dashboard
            const mensajesCount = document.getElementById('mensajes-count');
            const mensajesText = document.getElementById('mensajes-text');
            
            if (mensajesCount && mensajesText) {
                if (data.count > 0) {
                    mensajesCount.textContent = data.count;
                    mensajesCount.style.display = 'block';
                    mensajesText.textContent = 'Mensajes nuevos';
                    mensajesCount.classList.add('pulse-animation');
                    setTimeout(() => mensajesCount.classList.remove('pulse-animation'), 1000);
                } else {
                    mensajesCount.style.display = 'none';
                    mensajesText.textContent = 'Sin mensajes nuevos';
                }
            }
        } catch (error) {
            console.error('Error al actualizar mensajes:', error);
        }
    }

    async actualizarNotificaciones() {
        try {
            const response = await fetch('/empresa/api/notificaciones/contador');
            const data = await response.json();
            
            const badgeNotificaciones = document.getElementById('badge-notificaciones-header');
            if (badgeNotificaciones) {
                if (data.count > 0) {
                    badgeNotificaciones.textContent = data.count;
                    badgeNotificaciones.style.display = 'inline-flex';
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
        new NotificacionesEmpresaTiempoReal();
    });
} else {
    new NotificacionesEmpresaTiempoReal();
}
