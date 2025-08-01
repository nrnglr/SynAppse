"""
Community-Aware Gemini Service
Generates problems using community learning data and successful patterns
"""

import logging
from typing import Dict, List, Optional
from services.gemini_service import GeminiService
from exercises.problem_chain.community_learner import CommunityLearner
from exercises.problem_chain.models import CommunityLearningData

logger = logging.getLogger(__name__)


class CommunityAwareGemini(GeminiService):
    """
    Enhanced Gemini service that learns from community feedback and successful patterns
    """
    
    def __init__(self):
        super().__init__()
        self.use_community_learning = True
    
    def generate_community_optimized_problem(self, difficulty: str, context: Dict = None) -> str:
        """
        Generate problem using community insights and successful patterns
        """
        try:
            # Get community learning insights
            insights = CommunityLearner.get_learning_insights(difficulty)
            avoid_patterns = CommunityLearner.get_avoid_patterns(difficulty)
            
            if insights.get('has_data', False):
                # Generate with community data
                return self._generate_with_community_data(difficulty, insights, avoid_patterns, context)
            else:
                # Fallback to standard generation
                logger.info(f"No community data available for {difficulty}, using standard generation")
                return self._generate_standard_problem(difficulty, context)
                
        except Exception as e:
            logger.error(f"Error in community-optimized generation: {e}", exc_info=True)
            return self._generate_standard_problem(difficulty, context)
    
    def _generate_with_community_data(self, difficulty: str, insights: Dict, avoid_patterns: Dict, context: Dict = None) -> str:
        """
        Generate problem using community insights
        """
        try:
            # Build enhanced prompt with community data
            prompt = self._build_community_enhanced_prompt(difficulty, insights, avoid_patterns, context)
            
            # Generate with Gemini
            response = self.generate_content(prompt)
            
            if response and len(response.strip()) > 50:
                logger.info(f"Generated community-optimized problem for {difficulty} difficulty")
                return response.strip()
            else:
                # Fallback if community generation fails
                return self._generate_standard_problem(difficulty, context)
                
        except Exception as e:
            logger.error(f"Error generating with community data: {e}", exc_info=True)
            return self._generate_standard_problem(difficulty, context)
    
    def _build_community_enhanced_prompt(self, difficulty: str, insights: Dict, avoid_patterns: Dict, context: Dict = None) -> str:
        """
        Build enhanced prompt using community learning data
        """
        # Get best examples from community
        best_examples = insights.get('best_examples', [])
        patterns = insights.get('patterns', {})
        success_categories = insights.get('success_categories', [])
        
        prompt = f"""Sen yaratıcı problem çözme egzersizi için topluluk verilerinden öğrenen bir AI asistanısın.

TOPLULUK VERİLERİNDEN ÖĞRENME:
Başarılı Problem Örnekleri (Yüksek Puan Alanlar):
"""
        
        # Add successful examples
        for i, example in enumerate(best_examples[:3], 1):
            prompt += f"{i}. Problem: {example['problem'][:200]}...\n"
            prompt += f"   Çözüm: {example['solution'][:150]}...\n"
            prompt += f"   Puan: {example['score']}/5, Kategori: {example['category']}\n\n"
        
        # Add pattern insights
        if patterns:
            prompt += f"""
BAŞARILI PATTERN'LER:
- Ortalama kelime sayısı: {patterns.get('avg_word_count', 50):.0f}
- Ortalama başarı puanı: {patterns.get('avg_score', 4.0):.1f}
- Başarılı kategoriler: {', '.join(success_categories)}
"""
        
        # Add avoidance patterns
        if avoid_patterns.get('has_data', False):
            prompt += f"""
KAÇINILMASI GEREKEN PATTERN'LER:
- Düşük puan alan kategoriler: {', '.join(avoid_patterns.get('avoid_categories', []))}
- Yaygın sorunlar: {', '.join(avoid_patterns.get('common_issues', []))}
"""
        
        # Add context if provided
        if context:
            prompt += f"\nEK CONTEXT:\n{context}\n"
        
        # Main generation instruction with original Problem Chain rules
        prompt += f"""
GÖREV: {difficulty.upper()} zorluk seviyesinde PROBLEM CHAIN türünde problem üret.

❗ PROBLEM CHAIN KURALLARI (ZORUNLU):
- Problem günlük yaşamda karşılaşılabilecek SOMUT bir soruna yol açmalı
- İnsanlar "Bu sorunu nasıl çözerim?" diye düşünmeli
- Çözülebilir ve mantıklı olmalı
- 1-2 cümle uzunluğunda
- Türkçe olmalı
- Sadece problemi yaz, açıklama yapma

PROBLEM YAPISI: [Tuhaf/Absürd ama mümkün durum] + [Bu durumun yarattığı somut rahatsızlık/zorluk]

YAPMA (YANLIŞ):
- Matematik problemleri
- Bulmaca/bilmece türü sorular
- "Hangi eşyayı unutmuş?" tarzı mantık soruları
- Fantastik durumlar (zaman durdu, vb.)

YAP (DOĞRU):
- Gerçek hayat sorunu yaratan durumlar
- İnsanların rahatsız olduğu durumlar
- Yaratıcı çözüm gerektiren günlük sorunlar

TOPLULUK VERİLERİNDEN ÖĞRENİLEN:
1. Topluluk tarafından beğenilen pattern'leri kullan ama KOPYALAMA
2. Başarılı örneklerden ilham al ama özgün ol
3. Kaçınılması gereken pattern'lerden uzak dur

{difficulty.upper()} seviyesi için uygun karmaşıklık:
- Easy: Basit günlük hayat problemleri, açık çözümler
- Medium: Orta karmaşıklık, çoklu çözüm yolları, biraz absürd durum
- Hard: Karmaşık senaryolar, derinlemesine analiz, daha absürd ama mantıklı

Problem metni (sadece problem, çözüm değil):"""
        
        return prompt
    
    def _generate_standard_problem(self, difficulty: str, context: Dict = None) -> str:
        """
        Fallback to standard problem generation
        """
        try:
            from exercises.problem_chain.prompts import PROBLEM_CHAIN_START_PROMPTS
            prompt = PROBLEM_CHAIN_START_PROMPTS.get(difficulty, PROBLEM_CHAIN_START_PROMPTS['medium'])
            
            if context:
                prompt += f"\n\nEk context: {context}"
            
            response = self.generate_content(prompt)
            return response.strip() if response else "Varsayılan problem: Bir şehirde trafik sıkışıklığı sorunu var. Çözüm öneriniz?"
            
        except Exception as e:
            logger.error(f"Error in standard generation: {e}", exc_info=True)
            return "Bir toplulukta geri dönüşüm oranları düşük. Bu sorunu nasıl çözersiniz?"
    
    def generate_next_problem_with_community_learning(self, previous_problem: str, user_solution: str, difficulty: str) -> str:
        """
        Generate next problem in chain using community learning
        """
        try:
            # Get community insights for this difficulty
            insights = CommunityLearner.get_learning_insights(difficulty)
            
            # Create context from previous interaction
            context = {
                'previous_problem': previous_problem,
                'user_solution': user_solution,
                'chain_position': 'middle'  # or calculate based on round
            }
            
            # Enhanced prompt for chain continuation
            prompt = self._build_chain_continuation_prompt(
                previous_problem, user_solution, difficulty, insights, context
            )
            
            response = self.generate_content(prompt)
            
            if response and len(response.strip()) > 30:
                return response.strip()
            else:
                # Fallback to standard next problem generation
                from exercises.problem_chain.prompts import PROBLEM_CHAIN_NEXT_PROMPT
                fallback_prompt = PROBLEM_CHAIN_NEXT_PROMPT.format(
                    previous_problem=previous_problem,
                    user_solution=user_solution
                )
                return self.generate_content(fallback_prompt).strip()
                
        except Exception as e:
            logger.error(f"Error generating next problem with community learning: {e}", exc_info=True)
            # Fallback
            return f"Önceki çözümünüz '{user_solution[:50]}...' yeni bir problem yaratıyor: Nasıl devam edersiniz?"
    
    def _build_chain_continuation_prompt(self, previous_problem: str, user_solution: str, difficulty: str, insights: Dict, context: Dict) -> str:
        """
        Build prompt for continuing problem chain with community insights
        """
        prompt = f"""Sen problem zinciri egzersizi için topluluk verilerinden öğrenen AI asistanısın.

ÖNCEKI DURUM:
Problem: {previous_problem}
Kullanıcı Çözümü: {user_solution}

"""
        
        # Add community insights if available
        if insights.get('has_data', False):
            best_examples = insights.get('best_examples', [])
            if best_examples:
                prompt += "TOPLULUK VERİLERİNDEN BAŞARILI ZİNCİR ÖRNEKLERİ:\n"
                for example in best_examples[:2]:
                    prompt += f"- {example['problem'][:100]}...\n"
        
        prompt += f"""
GÖREV: Kullanıcının çözümünden doğan yeni bir PROBLEM CHAIN türü problem üret.

❗ PROBLEM CHAIN KURALLARI (ZORUNLU):
- Kullanıcının çözümü YENİ BİR SOMUT SORUNA dönüştür
- Problem günlük yaşamda karşılaşılabilecek durumlar olmalı
- İnsanlar "Bu yeni sorunu nasıl çözerim?" diye düşünmeli
- Çözülebilir ve mantıklı olmalı
- 1-2 cümle uzunluğunda
- Türkçe olmalı
- Sadece yeni problemi yaz, çözüm önerme

YAPMA (YANLIŞ):
- Matematik problemleri
- Bulmaca/bilmece türü sorular
- Mantık puzzleları
- Fantastik durumlar

YAP (DOĞRU):
- Kullanıcının çözümü başka bir günlük sorun yaratıyor
- Gerçek hayat komplikasyonları
- İnsanların rahatsız olduğu yeni durumlar

ÖRNEK ZİNCİR MANTIĞI:
Problem: "Apartman asansörü bozuldu, yaşlılar alışveriş yapamıyor"
Çözüm: "Genç komşular market listesi alıp alışveriş yapabilir"
→ YENİ PROBLEM: "Genç komşular sürekli alışveriş yaptıkları için kendi işleri aksıyor, yoruluyorlar"

{difficulty} seviyesine uygun zorluk, topluluk pattern'lerini kullan ama özgün ol.

Yeni problem:"""
        
        return prompt
    
    def evaluate_with_community_context(self, problems: List[str], solutions: List[str], difficulty: str) -> Dict:
        """
        Evaluate session with community learning context
        """
        try:
            # Get community benchmarks
            insights = CommunityLearner.get_learning_insights(difficulty)
            
            # Standard evaluation prompt with community context
            prompt = self._build_evaluation_prompt_with_community(problems, solutions, insights)
            
            response = self.generate_content(prompt)
            
            if response:
                # Parse evaluation response
                evaluation = self.parse_evaluation_response(response)
                
                # Add community-specific insights
                evaluation['community_comparison'] = self._compare_with_community(
                    evaluation, insights
                )
                
                return evaluation
            else:
                # Fallback evaluation
                return {
                    'creativity_score': 3,
                    'practicality_score': 3,
                    'feedback': 'Değerlendirme tamamlandı.'
                }
                
        except Exception as e:
            logger.error(f"Error in community-aware evaluation: {e}", exc_info=True)
            return {
                'creativity_score': 3,
                'practicality_score': 3,
                'feedback': 'Değerlendirme tamamlandı.'
            }
    
    def _build_evaluation_prompt_with_community(self, problems: List[str], solutions: List[str], insights: Dict) -> str:
        """
        Build evaluation prompt with community benchmarks
        """
        prompt = "Problem zinciri değerlendirmesi yapacaksın.\n\n"
        
        # Add problem-solution history
        for i, (problem, solution) in enumerate(zip(problems, solutions), 1):
            prompt += f"TUR {i}:\nProblem: {problem}\nÇözüm: {solution}\n\n"
        
        # Add community context
        if insights.get('has_data', False):
            patterns = insights.get('patterns', {})
            prompt += f"""
TOPLULUK KARŞILAŞTIRMASI:
- Topluluk ortalama puanı: {patterns.get('avg_score', 4.0):.1f}/5
- Başarılı kategoriler: {', '.join(insights.get('success_categories', []))}
"""
        
        prompt += """
DEĞERLENDIRME KRİTERLERİ:
1. Yaratıcılık (1-5): Özgünlük, yenilikçilik
2. Pratiklik (1-5): Uygulanabilirlik, gerçekçilik

JSON formatında yanıt ver:
{
    "creativity_score": X,
    "practicality_score": Y,
    "feedback": "Detaylı geri bildirim"
}"""
        
        return prompt
    
    def _compare_with_community(self, evaluation: Dict, insights: Dict) -> Dict:
        """
        Compare evaluation with community benchmarks
        """
        if not insights.get('has_data', False):
            return {}
        
        patterns = insights.get('patterns', {})
        community_avg = patterns.get('avg_score', 4.0)
        user_avg = (evaluation.get('creativity_score', 0) + evaluation.get('practicality_score', 0)) / 2
        
        comparison = {
            'user_score': user_avg,
            'community_average': community_avg,
            'performance_vs_community': 'above' if user_avg > community_avg else 'below' if user_avg < community_avg else 'average',
            'percentile_estimate': min(100, max(0, (user_avg / 5) * 100))
        }
        
        return comparison
