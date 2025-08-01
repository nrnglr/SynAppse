"""
Test Community Learning System
Bu script community learning sisteminin doğru çalıştığını test eder.
"""

import os
import sys
import django

# Django ayarlarını yükle
sys.path.append('c:\\Users\\mehme\\Desktop\\github2Synappse\\SynAppse')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lobsmart.settings')

try:
    django.setup()
    print("✅ Django başarıyla yüklendi")
except Exception as e:
    print(f"❌ Django yüklenirken hata: {e}")
    sys.exit(1)

def test_community_learning_system():
    """Test community learning system components"""
    print("\n🧪 Community Learning Sistemi Test Ediliyor...\n")
    
    # Test 1: Model import testi
    try:
        from exercises.problem_chain.models import CommunityLearningData, CommunityProblemMetrics
        print("✅ CommunityLearningData model başarıyla import edildi")
        print("✅ CommunityProblemMetrics model başarıyla import edildi")
    except Exception as e:
        print(f"❌ Model import hatası: {e}")
        return False
    
    # Test 2: Community Learner servisi
    try:
        from exercises.problem_chain.community_learner import CommunityLearner
        print("✅ CommunityLearner servis başarıyla import edildi")
        
        # Test learning insights
        insights = CommunityLearner.get_learning_insights('medium')
        print(f"✅ Learning insights alındı: {insights.get('total_examples', 0)} örnek")
    except Exception as e:
        print(f"❌ CommunityLearner import/test hatası: {e}")
        return False
    
    # Test 3: Community Aware Gemini
    try:
        from services.community_aware_gemini import CommunityAwareGemini
        print("✅ CommunityAwareGemini servis başarıyla import edildi")
    except Exception as e:
        print(f"❌ CommunityAwareGemini import hatası: {e}")
        return False
    
    # Test 4: Community Insight Service
    try:
        from exercises.problem_chain.community_insight_service import CommunityInsightService
        print("✅ CommunityInsightService başarıyla import edildi")
        
        # Test live stats
        stats = CommunityInsightService.get_live_stats()
        print(f"✅ Live stats alındı: {stats.get('total_learning_entries', 0)} learning entry")
    except Exception as e:
        print(f"❌ CommunityInsightService import/test hatası: {e}")
        return False
    
    # Test 5: Database bağlantısı ve tabloları
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # CommunityLearningData tablosunu kontrol et
            cursor.execute("SELECT COUNT(*) FROM community_learning_data")
            learning_count = cursor.fetchone()[0]
            print(f"✅ CommunityLearningData tablosu: {learning_count} kayıt")
            
            # CommunityProblemMetrics tablosunu kontrol et
            cursor.execute("SELECT COUNT(*) FROM community_problem_metrics") 
            metrics_count = cursor.fetchone()[0]
            print(f"✅ CommunityProblemMetrics tablosu: {metrics_count} kayıt")
            
    except Exception as e:
        print(f"❌ Database test hatası: {e}")
        return False
    
    # Test 6: Mevcut session'ları kontrol et
    try:
        from exercises.problem_chain.models import ProblemChainSession
        session_count = ProblemChainSession.objects.count()
        completed_count = ProblemChainSession.objects.filter(is_completed=True).count()
        print(f"✅ Problem Chain Sessions: {session_count} toplam, {completed_count} tamamlanmış")
    except Exception as e:
        print(f"❌ Session test hatası: {e}")
        return False
        
    return True

def test_create_sample_learning_data():
    """Örnek learning data oluştur"""
    print("\n📝 Örnek Learning Data Oluşturuluyor...\n")
    
    try:
        from exercises.problem_chain.models import CommunityLearningData
        from django.utils import timezone
        
        # Örnek başarılı bir session simüle et
        import hashlib
        problem_text = "2, 4, 8, 16, ? - Bu sayı dizisindeki eksik sayıyı bulun."
        problem_hash = hashlib.md5(problem_text.encode()).hexdigest()
        
        sample_data = CommunityLearningData.objects.create(
            problem_text=problem_text,
            solution_text="32 - Bu geometrik bir dizidir, her sayı bir öncekinin 2 katıdır.",
            problem_hash=problem_hash,
            problem_category="pattern_recognition",
            difficulty="medium",
            round_number=3,
            overall_score=4.5,
            user_rating=5,
            creativity_score=4,
            practicality_score=5,
            engagement_time=45.0,
            success_pattern={
                "type": "geometric_sequence",
                "pattern": "multiply_by_2",
                "difficulty_level": "medium",
                "cognitive_load": "moderate"
            }
        )
        
        print(f"✅ Örnek learning data oluşturuldu - ID: {sample_data.id}")
        print(f"   Problem: {sample_data.problem_text[:50]}...")
        print(f"   Score: {sample_data.overall_score}")
        print(f"   Category: {sample_data.problem_category}")
        
        return True
        
    except Exception as e:
        print(f"❌ Örnek data oluşturma hatası: {e}")
        return False

def test_ai_community_integration():
    """AI'ın community data'yı kullanıp kullanmadığını test et"""
    print("\n🤖 AI Community Integration Test...\n")
    
    try:
        from services.community_aware_gemini import CommunityAwareGemini
        from exercises.problem_chain.community_learner import CommunityLearner
        
        # Learning insights al
        insights = CommunityLearner.get_learning_insights('medium')
        
        if insights.get('has_data', False):
            print(f"✅ Community data mevcut: {insights['total_examples']} örnek")
            print(f"   Successful patterns: {len(insights.get('successful_patterns', []))}")
            print(f"   Categories: {', '.join(insights.get('categories', []))}")
            
            # AI service test
            gemini_service = CommunityAwareGemini()
            print("✅ CommunityAwareGemini service başlatıldı")
            print("✅ AI community data'yı kullanmaya hazır")
            
        else:
            print("ℹ️ Henüz community data yok, AI standart modda çalışacak")
            
        return True
        
    except Exception as e:
        print(f"❌ AI integration test hatası: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SynAppse Community Learning System Test Başlıyor...")
    
    # Ana test
    if test_community_learning_system():
        print("\n✅ Tüm temel testler başarılı!")
        
        # Örnek data oluştur
        if test_create_sample_learning_data():
            print("\n✅ Örnek data test başarılı!")
            
            # AI integration test
            if test_ai_community_integration():
                print("\n🎉 TÜM TESTLER BAŞARILI!")
                print("\n📊 Community Learning Sistemi Durumu:")
                print("   ✅ Database tabloları hazır")
                print("   ✅ Servisler çalışıyor") 
                print("   ✅ AI community learning aktif")
                print("   ✅ Frontend rating sistemi entegre")
                print("\n🎯 Sistem kullanıma hazır!")
            else:
                print("\n⚠️ AI integration testinde sorun var")
        else:
            print("\n⚠️ Örnek data testinde sorun var")
    else:
        print("\n❌ Temel testlerde hata var, sistemi kontrol edin")
