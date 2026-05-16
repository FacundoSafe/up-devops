from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from scraper import fetch_cotizaciones, _parse_table
from models.cotizacion import Cotizacion, CotizacionGroup, CotizacionRow

BNA_HTML_MOCK = """
<html>
<body>
  <div id="billetes">
    <table>
      <thead><tr>
        <th class="fechaCot">24/4/2026</th>
        <th>Compra</th>
        <th>Venta</th>
      </tr></thead>
      <tbody>
        <tr><td class="tit">Dolar U.S.A</td><td>1370,00</td><td>1420,00</td></tr>
        <tr><td class="tit">Euro</td><td>1585,00</td><td>1685,00</td></tr>
        <tr><td class="tit">Real *</td><td>27600,00</td><td>29100,00</td></tr>
      </tbody>
    </table>
  </div>
  <div id="divisas">
    <table>
      <thead><tr>
        <th class="fechaCot">24/4/2026</th>
        <th>Compra</th>
        <th>Venta</th>
      </tr></thead>
      <tbody>
        <tr><td class="tit">Dolar U.S.A</td><td>1390.5000</td><td>1399.5000</td></tr>
        <tr><td class="tit">Euro</td><td>1627.3022</td><td>1641.3336</td></tr>
      </tbody>
    </table>
  </div>
</body>
</html>
"""


class ScraperParseTableTest(TestCase):
    def setUp(self):
        from bs4 import BeautifulSoup
        self.soup = BeautifulSoup(BNA_HTML_MOCK, "html.parser")

    def test_parse_billetes_fecha(self):
        table = self.soup.find("div", id="billetes").find("table")
        fecha, _ = _parse_table(table)
        self.assertEqual(fecha, "24/4/2026")

    def test_parse_billetes_cantidad(self):
        table = self.soup.find("div", id="billetes").find("table")
        _, rows = _parse_table(table)
        self.assertEqual(len(rows), 3)

    def test_parse_billetes_dolar(self):
        table = self.soup.find("div", id="billetes").find("table")
        _, rows = _parse_table(table)
        dolar = rows[0]
        self.assertEqual(dolar["moneda"], "Dolar U.S.A")
        self.assertEqual(dolar["compra"], "1370,00")
        self.assertEqual(dolar["venta"], "1420,00")

    def test_parse_divisas_cantidad(self):
        table = self.soup.find("div", id="divisas").find("table")
        _, rows = _parse_table(table)
        self.assertEqual(len(rows), 2)

    def test_parse_divisas_dolar(self):
        table = self.soup.find("div", id="divisas").find("table")
        _, rows = _parse_table(table)
        dolar = rows[0]
        self.assertEqual(dolar["moneda"], "Dolar U.S.A")
        self.assertEqual(dolar["compra"], "1390.5000")
        self.assertEqual(dolar["venta"], "1399.5000")


class FetchCotizacionesTest(TestCase):
    @patch("scraper.requests.get")
    def test_fetch_returns_billetes_y_divisas(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = BNA_HTML_MOCK
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_cotizaciones()

        self.assertIn("billetes", result)
        self.assertIn("divisas", result)

    @patch("scraper.requests.get")
    def test_fetch_billetes_estructura(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = BNA_HTML_MOCK
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_cotizaciones()
        billetes = result["billetes"]

        self.assertIn("fecha", billetes)
        self.assertIn("cotizaciones", billetes)
        self.assertEqual(billetes["fecha"], "24/4/2026")
        self.assertEqual(len(billetes["cotizaciones"]), 3)

    @patch("scraper.requests.get")
    def test_fetch_divisas_estructura(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = BNA_HTML_MOCK
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_cotizaciones()
        divisas = result["divisas"]

        self.assertIn("fecha", divisas)
        self.assertIn("cotizaciones", divisas)
        self.assertEqual(len(divisas["cotizaciones"]), 2)

    @patch("scraper.requests.get")
    def test_fetch_raises_on_missing_tables(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            fetch_cotizaciones()

    @patch("scraper.requests.get")
    def test_fetch_raises_on_http_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.HTTPError("500 Server Error")

        with self.assertRaises(req.exceptions.HTTPError):
            fetch_cotizaciones()


class CotizacionesViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("routes.cotizaciones.get_cotizaciones")
    def test_get_cotizaciones_ok(self, mock_get):
        mock_get.return_value = Cotizacion(
            billetes=CotizacionGroup(
                fecha="24/4/2026",
                cotizaciones=[CotizacionRow("Dolar U.S.A", "1370,00", "1420,00")],
            ),
            divisas=CotizacionGroup(
                fecha="24/4/2026",
                cotizaciones=[CotizacionRow("Dolar U.S.A", "1390.5000", "1399.5000")],
            ),
        )
        response = self.client.get("/api/cotizaciones/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("billetes", response.data)
        self.assertIn("divisas", response.data)

    @patch("routes.cotizaciones.get_cotizaciones")
    def test_get_cotizaciones_valor_error(self, mock_get):
        mock_get.side_effect = ValueError("Tablas no encontradas")
        response = self.client.get("/api/cotizaciones/")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)

    @patch("routes.cotizaciones.get_cotizaciones")
    def test_get_cotizaciones_error_generico(self, mock_get):
        mock_get.side_effect = Exception("Timeout")
        response = self.client.get("/api/cotizaciones/")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)

    def test_post_no_permitido(self):
        response = self.client.post("/api/cotizaciones/", {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
