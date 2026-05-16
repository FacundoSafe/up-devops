from scraper import fetch_cotizaciones
from models.cotizacion import Cotizacion, CotizacionGroup, CotizacionRow


def get_cotizaciones() -> Cotizacion:
    data = fetch_cotizaciones()
    billetes = CotizacionGroup(
        fecha=data["billetes"]["fecha"],
        cotizaciones=[CotizacionRow(**row) for row in data["billetes"]["cotizaciones"]],
    )
    divisas = CotizacionGroup(
        fecha=data["divisas"]["fecha"],
        cotizaciones=[CotizacionRow(**row) for row in data["divisas"]["cotizaciones"]],
    )
    return Cotizacion(billetes=billetes, divisas=divisas)
