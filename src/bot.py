import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import psycopg

print("Ejecutando script de conexión...")

load_dotenv()
PASSWORD = os.getenv("PASSWORD")
TOKEN = os.getenv("TOKEN")

# Función para obtener conexión a la base de datos
def get_connection():
    try:
        connection = psycopg.connect(
            host='localhost',
            user='postgres',
            password=PASSWORD,
            dbname='KentBot',
            port=5432
        )
        return connection
    except Exception as e:
        print("Error en la conexión:", e)
        return None

# Función para buscar DNI en la base de datos
def get_dni_info(dni):
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT dni, ap_pat, ap_mat, nombres, fecha_nac, fch_inscripcion, 
                           fch_emision, fch_caducidad, ubigeo_nac, ubigeo_dir, 
                           direccion, sexo, est_civil, dig_ruc, madre, padre
                    FROM usuarios WHERE dni = %s
                ''', (dni,))
                result = cursor.fetchone()
                if result:
                    return {
                        "dni": result[0],
                        "ap_pat": result[1],
                        "ap_mat": result[2],
                        "nombres": result[3],
                        "fecha_nac": result[4],
                        "fch_inscripcion": result[5],
                        "fch_emision": result[6],
                        "fch_caducidad": result[7],
                        "ubigeo_nac": result[8],
                        "ubigeo_dir": result[9],
                        "direccion": result[10],
                        "sexo": "Masculino" if result[11] == 'M' else "Femenino",
                        "est_civil": result[12],
                        "dig_ruc": result[13],
                        "madre": result[14],
                        "padre": result[15]
                    }
                return None
        except Exception as e:
            print(f"⚠ Error al consultar DNI {dni}:", e)
            return None
        finally:
            connection.close()

# Función RESPUESTA AL USER
def dni_lookup(update: Update, context: CallbackContext) -> None:
    dni = update.message.text.strip()
    user_data = get_dni_info(dni)
    
    if user_data:
        info = f"""
        🟢 Información del Usuario 🟢
        📌 DNI: {user_data['dni']}
        👤 Nombre: {user_data['ap_pat']} {user_data['ap_mat']} {user_data['nombres']}
        🎂 Fecha de Nacimiento: {user_data['fecha_nac']}
        📝 Fecha de Inscripción: {user_data['fch_inscripcion']}
        📆 Fecha de Emisión: {user_data['fch_emision']}
        ⏳ Fecha de Caducidad: {user_data['fch_caducidad']}
        🌍 Ubigeo Nacimiento: {user_data['ubigeo_nac']}
        🏠 Ubigeo Dirección: {user_data['ubigeo_dir']}
        📍 Dirección: {user_data['direccion']}
        🚻 Sexo: {user_data['sexo']}
        💍 Estado Civil: {user_data['est_civil']}
        🔢 Dígito RUC: {user_data['dig_ruc']}
        👩 Madre: {user_data['madre']}
        👨 Padre: {user_data['padre']}
        """
        update.message.reply_text(info)
    else:
        update.message.reply_text("⚠ No se encontró información.")

# Función INICIO DEL BOT
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Ingresa un DNI y te daré la información.")

def main():
    print("⏳ Verificando conexión a la base de datos...")
    connection = get_connection()
    if connection:
        print("✅ Conexión a la base de datos exitosa")
        with connection.cursor() as cursor:
            cursor.execute('SELECT version()')
            row = cursor.fetchone()
            print(f"📌 Versión de PostgreSQL: {row}")
        connection.close()
        print("🔗 Conexión de prueba cerrada")
    else:
        print("❌ No se pudo establecer conexión a la base de datos. Revise las credenciales.")
        return

    print("🔄 Iniciando el bot...")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    print("📢 Registrando manejadores de comandos...")
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, dni_lookup))

    print("🚀 Bot en ejecución. Esperando mensajes...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
