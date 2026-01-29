import httpx
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- আপনার টোকেনগুলো ---
TELEGRAM_BOT_TOKEN = "8516062464:AAHBjjOfArYXf6-xsfjuCXGN9kUAA5Wi3gQ"
GROQ_API_KEY = "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"

# Groq API endpoint
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Render-এ সচল থাকার জন্য ছোট একটি সার্ভার
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

async def query_ai(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
        result = response.json()
        return result['choices'][0]['message']['content']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আসসালামু আলাইকুম! আমি Study Help AI। আমাকে তৈরি করেছেন Abdur Rahman। আমি আপনাকে কীভাবে সাহায্য করতে পারি?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = await query_ai(update.message.text)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"System Error: {str(e)}")

def main():
    # সার্ভার শুরু করা
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Study Help AI is running via Groq...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
