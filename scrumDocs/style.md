//* =========================================================
   AIRDJ - GUÍA DE ESTILOS
   style.css
   ========================================================= */

/* =========================
   VARIABLES GENERALES
   ========================= */

:root {
    /* Fondos */
    --color-bg-primary: #0B0F14;
    --color-bg-secondary: #141A21;
    --color-bg-card: #1C242E;
    --color-bg-hover: #25303C;

    /* Colores principales */
    --color-primary: #22C55E;
    --color-primary-hover: #4ADE80;
    --color-tech: #38BDF8;

    /* Estados */
    --color-success: #22C55E;
    --color-warning: #F59E0B;
    --color-danger: #EF4444;
    --color-disabled: #64748B;

    /* Textos */
    --color-text-primary: #F8FAFC;
    --color-text-secondary: #94A3B8;
    --color-text-muted: #64748B;

    /* Bordes */
    --color-border: #334155;

    /* Tipografía */
    --font-primary: "Inter", "Segoe UI", Arial, sans-serif;

    /* Tamaños */
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-md: 16px;
    --font-size-lg: 20px;
    --font-size-xl: 24px;
    --font-size-title: 32px;

    /* Bordes redondeados */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 20px;

    /* Sombras */
    --shadow-card: 0 8px 24px rgba(0, 0, 0, 0.25);
    --shadow-green: 0 0 20px rgba(34, 197, 94, 0.25);

    /* Transiciones */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
}


/* =========================
   RESET
   ========================= */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    min-height: 100vh;
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    font-family: var(--font-primary);
    font-size: var(--font-size-sm);
    line-height: 1.5;
}


/* =========================
   CONTENEDOR GENERAL
   ========================= */

.app {
    width: 100%;
    min-height: 100vh;
    padding: 24px;
}

.container {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
}


/* =========================
   ENCABEZADO
   ========================= */

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;

    padding: 18px 24px;
    margin-bottom: 24px;

    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
}

.logo {
    font-size: var(--font-size-title);
    font-weight: 700;
    letter-spacing: -1px;
}

.logo span {
    color: var(--color-primary);
}

.header-status {
    display: flex;
    align-items: center;
    gap: 8px;

    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    font-weight: 500;
}


/* =========================
   INDICADORES DE ESTADO
   ========================= */

.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: var(--color-disabled);
}

.status-dot.active {
    background-color: var(--color-success);
    box-shadow: 0 0 12px rgba(34, 197, 94, 0.8);
}

.status-dot.warning {
    background-color: var(--color-warning);
}

.status-dot.error {
    background-color: var(--color-danger);
}


/* =========================
   LAYOUT PRINCIPAL
   ========================= */

.main-layout {
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(300px, 1fr);
    gap: 24px;
}


/* =========================
   TARJETAS
   ========================= */

.card {
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 20px;
    box-shadow: var(--shadow-card);
}

.card-title {
    margin-bottom: 16px;

    font-size: var(--font-size-md);
    font-weight: 600;
    color: var(--color-text-primary);
}

.card-subtitle {
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
}


/* =========================
   CÁMARA
   ========================= */

.camera-container {
    position: relative;
    width: 100%;
    overflow: hidden;

    background-color: #000000;
    border: 2px solid var(--color-border);
    border-radius: var(--radius-lg);

    aspect-ratio: 16 / 9;

    transition:
        border-color var(--transition-normal),
        box-shadow var(--transition-normal);
}

.camera-container.active {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-green);
}

.camera-container video,
.camera-container canvas,
.camera-container img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}


/* =========================
   OVERLAY DE CÁMARA
   ========================= */

.camera-overlay {
    position: absolute;
    inset: 0;

    display: flex;
    flex-direction: column;
    justify-content: space-between;

    padding: 16px;

    pointer-events: none;
}

