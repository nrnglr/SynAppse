#!/usr/bin/env python3
"""
Word Bridge API Test Script
Django projesi içinde çalıştırılacak basit test
"""

import os
import sys
import django
import json
import requests

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobsmart.settings')
django.setup()

from exercises.word_bridge.models import WordBridgeSession

def test_word_bridge_api():
    """Word Bridge API endpoints test"""
    base_url = 'http://127.0.0.1:8000'
    
    print("🧪 Word Bridge API Test Başlıyor...")
    print("=" * 50)
    
    # Test 1: Start exercise
    print("\n1. Egzersiz Başlatma Testi")
    try:
        response = requests.post(f'{base_url}/exercises/word-bridge/start/', 
                               json={'difficulty': 'easy'},
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 201:
            data = response.json()
            session_id = data.get('session_id')
            print(f"✅ Session oluşturuldu: {session_id}")
            return session_id
        else:
            print(f"❌ API Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None

def test_database_connection():
    """Database bağlantısı test"""
    print("\n2. Database Bağlantı Testi")
    try:
        count = WordBridgeSession.objects.count()
        print(f"✅ Database bağlantısı başarılı. Toplam session: {count}")
        
        # Son oluşturulan session
        if count > 0:
            latest = WordBridgeSession.objects.latest('created_at')
            print(f"Son session: {latest.session_id} - {latest.difficulty}")
            
        return True
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False

def test_gemini_import():
    """Gemini servis import test"""
    print("\n3. Gemini Service Import Testi")
    try:
        from services.gemini_service import GeminiService
        gemini = GeminiService()
        print("✅ Gemini Service import başarılı")
        return True
    except Exception as e:
        print(f"❌ Gemini Import Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SynAppse Word Bridge Test Suite")
    print("Sunucunun çalıştığından emin olun: python manage.py runserver")
    print()
    
    # Tests
    db_ok = test_database_connection()
    gemini_ok = test_gemini_import()
    api_session = test_word_bridge_api()
    
    print("\n" + "=" * 50)
    print("📋 Test Sonuçları:")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"Gemini Service: {'✅' if gemini_ok else '❌'}")
    print(f"API Start: {'✅' if api_session else '❌'}")
    
    if all([db_ok, gemini_ok, api_session]):
        print("\n🎉 Tüm testler başarılı!")
    else:
        print("\n⚠️ Bazı testler başarısız. Loglara bakın.")
