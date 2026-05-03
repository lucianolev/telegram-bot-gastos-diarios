from datetime import datetime
from os import environ

import flask
import google.auth
import telebot
from googleapiclient.discovery import build

app = flask.Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    return webhook_handler(flask.request)

# --- CONFIGURACIÓN ---
# Reemplazá estos valores con tus datos reales
API_TOKEN = environ.get('TELEGRAM_API_TOKEN')
SPREADSHEET_ID = environ.get('DATA_SPREADSHEET_ID')
GRUPO_GASTOS_ID = int(environ.get('GRUPO_TELEGRAM_ID'))
LIMITE_DIARIO_OBJETIVO = int(environ.get('LIMITE_DIARIO_OBJETIVO'))

# Autenticación con Google Sheets
SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
creds, project = google.auth.default(scopes=SCOPE)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

bot = telebot.TeleBot(API_TOKEN)

def webhook_handler(request):
    """
    Punto de entrada principal en Google Cloud Functions.
    """
    # 1. Verificamos si es el Cloud Scheduler (Reporte de las 22hs)
    # Se activa llamando a la URL: https://TU_URL?action=reporte
    if request.args.get('action') == 'reporte':
        enviar_reporte_diario()
        return "Reporte enviado con éxito", 200

    # 2. Procesamos mensajes entrantes de Telegram
    if request.method == 'POST':
        # Log para saber que entró un POST
        print("--- NUEVO POST RECIBIDO DESDE TELEGRAM ---")
        json_string = flask.request.get_json(force=True)
        print(f"Contenido del JSON: {json_string}")

        update = telebot.types.Update.de_json(json_string)
        if update.message:
            print(f"Mensaje detectado: {update.message.text}")
            procesar_mensaje(update.message)
        return "OK", 200
    
    return "Método no permitido", 405

def procesar_mensaje(msg):
    # Seguridad: Solo procesar mensajes que vengan del grupo de Gastos
    if msg.chat.id != GRUPO_GASTOS_ID:
        print(f"Ignorando mensaje de chat desconocido: {msg.chat.id}")
        return

    texto = msg.text.strip() if msg.text else ""

    # Comando de reinicio manual
    if texto.lower() == "empezar nuevo mes":
        archivar_ciclo()
        bot.send_message(GRUPO_GASTOS_ID, "🧹 *Ciclo reiniciado.* La planilla se ha vaciado para el nuevo mes.", parse_mode='Markdown')
        return

    # Intentar procesar como gasto si el mensaje es un número
    # Reemplazamos coma por punto por si escriben "1500,50"
    texto_limpio = texto.replace(',', '.')
    try:
        monto = float(texto_limpio)
        nombre_usuario = msg.from_user.first_name
        registrar_gasto_en_sheet(monto, nombre_usuario)
        bot.reply_to(msg, f"Registrado: *${monto:,.0f}* ✅", parse_mode='Markdown')
    except ValueError:
        # Si no es un número, el bot no hace nada (ignora la charla normal)
        pass

def registrar_gasto_en_sheet(monto, usuario):
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    valores = [[fecha_hora, usuario, monto]]
    body = {'values': valores}
    
    # Agrega el gasto en la hoja llamada 'Gastos'
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Gastos!A:C',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

def enviar_reporte_diario():
    # Leer datos de la hoja
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Gastos!A:C').execute()
    rows = result.get('values', [])
    
    if not rows or len(rows) <= 1:
        bot.send_message(GRUPO_GASTOS_ID, "⚠️ No hay gastos registrados en este ciclo todavía.")
        return

    datos = rows[1:] # Ignorar encabezados
    hoy_str = datetime.now().strftime('%Y-%m-%d')
    
    total_hoy = 0
    total_ciclo = 0
    fechas_con_gastos = set()

    for row in datos:
        try:
            fecha_full = row[0]
            fecha_solo_dia = fecha_full.split(' ')[0]
            # Limpiamos el monto de posibles caracteres extra
            monto = float(str(row[2]).replace(',', ''))
            
            total_ciclo += monto
            fechas_con_gastos.add(fecha_solo_dia)
            
            if fecha_solo_dia == hoy_str:
                total_hoy += monto
        except (IndexError, ValueError):
            continue

    # Cálculos de métricas
    dias_activos = len(fechas_con_gastos) if fechas_con_gastos else 1
    promedio_actual = total_ciclo / dias_activos
    desviacion = promedio_actual - LIMITE_DIARIO_OBJETIVO
    
    emoji_alerta = "🚩" if promedio_actual > LIMITE_DIARIO_OBJETIVO else "✅"

    mensaje = (
        f"📊 *CIERRE DEL DÍA*\n"
        f"---"
        f"💰 *Gasto hoy:* ${total_hoy:,.0f}\n"
        f"🗓️ *Total acumulado:* ${total_ciclo:,.0f}\n"
        f"📈 *Promedio diario:* ${promedio_actual:,.0f}\n"
        f"{emoji_alerta} *Desviación:* ${desviacion:+,.0f} vs objetivo\n\n"
        f"_Ciclo de {dias_activos} días con actividad._"
    )

    bot.send_message(GRUPO_GASTOS_ID, mensaje, parse_mode='Markdown')

def archivar_ciclo():
    # Limpia el rango de la planilla (ajustar si el nombre de la hoja es distinto)
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range='Gastos!A2:C5000').execute()
