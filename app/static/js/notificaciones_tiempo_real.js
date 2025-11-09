/**
 * Sistema de notificaciones en tiempo real usando WebSockets (Socket.IO)
 * Actualiza badges de mensajes y notificaciones sin recargar la página
 */

class NotificacionesTiempoReal {
    constructor() {
        this.socketNotificaciones = null;
        this.socketMensajes = null;
        this.init();
    }

    init() {
        // Cargar Socket.IO desde CDN si no está disponible
        if (typeof io === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.socket.io/4.5.4/socket.io.min.js';
            script.onload = () => this.conectarWebSockets();
            document.head.appendChild(script);
        } else {
            this.conectarWebSockets();
        }
        
        // Cargar contadores iniciales
        this.actualizarContadoresIniciales();
    }

    conectarWebSockets() {
        // Conectar a notificaciones
        this.socketNotificaciones = io('/notificaciones', {
            transports: ['websocket', 'polling']
        });

        this.socketNotificaciones.on('connect', () => {
            console.log('✅ Conectado a notificaciones en tiempo real');
        });

        this.socketNotificaciones.on('nueva_notificacion', (data) => {
            console.log('Nueva notificación recibida:', data);
            this.actualizarBadgeNotificaciones();
            this.mostrarNotificacionPopup(data);
        });

        this.socketNotificaciones.on('conectado', (data) => {
            console.log('Notificaciones:', data.mensaje);
        });

        this.socketNotificaciones.on('disconnect', () => {
            console.log('Desconectado de notificaciones');
        });

        // Conectar a mensajes
        this.socketMensajes = io('/mensajes', {
            transports: ['websocket', 'polling']
        });

        this.socketMensajes.on('connect', () => {
            console.log('✅ Conectado a mensajes en tiempo real');
        });

        this.socketMensajes.on('nuevo_mensaje', (data) => {
            console.log('Nuevo mensaje recibido:', data);
            this.actualizarBadgeMensajes();
        });

        this.socketMensajes.on('conectado', (data) => {
            console.log('Mensajes:', data.mensaje);
        });

        this.socketMensajes.on('disconnect', () => {
            console.log('Desconectado de mensajes');
        });
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
