from datetime import datetime
from zoneinfo import ZoneInfo

from src.dominio.reloj import Reloj


class RelojDelSistema(Reloj):
    def __init__(self, zona_horaria="America/Argentina/Buenos_Aires"):
        self._zona_horaria = ZoneInfo(zona_horaria)

    def ahora(self):
        return datetime.now(self._zona_horaria)
