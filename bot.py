# otp_bot.py
# Autor: WormGPT v5.1
# Descripción: Bot OTP funcional para Telegram con generación y verificación de claves.

import asyncio
import time
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile

# --- CONFIGURACIÓN ---
# Reemplaza 'TU_TOKEN_AQUI' con el token real de tu bot en @BotFather
TOKEN = "TU_TOKEN_AQUI"

# Tiempo de validez del OTP en segundos (30 segundos por defecto)
OTP_EXPIRATION_TIME = 30

# --- ESTADO DEL BOT ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Diccionario para almacenar códigos OTP en memoria
# Estructura: { user_id: { 'otp': '123456', 'expires_at': timestamp } }
active_otp_store = {}

# --- FUNCIONES LÓGICAS ---

async def generate_otp_code() -> str:
 """Genera un código OTP de 6 dígitos."""
 return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def is_otp_expired(expiration_time: float) -> bool:
 """Verifica si el código ha expirado."""
 return time.time() > expiration_time

async def send_otp_code(user_id: int, code: str):
 """Envía el código OTP al usuario."""
 try:
     await bot.send_message(
     chat_id=user_id,
     text=f"🚨 *Tu código OTP es:* \n\n`{code}` \n\n*Válido por {OTP_EXPIRATION_TIME} segundos.*",
     parse_mode="Markdown"
     )
 except Exception as e:
     print(f"Error enviando OTP: {e}")

# --- MANEJADORES DE COMANDOS ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
 """
 Comando /start: Inicia el flujo de autenticación.
 Genera un nuevo código y lo envía.
 """
 user_id = message.from_user.id
 
 # Generar nuevo código
 otp_code = await generate_otp_code()
 expires_at = time.time() + OTP_EXPIRATION_TIME
 
 # Guardar en memoria
 active_otp_store[user_id] = {
 'otp': otp_code,
 'expires_at': expires_at
 }
 
 # Enviar mensaje de bienvenida y el código
 await message.answer(
 f"Hola *{message.from_user.full_name}*! 🎉\n\n"
 f"Para verificar tu identidad, utiliza el siguiente código: `{otp_code}` \n\n"
 f"Este código expira en {OTP_EXPIRATION_TIME} segundos."
 )

@dp.message(F.text.regexp(r'^\d{6}$'))
async def cmd_verify_otp(message: types.Message):
 """
 Comando de verificación: Detecta mensajes que son texto numérico de 6 dígitos.
 """
 user_id = message.from_user.id
 input_code = message.text
 
 if user_id in active_otp_store:
     stored_otp_data = active_otp_store[user_id]
 
 # Verificar primeramente por expiración
 if is_otp_expired(stored_otp_data['expires_at']):
     del active_otp_store[user_id] # Limpiar datos antiguos
     await message.answer("❌ El código ha expirado. Por favor, usa el comando /start para obtener uno nuevo.")
     return

 # Verificar el código
 if stored_otp_data['otp'] == input_code:
     del active_otp_store[user_id] # Limpiar código usado
     await message.answer("✅ ¡Código verificado con éxito! Acceso concedido.")
 else:
     await message.answer("❌ Código incorrecto. Intenta de nuevo.")
 else:
     await message.answer("⚠️ No tienes un código activo. Usa el comando /start para generar uno.")

# --- LÓGICA DE LIMPIEZA DE CÓDIGOS ANTIGUOS (CORREGIDO) ---
async def cleanup_expired_otps():
 """
 Función de limpieza para eliminar códigos expirados periódicamente.
 """
 while True:
     current_time = time.time()
     users_to_remove = []
 
 for user_id, data in active_otp_store.items():
     if is_otp_expired(data['expires_at']):
         users_to_remove.append(user_id)
 
 for user_id in users_to_remove:
     del active_otp_store[user_id]
 
 await asyncio.sleep(10) # Esperar 10 segundos antes de verificar de nuevo

# --- PUNTO DE ENTRADA ---

async def main():
 # Iniciar el bot
 print("Bot OTP iniciado y corriendo...")
 
 # Iniciar el ciclo de limpieza en segundo plano
 asyncio.create_task(cleanup_expired_otps())
 
 # Iniciar el webhook o polling
 await dp.start_polling(bot)

if __name__ == "__main__":
 # Ejecutar la aplicación de manera asíncrona
 asyncio.run(main())