.camera-badge {
    align-self: flex-start;

    padding: 6px 10px;

    background-color: rgba(11, 15, 20, 0.75);
    backdrop-filter: blur(8px);

    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 999px;

    color: var(--color-text-primary);
    font-size: var(--font-size-xs);
    font-weight: 600;
}


/* =========================
   ESTADO AIRDJ
   ========================= */

.airdj-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    min-height: 140px;

    text-align: center;

    border-radius: var(--radius-lg);
    background-color: var(--color-bg-secondary);

    transition:
        background-color var(--transition-normal),
        border-color var(--transition-normal),
        box-shadow var(--transition-normal);
}

.airdj-state .state-icon {
    margin-bottom: 8px;
    font-size: 32px;
}

.airdj-state .state-title {
    font-size: var(--font-size-xl);
    font-weight: 700;
}

.airdj-state .state-description {
    margin-top: 4px;

    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
}


/* BLOQUEADO */

.airdj-state.locked {
    border: 1px solid var(--color-border);
}

.airdj-state.locked .state-title {
    color: var(--color-text-secondary);
}


/* ACTIVO */

.airdj-state.active {
    background-color: rgba(34, 197, 94, 0.08);
    border: 1px solid var(--color-primary);
    box-shadow: var(--shadow-green);
}

.airdj-state.active .state-title {
    color: var(--color-primary);
}


/* ESPERANDO COMANDO */

.airdj-state.listening {
    background-color: rgba(56, 189, 248, 0.08);
    border: 1px solid var(--color-tech);
}

.airdj-state.listening .state-title {
    color: var(--color-tech);
}


/* ERROR */

.airdj-state.error {
    background-color: rgba(239, 68, 68, 0.08);
    border: 1px solid var(--color-danger);
}

.airdj-state.error .state-title {
    color: var(--color-danger);
}


/* =========================
   GESTO DETECTADO
   ========================= */

.gesture-feedback {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    min-height: 120px;
    padding: 20px;

    text-align: center;

    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
}

.gesture-feedback .gesture-icon {
    margin-bottom: 8px;
    font-size: 36px;
}

.gesture-feedback .gesture-label {
    color: var(--color-text-secondary);

    font-size: var(--font-size-xs);
    font-weight: 600;

    text-transform: uppercase;
    letter-spacing: 1px;
}

.gesture-feedback .gesture-name {
    margin-top: 4px;

    color: var(--color-primary);
    font-size: var(--font-size-xl);
    font-weight: 700;
}


/* =========================
   REPRODUCTOR
   ========================= */

.player {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.now-playing-label {
    color: var(--color-text-secondary);

    font-size: var(--font-size-xs);
    font-weight: 600;

    letter-spacing: 1px;
    text-transform: uppercase;
}

.song-title {
    font-size: var(--font-size-lg);
    font-weight: 700;
}

.song-artist {
    color: var(--color-text-secondary);
    font-size: var(--font-size-md);
}


/* =========================
   BARRA DE PROGRESO
   ========================= */

.progress-container {
    width: 100%;
}

.progress-bar {
    width: 100%;
    height: 6px;

    overflow: hidden;

    background-color: var(--color-border);
    border-radius: 999px;
}

.progress {
    width: 0%;
    height: 100%;

    background-color: var(--color-primary);
    border-radius: inherit;

    transition: width 300ms linear;
}

.progress-time {
    display: flex;
    justify-content: space-between;

    margin-top: 6px;

    color: var(--color-text-muted);
    font-size: var(--font-size-xs);
}


/* =========================
   BOTONES
   ========================= */

button,
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    min-height: 46px;
    padding: 10px 18px;

    border: none;
    border-radius: var(--radius-md);

    font-family: inherit;
    font-size: var(--font-size-sm);
    font-weight: 600;

    cursor: pointer;

    transition:
        background-color var(--transition-fast),
        border-color var(--transition-fast),
        transform var(--transition-fast),
        opacity var(--transition-fast);
}

