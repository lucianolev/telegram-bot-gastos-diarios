import google.auth
from googleapiclient.discovery import build

from src.dominio.base_de_datos import BaseDeDatos


class GoogleSheets(BaseDeDatos):
    def __init__(self, spreadsheet_id):
        self._spreadsheet_id = spreadsheet_id
        self._sheet = self._crear_cliente()

    def agregar_fila(self, rango, valores):
        body = {"values": [valores]}
        self._sheet.values().append(
            spreadsheetId=self._spreadsheet_id,
            range=rango,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def leer_filas(self, rango):
        resultado = self._sheet.values().get(
            spreadsheetId=self._spreadsheet_id,
            range=rango,
        ).execute()
        return resultado.get("values", [])

    def limpiar_rango(self, rango):
        self._sheet.values().clear(
            spreadsheetId=self._spreadsheet_id,
            range=rango,
        ).execute()

    def _crear_cliente(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        credenciales, _ = google.auth.default(scopes=scope)
        servicio = build("sheets", "v4", credentials=credenciales)
        return servicio.spreadsheets()
