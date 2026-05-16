# up-devops

**Trabajo Práctico - DevOps**
Universidad de Palermo

API REST que obtiene en tiempo real las cotizaciones de **dólar y principales monedas** del Banco de la Nación Argentina (BNA).

---

### Características

- Scraping de cotizaciones oficiales del BNA (Billetes y Divisas)
- Multi-stage Docker build (optimizado y ligero)
- Healthcheck integrado
- Tests unitarios completos
- CI/CD con GitHub Actions

---

### Tecnologías

- **Python 3.12** + **Django** + **Django REST Framework**
- **Gunicorn** como servidor WSGI
- **Docker** multi-stage + **Docker Compose**
- **BeautifulSoup4** + Requests (scraper)

---

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cotizaciones/` | Cotizaciones actuales del BNA |
| GET | `/api/health/` | Estado del servicio |

---

### Cómo ejecutar

```bash
docker compose up --build
```
