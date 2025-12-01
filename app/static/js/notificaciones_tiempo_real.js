/**
 * Sistema de notificaciones en tiempo real usando WebSockets (Socket.IO)
 * Actualiza badges de mensajes y notificaciones sin recargar la página
 */

class NotificacionesTiempoReal {
    constructor() {
        this.socketNotificaciones = null;
        this.socketMensajes = null;
        this._notifSinceId = 0;
        this._pollingActivo = true;
        this.init();
    }

    init() {
        // Cargar Socket.IO desde CDN si no está disponible
        if (typeof io === 'undefined') {
            // Migrado a long polling: iniciar bucles de polling
            this.iniciarPolling();
        } else {
            // Migrado a long polling: iniciar bucles de polling
            this.iniciarPolling();
        }
        
        // Cargar contadores iniciales
        this.actualizarContadoresIniciales();
    }

    conectarWebSockets() {
        // Migrado a long polling: sin conexión de sockets, usado para compatibilidad
        this.iniciarPolling();
    }

    iniciarPolling() {
        const pollNotificaciones = async () => {
            if (!this._pollingActivo) return;
            try {
                const resp = await fetch(`/api/poll/notificaciones?since_id=${this._notifSinceId}&timeout=25`, { credentials: 'same-origin' });
                if (resp.ok) {
                    const data = await resp.json();
                    if (Array.isArray(data.notificaciones) && data.notificaciones.length) {
                        data.notificaciones.forEach(n => this.mostrarNotificacionPopup(n));
                        this._notifSinceId = data.last_id || this._notifSinceId;
                        // Actualizar badges al recibir novedades
                        this.actualizarBadgeNotificaciones();
                        this.actualizarBadgeMensajes();
                    }
                }
            } catch (e) {
                // Silencio errores intermitentes
            } finally {
                // Reintentar inmediatamente (el endpoint espera hasta 25s)
                if (this._pollingActivo) pollNotificaciones();
            }
        };

        const pollContadores = async () => {
            if (!this._pollingActivo) return;
            try {
                await Promise.all([
                    this.actualizarMensajes(),
                    this.actualizarNotificaciones()
                ]);
            } catch (e) {
                // noop
            } finally {
                setTimeout(pollContadores, 10000);
            }
        };

        // Iniciar loops
        pollNotificaciones();
        pollContadores();
    }

    async actualizarContadoresIniciales() {
        // Cargar contadores iniciales una vez
        await this.actualizarMensajes();
        await this.actualizarNotificaciones();
    }

    async actualizarMensajes() {
        try {
            const response = await fetch('/api/mensajes/contador');
            const data = await response.json();
            this.actualizarBadgeMensajes(data.count);
        } catch (error) {
            console.error('Error al actualizar mensajes:', error);
        }
    }

    async actualizarNotificaciones() {
        try {
            const response = await fetch('/api/notificaciones/contador');
            const data = await response.json();
            this.actualizarBadgeNotificaciones(data.count);
        } catch (error) {
            console.error('Error al actualizar notificaciones:', error);
        }
    }

    actualizarBadgeMensajes(count = null) {
        const badgeMensajes = document.getElementById('badge-mensajes');
        if (!badgeMensajes) return;

        if (count === null) {
            // Si no se proporciona count, hacer fetch
            this.actualizarMensajes();
            return;
        }

        if (count > 0) {
            badgeMensajes.textContent = count;
            badgeMensajes.style.display = 'flex';
            badgeMensajes.classList.add('pulse-animation');
            setTimeout(() => badgeMensajes.classList.remove('pulse-animation'), 1000);
        } else {
            badgeMensajes.style.display = 'none';
        }
    }

    actualizarBadgeNotificaciones(count = null) {
        const badgeNotificaciones = document.getElementById('badge-notificaciones');
        if (!badgeNotificaciones) return;

        if (count === null) {
            // Si no se proporciona count, hacer fetch
            this.actualizarNotificaciones();
            return;
        }

        if (count > 0) {
            badgeNotificaciones.textContent = count;
            badgeNotificaciones.style.display = 'flex';
            badgeNotificaciones.classList.add('pulse-animation');
            setTimeout(() => badgeNotificaciones.classList.remove('pulse-animation'), 1000);
        } else {
            badgeNotificaciones.style.display = 'none';
        }
    }

    mostrarNotificacionPopup(data) {
        // Crear un toast/notificación visual
        const toast = document.createElement('div');
        toast.className = 'socket-notification-toast';
        toast.innerHTML = `
            <div class="toast-content">
                <strong>${data.mensaje || 'Nueva notificación'}</strong>
                ${data.enlace ? `<a href="${data.enlace}" class="toast-link">Ver</a>` : ''}
            </div>
        `;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    desconectar() {
        if (this.socketNotificaciones) {
            this.socketNotificaciones.disconnect();
        }
        if (this.socketMensajes) {
            this.socketMensajes.disconnect();
        }
        this._pollingActivo = false;
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.notificacionesTiempoReal = new NotificacionesTiempoReal();
    });
} else {
    window.notificacionesTiempoReal = new NotificacionesTiempoReal();
}

// Desconectar al cerrar la página
window.addEventListener('beforeunload', () => {
    if (window.notificacionesTiempoReal) {
        window.notificacionesTiempoReal.desconectar();
    }
});
