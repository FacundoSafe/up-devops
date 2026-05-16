from dataclasses import dataclass, field
from typing import List


@dataclass
class CotizacionRow:
    moneda: str
    compra: str
    venta: str


@dataclass
class CotizacionGroup:
    fecha: str
    cotizaciones: List[CotizacionRow] = field(default_factory=list)


@dataclass
class Cotizacion:
    billetes: CotizacionGroup
    divisas: CotizacionGroup
