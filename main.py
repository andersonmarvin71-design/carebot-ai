"""
╔════════════════════════════════════════════════════════════════╗
║         CareBot AI - Telegram Health Assistant                 ║
║                                                                ║
║  Created by: Monu                                              ║
║  Date: 2026-04-26                                              ║
║  Description: A Telegram chatbot powered by Google Gemini AI   ║
║               for health-related queries                       ║
╚════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request
import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# 🔑 Configuration from environment variables
TOKEN = os.getenv("8618597269:AAGuVOwLmesBYZ2OazaQId0SNm_gwowGs6I")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ⚙️ Validation
if not TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN and GEMINI_API_KEY must be set in .env file")

# 📊 Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 📩 Send Telegram Message
def send_message(chat_id, text):
    """
    Send a message to a Telegram chat
    
    Args:
        chat_id (int): The chat ID to send message to
        text (str): The message text to send
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not text or not chat_id:
        logger.warning(f"Invalid chat_id ({chat_id}) or text ({text})")
        return False
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"✅ Message sent to chat {chat_id}")
        return True
    
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout sending message to {chat_id}")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"🌐 Connection error sending message to {chat_id}")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP error sending message: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error sending message: {e}")
        return False

# 🤖 Get AI Reply from Gemini
def get_ai_reply(user_text):
    """
    Get a health-related response from Google Gemini AI
    
    Args:
        user_text (str): The user's question/message
    
    Returns:
        str: AI-generated response or error message
    """
    if not user_text or not user_text.strip():
        return "📝 Please send a message for health assistance."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"You are a helpful health assistant. Provide accurate, safe health information. User query: {user_text}"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Extract AI response
        if "candidates" in result and len(result["candidates"]) > 0:
            ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
            logger.info(f"✅ AI response generated successfully")
            return ai_response
        else:
            logger.warning("⚠️ Unexpected API response structure")
            return "⚠️ Could not generate response. Please try again."
    
    except requests.exceptions.Timeout:
        logger.error("⏱️ Gemini API timeout")
        return "⏱️ Request timeout. Please try again in a moment."
    except requests.exceptions.ConnectionError:
        logger.error("🌐 Gemini API connection error")
        return "🌐 Network error. Please check your connection."
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Gemini API HTTP error: {e}")
        return "❌ API error. Please try again later."
    except KeyError as e:
        logger.error(f"❌ Missing key in API response: {e}")
        return "⚠️ API response error. Please try again."
    except IndexError:
        logger.error("❌ Empty candidates in API response")
        return "⚠️ AI service error. Please try again."
    except Exception as e:
        logger.error(f"❌ Unexpected error in get_ai_reply: {e}")
        return "❌ An unexpected error occurred. Please try again."

# 🔗 Telegram Webhook Handler
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    """
    Handle incoming Telegram messages via webhook
    """
    try:
        data = request.get_json()
        
        # Validate webhook data
        if not data:
            logger.warning("❌ Empty webhook data received")
            return "ok", 200
        
        if "message" not in data:
            logger.info("ℹ️ Webhook update without message")
            return "ok", 200
        
        message_data = data["message"]
        chat_id = message_data.get("chat", {}).get("id")
        message_text = message_data.get("text", "").strip()
        user_name = message_data.get("chat", {}).get("first_name", "User")
        
        # Validate message
        if not chat_id:
            logger.warning("❌ No chat_id found in message")
            return "ok", 200
        
        if not message_text:
            logger.info(f"ℹ️ Empty message from {user_name}")
            return "ok", 200
        
        logger.info(f"📨 New message from {user_name}: {message_text}")
        
        # Handle /start command
        if message_text == "/start":
            reply = (
                "👋 Welcome to CareBot AI (FREE VERSION)\n\n"
                "🤖 Powered by Google Gemini AI\n"
                "👨‍💻 Created by: Monu\n\n"
                "💬 Ask me anything about health, wellness, and fitness!\n"
                "Type /help for more commands."
            )
        
        # Handle /help command
        elif message_text == "/help":
            reply = (
                "📚 Available Commands:\n\n"
                "/start - Welcome message\n"
                "/about - About CareBot AI\n"
                "/help - Show this help message\n\n"
                "Just type your health question anytime! 🏥"
            )
        
        # Handle /about command
        elif message_text == "/about":
            reply = (
                "ℹ️ About CareBot AI\n\n"
                "👨‍💻 Creator: Monu\n"
                "🤖 Powered by: Google Gemini AI\n"
                "🛠️ Built with: Flask + Telegram API\n"
                "📅 Version: 1.0\n"
                "📝 Purpose: Health assistance chatbot\n\n"
                "⚠️ Disclaimer: This bot provides general health information. "
                "Always consult a healthcare professional for medical advice."
            )
        
        # Default: Get AI response
        else:
            reply = get_ai_reply(message_text)
        
        # Send reply
        success = send_message(chat_id, reply)
        
        if not success:
            logger.error(f"❌ Failed to send message to {chat_id}")
        
        return "ok", 200
    
    except ValueError as e:
        logger.error(f"❌ Value error in webhook: {e}")
        return "ok", 200
    except Exception as e:
        logger.error(f"❌ Unexpected error in webhook: {e}")
        return "ok", 200

# 🧪 Health Check Route
@app.route("/", methods=["GET"])
def health_check():
    """
    Health check endpoint - verifies bot is running
    """
    status = {
        "status": "✅ CareBot AI is running",
        "version": "1.0",
        "creator": "Monu",
        "timestamp": datetime.now().isoformat()
    }
    logger.info("✅ Health check passed")
    return status, 200

# 🧪 Status Route
@app.route("/status", methods=["GET"])
def status():
    """
    Show bot status and configuration info
    """
    return {
        "bot_name": "CareBot AI",
        "status": "🚀 Running",
        "created_by": "Monu",
        "ai_provider": "Google Gemini",
        "platform": "Telegram",
        "version": "1.0"
    }, 200

# 🚀 Error Handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 Error: {error}")
    return {"error": "❌ Not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 Error: {error}")
    return {"error": "❌ Internal server error"}, 500

# 🎯 Main Entry Point
if __name__ == "__main__":
    logger.info("🚀 Starting CareBot AI...")
    logger.info(f"📱 Webhook endpoint: /{TOKEN}")
    logger.info("👨‍💻 Creator: Monu")
    
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        threaded=True
    )
