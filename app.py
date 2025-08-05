from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
BOT_TOKEN = "8233627901:AAEwfCxwf8-FBNU6achzbW2XxUQy-Na9VKg"
DATA_FILE = "data/storage.json"

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs("data", exist_ok=True)

def read_data():
    """Read data from JSON file"""
    ensure_data_directory()
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create initial empty data structure
            initial_data = {"users": [], "verifications": []}
            write_data(initial_data)
            return initial_data
    except Exception as e:
        print(f"Error reading data: {e}")
        return {"users": [], "verifications": []}

def write_data(data):
    """Write data to JSON file"""
    ensure_data_directory()
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        print(f"Error writing data: {e}")

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook"""
    try:
        update = request.get_json()
        print(f"Received webhook: {json.dumps(update, indent=2)}")
        
        if 'message' in update:
            message = update['message']
            chat = message['chat']
            user = message['from']
            text = message.get('text', '')
            
            if text == '/start':
                # Get the domain where frontend is hosted
                frontend_domain = os.getenv('FRONTEND_DOMAIN', 'localhost:3000')
                web_app_url = f"https://{frontend_domain}/verification?bot=binarow_bot&botHash=verification_hash_{user['id']}&user_id={user['id']}"
                
                response_data = {
                    "chat_id": chat['id'],
                    "text": "🔐 Welcome to Device Verification Bot!\n\nClick the button below to verify your device:",
                    "reply_markup": {
                        "inline_keyboard": [[
                            {
                                "text": "🚀 Verify Device",
                                "web_app": {
                                    "url": web_app_url
                                }
                            }
                        ]]
                    }
                }
                
                # Send message to Telegram
                telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                telegram_response = requests.post(telegram_api_url, json=response_data)
                telegram_result = telegram_response.json()
                
                print(f"Telegram API response: {telegram_result}")
        
        return jsonify({"ok": True})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/verify', methods=['POST'])
def verify_device():
    """Handle device verification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'bot', 'bot_hash', 'device_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400
        
        storage_data = read_data()
        
        # Check if user is already verified
        existing_verification = None
        for verification in storage_data['verifications']:
            if verification['userId'] == data['user_id'] and verification['bot'] == data['bot']:
                existing_verification = verification
                break
        
        if existing_verification and existing_verification.get('isVerified', False):
            return jsonify({
                "status": "continue",
                "message": "User already verified",
                "attempt": existing_verification.get('attempts', 0)
            })
        
        # Check if device is already used by another user
        for verification in storage_data['verifications']:
            if (verification['deviceId'] == data['device_id'] and 
                verification['bot'] == data['bot'] and 
                verification['userId'] != data['user_id']):
                return jsonify({
                    "status": "error",
                    "message": "This device is already verified with another account"
                }), 400
        
        # Create or update verification
        current_time = datetime.now().isoformat()
        
        if existing_verification:
            # Update existing verification
            existing_verification.update({
                'userAgent': data.get('user_agent'),
                'platform': data.get('platform'),
                'language': data.get('language'),
                'timezone': data.get('timezone'),
                'hardwareConcurrency': data.get('hardware_concurrency'),
                'deviceMemory': data.get('device_memory'),
                'screenResolution': data.get('screen_resolution'),
                'isVerified': True,
                'attempts': existing_verification.get('attempts', 0) + 1,
                'updatedAt': current_time
            })
            result_verification = existing_verification
        else:
            # Create new verification
            new_verification = {
                'id': generate_id(),
                'userId': data['user_id'],
                'bot': data['bot'],
                'botHash': data['bot_hash'],
                'deviceId': data['device_id'],
                'userAgent': data.get('user_agent'),
                'platform': data.get('platform'),
                'language': data.get('language'),
                'timezone': data.get('timezone'),
                'hardwareConcurrency': data.get('hardware_concurrency'),
                'deviceMemory': data.get('device_memory'),
                'screenResolution': data.get('screen_resolution'),
                'isVerified': True,
                'attempts': 1,
                'createdAt': current_time,
                'updatedAt': current_time
            }
            storage_data['verifications'].append(new_verification)
            result_verification = new_verification
        
        # Save data
        write_data(storage_data)
        
        return jsonify({
            "status": "success",
            "message": "Device verified successfully",
            "verification": result_verification
        })
    
    except Exception as e:
        print(f"Verification error: {e}")
        return jsonify({
            "status": "error",
            "message": "Verification failed due to server error"
        }), 500

@app.route('/api/verifications', methods=['GET'])
def get_verifications():
    """Get all verifications (for admin purposes)"""
    try:
        storage_data = read_data()
        return jsonify({
            "verifications": storage_data.get('verifications', []),
            "total": len(storage_data.get('verifications', []))
        })
    except Exception as e:
        print(f"Error getting verifications: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get verification statistics"""
    try:
        storage_data = read_data()
        verifications = storage_data.get('verifications', [])
        
        total_verifications = len(verifications)
        verified_count = len([v for v in verifications if v.get('isVerified', False)])
        unique_users = len(set(v['userId'] for v in verifications))
        unique_devices = len(set(v['deviceId'] for v in verifications))
        
        return jsonify({
            "total_verifications": total_verifications,
            "verified_count": verified_count,
            "unique_users": unique_users,
            "unique_devices": unique_devices
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

def setup_telegram_webhook():
    """Setup Telegram webhook"""
    try:
        # Get the domain where this backend is hosted
        backend_domain = os.getenv('BACKEND_DOMAIN', 'localhost:5000')
        webhook_url = f"https://{backend_domain}/webhook"
        
        set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        response = requests.post(set_webhook_url, json={
            "url": webhook_url,
            "allowed_updates": ["message"]
        })
        
        result = response.json()
        print(f"Telegram webhook setup: {result}")
        
        # Set bot commands
        set_commands_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
        requests.post(set_commands_url, json={
            "commands": [
                {
                    "command": "start",
                    "description": "Start device verification process"
                }
            ]
        })
        
    except Exception as e:
        print(f"Failed to setup Telegram bot: {e}")

if __name__ == '__main__':
    # Setup webhook on startup
    setup_telegram_webhook()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)