/**
 * Sistema de notificaciones en tiempo real usando WebSockets (Socket.IO)
 * Actualiza badges de mensajes y notificaciones sin recargar la página
 */

class NotificacionesTiempoReal {
    constructor() {
        this.pusher = null;
        this.channel = null;
        this.init();
    }

    init() {
        // Cargar contadores iniciales
        this.actualizarContadoresIniciales();
        // Conectar a Pusher
        this.iniciarPusher();
    }

    async loadPusherIfNeeded() {
        if (typeof Pusher !== 'undefined') return true;
        try {
            await new Promise((resolve, reject) => {
                const s = document.createElement('script');
                s.src = 'https://js.pusher.com/8.0/pusher.min.js';
                s.async = true;
                s.onload = resolve;
                s.onerror = reject;
                document.head.appendChild(s);
            });
            return typeof Pusher !== 'undefined';
        } catch (e) {
            console.warn('No se pudo cargar Pusher JS:', e);
            return false;
        }
    }

    async iniciarPusher() {
        try {
            const [cfgResp, meResp] = await Promise.all([
                fetch('/pusher/config', { credentials: 'same-origin' }),
                fetch('/pusher/me', { credentials: 'same-origin' })
            ]);
            if (!cfgResp.ok || !meResp.ok) return;
            const cfg = await cfgResp.json();
            const me = await meResp.json();
            if (!cfg.key || !cfg.cluster || !me.id) return;

            if (!(await this.loadPusherIfNeeded())) return;

            this.pusher = new Pusher(cfg.key, {
                cluster: cfg.cluster,
                forceTLS: true,
                channelAuthorization: {
                    endpoint: '/pusher/auth',
                    transport: 'ajax',
                    headers: {}
                }
            });
            this.channel = this.pusher.subscribe(`private-chat-${me.id}`);
            this.channel.bind('pusher:subscription_succeeded', () => {
                try { console.debug('[Pusher usuario] Suscripción OK', `private-chat-${me.id}`); } catch(e){}
            });
            this.channel.bind('pusher:subscription_error', (status) => {
                try { console.error('[Pusher usuario] Error de suscripción', status); } catch(e){}
            });

            this.channel.bind('new-message', (data) => {
                try {
                    // Actualizar badges cuando llega un mensaje nuevo
                    this.actualizarMensajes();
                    this.actualizarNotificaciones();
                    // Emitir evento global para que vistas de chat lo consuman
                    window.dispatchEvent(new CustomEvent('pusher:new-message', { detail: data }));
                    try { console.debug('[Pusher usuario] new-message', data); } catch(e){}
                } catch (e) { /* noop */ }
            });
        } catch (e) {
            console.error('Error iniciando Pusher:', e);
        }
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
        try {
            if (this.channel) this.pusher.unsubscribe(this.channel.name);
            if (this.pusher) this.pusher.disconnect();
        } catch (e) { /* noop */ }
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
