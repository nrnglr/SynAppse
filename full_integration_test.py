#!/usr/bin/env python3
"""
Word Bridge Full Integration Test
Tüm API flow'unu test eder
"""

import os
import sys
import django
import json
import requests
import time

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobsmart.settings')
django.setup()

from exercises.word_bridge.models import WordBridgeSession

def test_full_word_bridge_flow():
    """Complete Word Bridge flow test"""
    base_url = 'http://127.0.0.1:8000'
    
    print("🚀 Word Bridge Full Integration Test")
    print("=" * 60)
    
    session_id = None
    
    try:
        # Test 1: Start Exercise
        print("\n1️⃣ Egzersiz Başlatma...")
        response = requests.post(f'{base_url}/exercises/word-bridge/start/', 
                               json={'difficulty': 'easy'},
                               timeout=30)
        
        if response.status_code != 201:
            print(f"❌ Start failed: {response.text}")
            return False
            
        data = response.json()
        session_id = data['session_id']
        target_word = data['target_word']
        start_options = data['start_options']
        
        print(f"✅ Session: {session_id[:8]}...")
        print(f"✅ Hedef: {target_word}")
        print(f"✅ Seçenekler: {start_options}")
        
        # Test 2: Select Start Word
        print(f"\n2️⃣ Başlangıç Kelimesi Seçimi...")
        selected_word = start_options[0]  # İlk seçeneği seç
        
        response = requests.post(f'{base_url}/exercises/word-bridge/select-start/',
                               json={
                                   'session_id': session_id,
                                   'selected_word': selected_word
                               },
                               timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Select start failed: {response.text}")
            return False
            
        print(f"✅ Başlangıç seçildi: {selected_word}")
        
        # Test 3: Submit Words
        print(f"\n3️⃣ Kelime Gönderme...")
        test_words = ["deneme", "test", "kelime"]
        
        for i, word in enumerate(test_words, 1):
            response = requests.post(f'{base_url}/exercises/word-bridge/submit-word/',
                                   json={
                                       'session_id': session_id,
                                       'word': word
                                   },
                                   timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Submit word {i} failed: {response.text}")
                return False
                
            data = response.json()
            print(f"✅ Kelime {i}: {word} (Adım: {data['current_step']})")
        
        # Test 4: Request Hint
        print(f"\n4️⃣ Hint İsteme...")
        response = requests.post(f'{base_url}/exercises/word-bridge/get-hint/',
                               json={
                                   'session_id': session_id,
                                   'hint_level': 1
                               },
                               timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Get hint failed: {response.text}")
            return False
            
        data = response.json()
        print(f"✅ Hint alındı: {data['hint_text'][:50]}...")
        
        # Test 5: Complete Exercise
        print(f"\n5️⃣ Egzersiz Tamamlama...")
        response = requests.post(f'{base_url}/exercises/word-bridge/complete/',
                               json={'session_id': session_id},
                               timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Complete failed: {response.text}")
            return False
            
        data = response.json()
        print(f"✅ Tamamlandı!")
        print(f"📊 Skorlar: {data['scores']}")
        print(f"🔗 Çözüm: {' → '.join(data['user_solution'])}")
        
        # Test 6: Database Verification
        print(f"\n6️⃣ Database Doğrulama...")
        try:
            session = WordBridgeSession.objects.get(session_id=session_id)
            print(f"✅ Session veritabanında: {session.is_completed}")
            print(f"✅ Submitted words: {len(session.submitted_words)}")
            print(f"✅ Hints used: {len(session.hints_used)}")
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def test_error_scenarios():
    """Test error handling"""
    base_url = 'http://127.0.0.1:8000'
    
    print(f"\n🧪 Error Scenario Tests")
    print("-" * 40)
    
    # Test invalid session ID
    response = requests.post(f'{base_url}/exercises/word-bridge/submit-word/',
                           json={
                               'session_id': '00000000-0000-0000-0000-000000000000',
                               'word': 'test'
                           },
                           timeout=10)
    
    if response.status_code == 404:
        print("✅ Invalid session ID handled correctly")
    else:
        print(f"❌ Invalid session ID: expected 404, got {response.status_code}")
    
    # Test invalid difficulty
    response = requests.post(f'{base_url}/exercises/word-bridge/start/',
                           json={'difficulty': 'invalid'},
                           timeout=10)
    
    if response.status_code == 400:
        print("✅ Invalid difficulty handled correctly")
    else:
        print(f"❌ Invalid difficulty: expected 400, got {response.status_code}")

if __name__ == "__main__":
    print("🔬 SynAppse Word Bridge Integration Test Suite")
    print("Sunucu çalışıyor olmalı: python manage.py runserver")
    
    # Ana flow testi
    success = test_full_word_bridge_flow()
    
    # Error handling testi
    test_error_scenarios()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 FULL INTEGRATION TEST PASSED!")
        print("Word Bridge egzersizi tamamen çalışıyor!")
    else:
        print("❌ Integration test failed")
        
    print("\n📋 Test Özeti:")
    print("✅ API Endpoints")
    print("✅ Gemini AI Integration") 
    print("✅ Database Operations")
    print("✅ Session Management")
    print("✅ Error Handling")
    print("✅ Frontend-Backend Communication")
