#!/usr/bin/env python3
"""
Word Bridge Kelime Üretimi Test
Yeni prompt ile alakasız kelimeler üretip üretmediğini test eder
"""

import os
import sys
import django
import requests

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobsmart.settings')
django.setup()

def test_word_generation():
    """Kelime üretimi test - alakasız kelimeler kontrolü"""
    base_url = 'http://127.0.0.1:8000'
    
    print("🧪 Word Bridge Kelime Üretimi Test")
    print("Alakasız kelimeler üretip üretmediğini kontrol ediyoruz...")
    print("=" * 60)
    
    difficulties = ['easy', 'medium', 'hard']
    
    for difficulty in difficulties:
        print(f"\n📋 {difficulty.upper()} Zorluk Seviyesi:")
        print("-" * 30)
        
        # 3 farklı test yap
        for i in range(3):
            try:
                response = requests.post(f'{base_url}/exercises/word-bridge/start/', 
                                       json={'difficulty': difficulty},
                                       timeout=30)
                
                if response.status_code == 201:
                    data = response.json()
                    target = data['target_word']
                    options = data['start_options']
                    
                    print(f"Test {i+1}:")
                    print(f"  🎯 Hedef: {target}")
                    print(f"  🔀 Seçenekler: {options}")
                    
                    # Basit benzerlik kontrolü
                    similarity_found = False
                    for option in options:
                        if target.lower() in option.lower() or option.lower() in target.lower():
                            similarity_found = True
                            print(f"  ⚠️ Benzerlik tespit edildi: {target} ↔ {option}")
                    
                    if not similarity_found:
                        print("  ✅ Kelimeler yeterince alakasız görünüyor")
                    
                else:
                    print(f"  ❌ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Test Error: {e}")
    
    print("\n" + "=" * 60)
    print("📝 Not: Gerçek alakasızlık manuel değerlendirme gerektirir")
    print("Bu test sadece açık benzerlik kontrolü yapar")

if __name__ == "__main__":
    print("🚀 SynAppse Word Bridge Kelime Test")
    print("Sunucu çalışıyor olmalı: python manage.py runserver")
    print()
    
    test_word_generation()
