# Requirements Specification: Python Equation Solver (Vercel Edition)

## 1. Projekt-Infrastruktur
* **Repository:** Hosting auf **GitHub**.
* **Deployment-Plattform:** **Vercel** (Automatisches Deployment via Git-Integration).
* **Architektur:** Python Serverless Functions (FastAPI).

## 2. Technischer Stack
* **Backend:** Python 3.9+ mit **FastAPI**.
* **Mathe-Engine:** **SymPy** (für symbolisches Lösen).
* **Frontend:** HTML5 / Tailwind CSS (Dark Mode, Glassmorphism).
* **Testing:** **pytest** (Unit Tests), **Playwright** (Automatisierte UI-Tests).
* **Sprache:** Vollständige Lokalisierung in **Deutsch** (UI & Fehlermeldungen).

## 3. Dateistruktur (Vercel-Konform)
* `/api/index.py`: Hauptlogik (FastAPI) inkl. eingebettetem UI-Fallback für maximale Cloud-Kompatibilität.
* `/public/index.html`: Statische UI (Responsive Design).
* `requirements.txt`: Python-Abhängigkeiten (`fastapi`, `uvicorn`, `sympy`, `python-multipart`).
* `vercel.json`: Konfiguration für Vercel (Routing & Rewrites).
* `/tests/`: Test-Suite für API und UI.

## 4. Funktionale Anforderungen
* **Gleichungstyp:** Fokus auf **lineare Gleichungen mit einer Variablen**.
* **Parsing:** Unterstützung von Formaten wie `2x + 5 = 15`.
* **Implizite Multiplikation:** Korrektes Parsen von Eingaben wie `2x` als `2*x`.
* **Potenz-Notation:** Unterstützung des `^`-Operators (z.B. für die Validierung nicht-linearer Fälle).
* **Automatische Erkennung:** Identifikation der unbekannten Variable (x, y, z, etc.).
* **Ergebnis:** Anzeige des gelösten Wertes in symbolischer Form und als Dezimalzahl (deutsches Format).
* **Responsive UI:** Optimale Darstellung auf Smartphones, Tablets und Desktop-PCs.

## 5. Fehlerbehandlung & Validierung
* **Linearität:** Ablehnung von nicht-linearen Gleichungen (z.B. `x^2`) mit spezifischer Fehlermeldung.
* **Variablen:** Prüfung auf genau eine Variable. Fehlermeldung bei 0 oder >1 Variablen.
* **Struktur:** Validierung des Vorhandenseins von `=` und mathematischer Korrektheit.

## 6. Deployment & Performance
* **CI/CD:** Automatisches Deployment via GitHub Push.
* **Performance:** Schnelle Antwortzeiten durch optimiertes Vercel-Routing.
