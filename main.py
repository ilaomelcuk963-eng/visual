from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


COMMENTS_FILE = 'comments.json'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
YOUR_EMAIL = os.getenv('YOUR_EMAIL', 'your-email@example.com')

def load_comments():
    """Загружает комментарии из файла"""
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_comments(comments):
    """Сохраняет комментарии в файл"""
    with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

@app.route('/api/comments', methods=['GET'])
def get_comments():
    """Возвращает список комментариев"""
    comments = load_comments()
    return jsonify(comments)

@app.route('/api/comments', methods=['POST'])
def add_comment():
    """Добавляет новый комментарий"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        text = data.get('text', '').strip()
        
        if not name or not text:
            return jsonify({
                'success': False, 
                'message': 'Имя и текст комментария обязательны'
            }), 400
        
        comments = load_comments()
        
        new_comment = {
            'id': len(comments) + 1,
            'name': name,
            'text': text,
            'date': datetime.now().isoformat()
        }
        
        comments.append(new_comment)
        save_comments(comments)
        
        return jsonify({
            'success': True, 
            'message': 'Комментарий успешно добавлен'
        })
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Ошибка сервера: {str(e)}'
        }), 500

@app.route('/api/contact', methods=['POST'])
def contact_form():
    """Обрабатывает форму обратной связи и отправляет email"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        

        if not name or not email or not message:
            return jsonify({
                'success': False, 
                'message': 'Все поля обязательны для заполнения'
            }), 400
        

        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False, 
                'message': 'Введите корректный email адрес'
            }), 400
        

        send_notification_email(name, email, message)
        
        return jsonify({
            'success': True, 
            'message': 'Сообщение успешно отправлено!'
        })
    
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Произошла ошибка при отправке: {str(e)}'
        }), 500

def send_notification_email(name, from_email, message):
    """Отправляет уведомление на email о новом сообщении"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("SMTP credentials not configured. Email won't be sent.")
        return
    

    msg = MimeMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = ilaomelcuk963@gmail.com
    msg['Subject'] = f'Новое сообщение с сайта от {name}'
    
    body = f"""
    Поступило новое сообщение.
    Имя: {name}
    Email: {from_email}
    
    Сообщение:
    {message}
    
    ---
    Это сообщение отправлено.
    """
    
    msg.attach(MimeText(body, 'plain'))
    

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

if __name__ == '__main__':

    if not os.path.exists(COMMENTS_FILE):
        save_comments([])
    
    app.run(debug=True, host='0.0.0.0', port=5000)