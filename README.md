# Telegram Device Verification Bot - Flask Backend

यह एक Python Flask backend है जो Telegram bot के device verification के लिए बनाया गया है। यह JSON file storage का उपयोग करता है।

## Features

- ✅ Telegram Bot Webhook Integration
- ✅ Device Fingerprinting Support
- ✅ JSON File Storage (No Database Required)
- ✅ CORS Support for Frontend
- ✅ RESTful API Endpoints
- ✅ Statistics & Analytics
- ✅ Health Check Endpoint

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Environment Variables

Backend को deploy करते समय ये environment variables set करें:

```bash
BACKEND_DOMAIN=your-backend-domain.com
FRONTEND_DOMAIN=your-frontend-domain.com
PORT=5000
```

## API Endpoints

### Core Endpoints
- `POST /webhook` - Telegram bot webhook
- `POST /api/verify` - Device verification
- `GET /health` - Health check

### Analytics Endpoints
- `GET /api/verifications` - Get all verifications
- `GET /api/stats` - Get verification statistics

## Deployment Steps for Pella.app

1. **Upload Files**
   ```
   flask-backend/
   ├── app.py
   ├── requirements.txt
   ├── data/
   └── .gitignore
   ```

2. **Set Environment Variables**
   - `BACKEND_DOMAIN`: Your Pella.app domain
   - `FRONTEND_DOMAIN`: Where your frontend is hosted
   - `PORT`: Usually 5000 or 8000

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   python app.py
   ```

## Frontend Integration

Frontend में `BACKEND_URL` को update करें:

```javascript
const BACKEND_URL = 'https://your-pella-domain.com';
```

## File Structure

```
flask-backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── data/              # JSON storage directory
│   ├── .gitkeep       # Keep directory in git
│   └── storage.json   # Data storage (auto-generated)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## JSON Storage Format

```json
{
  "users": [],
  "verifications": [
    {
      "id": "unique-id",
      "userId": "telegram-user-id",
      "bot": "bot-name",
      "botHash": "verification-hash",
      "deviceId": "fingerprint-id",
      "userAgent": "browser-info",
      "platform": "device-platform",
      "language": "user-language",
      "timezone": "user-timezone",
      "hardwareConcurrency": 4,
      "deviceMemory": "8",
      "screenResolution": "1920x1080",
      "isVerified": true,
      "attempts": 1,
      "createdAt": "2024-01-01T12:00:00.000Z",
      "updatedAt": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

## Support

यदि कोई issue आए तो:
1. Logs check करें
2. Environment variables verify करें  
3. JSON file permissions check करें
4. Telegram webhook status verify करें

## Bot Information

- Bot Token: `8233627901:AAEwfCxwf8-FBNU6achzbW2XxUQy-Na9VKg`
- Bot Username: `@binarow_bot`