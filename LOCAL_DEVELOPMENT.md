# 🛠️ Lokales Testen & Entwickeln

Diese Anleitung erklärt, wie du das **Bergfex Snow Dashboard** lokal auf deinem Rechner ausführst und testest.

---

## ⚡ Schnellstart (Empfohlen)

Führe einfach das fertige Starter-Skript aus:

```bash
./start-dev.sh
```

Dieses Skript prüft und installiert automatisch alle notwendigen Python- und Node.js-Abhängigkeiten und startet danach Frontend und Backend parallel.

---

## 🔍 Wie funktioniert das lokale Testen?

Im lokalen Entwicklungsmodus laufen **zwei Prozesse simultan**:

1. **Backend (Python FastAPI)**
   - **URL:** `http://localhost:8000`
   - **Befehl:** `npm run dev:server` (`.venv/bin/uvicorn server.server:app --reload --port 8000`)
   - Bietet die API-Endpunkte unter `/api/resorts` und `/api/resorts/{id}/history` an.

2. **Frontend (Vite / React)**
   - **URL:** `http://localhost:8080`
   - **Befehl:** `npm run dev:client` (`vite`)
   - Öffne deine Anwendung im Browser unter `http://localhost:8080`.
   - **Proxy-Setup:** Vite leitet API-Anfragen (`/api/*`) automatisch an das Backend unter `http://localhost:8000` weiter (konfiguriert in `vite.config.ts`).

---

## 🛠️ Manuelle Schritte (npm)

Alternativ kannst du auch direkt `npm` verwenden:

```bash
# 1. Einmalig Python-Abhängigkeiten installieren
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt

# 2. Node-Abhängigkeiten installieren
npm install

# 3. Beide Server gemeinsam starten
npm run dev
```

---

## 🌐 Unterschied zu Produktion (Render.com)

| Eigenschaft | Lokaler Dev-Modus | Produktion (Render.com) |
| :--- | :--- | :--- |
| **Architektur** | Frontend (Vite) + Backend (FastAPI) getrennt | Single Docker Container (Python + Static Assets) |
| **Frontend Port** | `http://localhost:8080` | Integriert in FastAPI auf Port `8080` |
| **API Proxying** | Vite proxied `/api` zu Port `8000` | FastAPI verarbeitet `/api` direkt intern |
| **Hot Reloading** | Ja (Vite HMR + Uvicorn Reload) | Nein (Static Production Build) |

---

## ❓ Häufige Fragen & Troubleshooting

### Why `ECONNREFUSED` on `/api/resorts`?
Wenn dieser Fehler im Terminal erscheint, läuft das Python-Backend auf Port `8000` nicht oder ist abgestürzt. 
- Stelle sicher, dass `.venv/bin/pip install -r server/requirements.txt` ausgeführt wurde.
- Starte die App mit `./start-dev.sh` neu.
