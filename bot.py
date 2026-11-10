# otp_bot.py
import asyncio
import time
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
import os

TOKEN = os.getenv("BOT_TOKEN")
OTP_EXPIRATION_TIME = 30

bot = Bot(token=TOKEN)
dp = Dispatcher()

active_otp_store = {}

async def generate_otp_code() -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def is_otp_expired(expiration_time: float) -> bool:
    return time.time() > expiration_time

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    otp_code = await generate_otp_code()
    expires_at = time.time() + OTP_EXPIRATION_TIME
    
    active_otp_store[user_id] = {
        'otp': otp_code,
        'expires_at': expires_at
    }
    
    await message.answer(
        f"Hola *{message.from_user.full_name}*! 🎉\n\n"
        f"Para verificar tu identidad, utiliza el siguiente código: `{otp_code}` \n\n"
        f"Este código expira en {OTP_EXPIRATION_TIME} segundos."
    )

@dp.message(F.text.regexp(r'^\d{6}$'))
async def cmd_verify_otp(message: types.Message):
    user_id = message.from_user.id
    input_code = message.text
    
    if user_id in active_otp_store:
        stored_otp_data = active_otp_store[user_id]
        
        if is_otp_expired(stored_otp_data['expires_at']):
            del active_otp_store[user_id]
            await message.answer("❌ El código ha expirado. Usa /start para obtener uno nuevo.")
            return

        if stored_otp_data['otp'] == input_code:
            del active_otp_store[user_id]
            await message.answer("✅ ¡Código verificado con éxito! Acceso concedido.")
        else:
            await message.answer("❌ Código incorrecto. Intenta de nuevo.")
    else:
        await message.answer("⚠️ No tienes un código activo. Usa /start para generar uno.")

async def cleanup_expired_otps():
    while True:
        users_to_remove = []
        for user_id, data in active_otp_store.items():
            if is_otp_expired(data['expires_at']):
                users_to_remove.append(user_id)
        for user_id in users_to_remove:
            del active_otp_store[user_id]
        await asyncio.sleep(10)

async def main():
    print("Bot OTP iniciado y corriendo...")
    asyncio.create_task(cleanup_expired_otps())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
