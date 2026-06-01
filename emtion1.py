from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = "sk-fe5a416971e94a59b8b49adaf0d6be6a"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

trips_db = []
next_id = 1

@app.route('/api/mood/analyze', methods=['POST'])
def analyze_mood():
    data = request.json
    diary_text = data.get('diary', '').strip()
    if not diary_text:
        return jsonify({"error": "Напишите дневник"}), 400

    prompt = f"""Ты профессиональный психолог. Проанализируй дневник и верни JSON:
{{
    "mental_health_index": число 0-100,
    "main_emotion": "эмоция",
    "triggers": "причины",
    "analysis": "анализ",
    "recommendation": "совет"
}}
Дневник: {diary_text}"""

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 800},
            timeout=30
        )
        result = response.json()
        ai_content = result['choices'][0]['message']['content']
        import re
        json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
        mood_data = json.loads(json_match.group())
        mood_data["mental_health_index"] = max(0, min(100, int(mood_data.get("mental_health_index", 50))))
        return jsonify(mood_data)
    except Exception as e:
        return jsonify({"mental_health_index": 50, "main_emotion": "спокойствие", "triggers": "Не удалось определить", "analysis": "Попробуйте ещё раз", "recommendation": "Отдохните и повторите"}), 200

@app.route('/api/trips', methods=['GET'])
def get_trips():
    return jsonify(trips_db)

@app.route('/api/trips', methods=['POST'])
def create_trip():
    global next_id
    data = request.json
    trip = {"id": next_id, "city": data.get('city'), "start_date": data.get('start_date'), "end_date": data.get('end_date'), "created_at": datetime.now().strftime("%d.%m.%Y")}
    trips_db.append(trip)
    next_id += 1
    return jsonify(trip), 201

@app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    global trips_db
    trips_db = [t for t in trips_db if t['id'] != trip_id]
    return jsonify({"message": "Удалено"})

@app.route('/')
def index():
    return send_file(r'C:\Users\user\Desktop\login.html')

@app.route('/app')
def app_main():
    return send_file(r'C:\Users\user\Desktop\frontend.html')

if __name__ == '__main__':
    print("Сервер запущен: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)