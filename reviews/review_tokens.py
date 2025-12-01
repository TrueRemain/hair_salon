# reviews/review_tokens.py
import hashlib
import time
import json
from datetime import datetime, timedelta
import secrets
import re

class ReviewTokenManager:
    def __init__(self):
        self.tokens_file = 'review_tokens.json'
        self.token_lifetime_hours = 168  # Ссылка действительна 7 дней
    
    def _load_tokens(self):
        try:
            with open(self.tokens_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_tokens(self, tokens):
        with open(self.tokens_file, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
    
    def generate_token(self, phone, client_name, master_code, booking_id):
        """Генерирует токен для номера телефона"""
        # Нормализуем номер телефона
        phone_normalized = self.normalize_phone(phone)
        
        # Создаем уникальный токен
        token_data = f"{phone_normalized}{secrets.token_hex(8)}{time.time()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:20]
        
        # Сохраняем токен
        tokens = self._load_tokens()
        tokens[token] = {
            'phone': phone_normalized,
            'client_name': client_name,
            'master_code': master_code,
            'booking_id': booking_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=self.token_lifetime_hours)).isoformat(),
            'used': False
        }
        
        self._save_tokens(tokens)
        return token
    
    def validate_token(self, token):
        """Проверяет валидность токена"""
        tokens = self._load_tokens()
        
        if token not in tokens:
            return False, "Токен не найден"
        
        token_data = tokens[token]
        
        # Проверяем срок действия
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() > expires_at:
            return False, "Срок действия ссылки истек"
        
        # Проверяем, не использован ли уже токен
        if token_data['used']:
            return False, "Эта ссылка уже была использована"
        
        return True, token_data
    
    def mark_token_used(self, token):
        """Помечает токен как использованный"""
        tokens = self._load_tokens()
        
        if token in tokens:
            tokens[token]['used'] = True
            tokens[token]['used_at'] = datetime.now().isoformat()
            self._save_tokens(tokens)
    
    def normalize_phone(self, phone):
        """Нормализует номер телефона к единому формату"""
        # Удаляем все нецифровые символы кроме +
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Если номер начинается с 8, заменяем на +7
        if cleaned.startswith('8'):
            cleaned = '+7' + cleaned[1:]
        # Если номер без кода страны, добавляем +7
        elif len(cleaned) == 10:
            cleaned = '+7' + cleaned
        # Если номер с 7 без +, добавляем +
        elif cleaned.startswith('7') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        
        return cleaned

# Глобальный экземпляр менеджера токенов
token_manager = ReviewTokenManager()