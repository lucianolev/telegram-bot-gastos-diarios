from os import environ

from src.aplicacion.aplicacion_gastos import AplicacionGastos
from src.aplicacion.formateador_reporte_diario import FormateadorReporteDiario
from src.dominio.repositorio_de_gastos import RepositorioDeGastos
from src.infraestructura.flask_server import FlaskServer
from src.infraestructura.google_sheets import GoogleSheets
from src.infraestructura.reloj_del_sistema import RelojDelSistema
from src.infraestructura.telegram_bot import TelegramBot


def crear_servidor():
    api_token = environ["TELEGRAM_API_TOKEN"]
    spreadsheet_id = environ["DATA_SPREADSHEET_ID"]
    grupo_gastos_id = int(environ["GRUPO_TELEGRAM_ID"])
    limite_diario_objetivo = int(environ["LIMITE_DIARIO_OBJETIVO"])

    base_de_datos = GoogleSheets(spreadsheet_id)
    repositorio = RepositorioDeGastos(base_de_datos)
    asistente = TelegramBot(api_token)
    reloj = RelojDelSistema()
    formateador = FormateadorReporteDiario()

    aplicacion = AplicacionGastos(
        grupo_gastos_id,
        limite_diario_objetivo,
        repositorio,
        asistente,
        reloj,
        formateador,
    )
    return FlaskServer(aplicacion, asistente)


servidor = crear_servidor()
app = servidor.app
