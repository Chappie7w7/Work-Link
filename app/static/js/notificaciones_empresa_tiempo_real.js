/**
 * Sistema de notificaciones en tiempo real para empresas usando WebSockets (Socket.IO)
 * Actualiza contadores de mensajes y notificaciones sin recargar la página
 */

class NotificacionesEmpresaTiempoReal {
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

    async actualizarContadoresIniciales() {
        // Cargar contadores iniciales una vez
        await this.actualizarMensajes();
        await this.actualizarNotificaciones();
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
            this.actualizarBadgeNotificaciones(data.count);
        } catch (error) {
            console.error('Error al actualizar notificaciones:', error);
        }
    }

    actualizarBadgeMensajes(count = null) {
        if (count === null) {
            this.actualizarMensajes();
            return;
        }

        const badgeMensajesHeader = document.getElementById('badge-mensajes-header');
        if (badgeMensajesHeader) {
            if (count > 0) {
                badgeMensajesHeader.textContent = count;
                badgeMensajesHeader.style.display = 'inline-flex';
                badgeMensajesHeader.classList.add('pulse-animation');
                setTimeout(() => badgeMensajesHeader.classList.remove('pulse-animation'), 1000);
            } else {
                badgeMensajesHeader.style.display = 'none';
            }
        }

        const mensajesCount = document.getElementById('mensajes-count');
        const mensajesText = document.getElementById('mensajes-text');
        if (mensajesCount && mensajesText) {
            if (count > 0) {
                mensajesCount.textContent = count;
                mensajesCount.style.display = 'block';
                mensajesText.textContent = 'Mensajes nuevos';
                mensajesCount.classList.add('pulse-animation');
                setTimeout(() => mensajesCount.classList.remove('pulse-animation'), 1000);
            } else {
                mensajesCount.style.display = 'none';
                mensajesText.textContent = 'Sin mensajes nuevos';
            }
        }
    }

    actualizarBadgeNotificaciones(count = null) {
        if (count === null) {
            this.actualizarNotificaciones();
            return;
        }

        const badgeNotificaciones = document.getElementById('badge-notificaciones-header');
        if (badgeNotificaciones) {
            if (count > 0) {
                badgeNotificaciones.textContent = count;
                badgeNotificaciones.style.display = 'inline-flex';
                badgeNotificaciones.classList.add('pulse-animation');
                setTimeout(() => badgeNotificaciones.classList.remove('pulse-animation'), 1000);
            } else {
                badgeNotificaciones.style.display = 'none';
            }
        }
    }

    mostrarNotificacionPopup(data) {
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
                        this.actualizarBadgeNotificaciones();
                        this.actualizarBadgeMensajes();
                    }
                }
            } catch (e) {
                // noop
            } finally {
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

        pollNotificaciones();
        pollContadores();
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.notificacionesEmpresaTiempoReal = new NotificacionesEmpresaTiempoReal();
    });
} else {
    window.notificacionesEmpresaTiempoReal = new NotificacionesEmpresaTiempoReal();
}

// Desconectar al cerrar la página
window.addEventListener('beforeunload', () => {
    if (window.notificacionesEmpresaTiempoReal) {
        window.notificacionesEmpresaTiempoReal.desconectar();
    }
});
