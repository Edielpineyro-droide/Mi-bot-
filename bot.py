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
 f"Para verificar tu identidad, utiliza el siguiente cód
