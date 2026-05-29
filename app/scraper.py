import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BNA_URL = "https://www.bna.com.ar/Personas"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _parse_table(table):
    rows = []
    header_row = table.find("thead")
    fecha = ""
    if header_row:
        th = header_row.find("th", class_="fechaCot")
        if th:
            fecha = th.get_text(strip=True)

    for tr in table.find("tbody").find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) == 3:
            rows.append(
                {
                    "moneda": cells[0].get_text(strip=True),
                    "compra": cells[1].get_text(strip=True),
                    "venta": cells[2].get_text(strip=True),
                }
            )
    return fecha, rows


def check_bna_status():
    try:
        response = requests.get(BNA_URL, headers=HEADERS, timeout=5, verify=False)
        return "up" if response.status_code == 200 else "down"
    except Exception:
        return "down"


def fetch_cotizaciones():
    response = requests.get(BNA_URL, headers=HEADERS, timeout=10, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    billetes_tab = soup.find("div", id="billetes")
    divisas_tab = soup.find("div", id="divisas")

    if not billetes_tab or not divisas_tab:
        raise ValueError("No se encontraron las tablas de cotización en la página del BNA")

    fecha_billetes, billetes = _parse_table(billetes_tab.find("table"))
    fecha_divisas, divisas = _parse_table(divisas_tab.find("table"))

    return {
        "billetes": {
            "fecha": fecha_billetes,
            "cotizaciones": billetes,
        },
        "divisas": {
            "fecha": fecha_divisas,
            "cotizaciones": divisas,
        },
    }