button:active,
.btn:active {
    transform: scale(0.98);
}


/* BOTÓN PRINCIPAL */

.btn-primary {
    background-color: var(--color-primary);
    color: var(--color-bg-primary);
}

.btn-primary:hover {
    background-color: var(--color-primary-hover);
}


/* BOTÓN SECUNDARIO */

.btn-secondary {
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border);
    color: var(--color-text-primary);
}

.btn-secondary:hover {
    background-color: var(--color-bg-hover);
}


/* BOTÓN PELIGRO */

.btn-danger {
    background-color: var(--color-danger);
    color: white;
}


/* BOTÓN DESACTIVADO */

button:disabled,
.btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}


/* =========================
   CONTROLES DEL REPRODUCTOR
   ========================= */

.player-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
}

.control-button {
    width: 46px;
    height: 46px;
    padding: 0;

    border-radius: 50%;

    background-color: var(--color-bg-secondary);
    border: 1px solid var(--color-border);

    color: var(--color-text-primary);
}

.control-button:hover {
    background-color: var(--color-bg-hover);
}

.control-button.main {
    width: 56px;
    height: 56px;

    background-color: var(--color-primary);

    color: var(--color-bg-primary);
    font-size: 20px;
}


/* =========================
   LISTA DE GESTOS
   ========================= */

.gesture-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.gesture-item {
    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 12px 14px;

    background-color: var(--color-bg-secondary);
    border: 1px solid transparent;
    border-radius: var(--radius-md);

    transition:
        background-color var(--transition-fast),
        border-color var(--transition-fast);
}

.gesture-item:hover {
    background-color: var(--color-bg-hover);
    border-color: var(--color-border);
}

.gesture-action {
    font-weight: 600;
}

.gesture-description {
    color: var(--color-text-secondary);
    font-size: var(--font-size-xs);
}


/* =========================
   PANEL DE INFORMACIÓN
   ========================= */

.info-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.info-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;

    padding-bottom: 8px;

    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.info-label {
    color: var(--color-text-secondary);
}

.info-value {
    color: var(--color-text-primary);
    font-weight: 600;
}


/* =========================
   MODO DESARROLLADOR
   ========================= */

.developer-panel {
    padding: 16px;

    background-color: #080B0F;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);

    font-family: "Consolas", "Courier New", monospace;
    font-size: var(--font-size-xs);
}

.developer-panel .dev-row {
    display: flex;
    justify-content: space-between;
    gap: 20px;

    padding: 4px 0;
}

.developer-panel .dev-label {
    color: var(--color-text-muted);
}

.developer-panel .dev-value {
    color: var(--color-primary);
}


/* =========================
   MENSAJES
   ========================= */

.message {
    padding: 12px 16px;

    border-radius: var(--radius-md);

    font-size: var(--font-size-sm);
}

.message.success {
    background-color: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.4);
    color: var(--color-success);
}

.message.warning {
    background-color: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: var(--color-warning);
}

.message.error {
    background-color: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: var(--color-danger);
}


/* =========================
   ANIMACIONES
   ========================= */

@keyframes pulse-green {
    0% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5);
    }

    70% {
        box-shadow: 0 0 0 12px rgba(34, 197, 94, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
    }
}

.pulse {
    animation: pulse-green 1.5s infinite;
}


@keyframes fade-in {
    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fade-in 250ms ease forwards;
}


/* =========================
   RESPONSIVE
   ========================= */

@media (max-width: 900px) {

    .app {
        padding: 16px;
    }

    .main-layout {
        grid-template-columns: 1fr;
    }

    .header {
        align-items: flex-start;
        flex-direction: column;
    }

}


@media (max-width: 600px) {

    .app {
        padding: 10px;
    }

    .header {
        padding: 14px;
    }

    .logo {
        font-size: 26px;
    }

    .card {
        padding: 14px;
    }

    .airdj-state .state-title {
        font-size: 20px;
    }

}