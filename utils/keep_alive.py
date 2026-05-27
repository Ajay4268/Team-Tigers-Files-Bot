"""
Tiny HTTP server so Railway / Render / Heroku see a live web process
and never spin the bot down due to inactivity.
"""
import threading
from aiohttp import web
import asyncio

async def handle(request):
    return web.Response(text="✅ AutoFilterBot is alive and running 24/7!")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

def run_keep_alive():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_web())
    loop.run_forever()

def keep_alive():
    t = threading.Thread(target=run_keep_alive, daemon=True)
    t.start()
