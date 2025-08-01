"""
Community-aware Gemini Service for Problem Chain
Enhances problem generation with community insights and user patterns
"""

from services.gemini_service import GeminiService
from .pattern_analyzer import PatternAnalyzer, CommunityInsightService
from .prompts import PROBLEM_CHAIN_START_PROMPTS, PROBLEM_CHAIN_NEXT_PROMPT
import logging
import random

logger = logging.getLogger(__name__)

class CommunityAwareGemini:
    """
    Enhanced Gemini service that uses community insights for better problem generation
    """
    
    def __init__(self):
        self.base_gemini = GeminiService()
        self.pattern_analyzer = PatternAnalyzer()
    
    def generate_optimized_problem(self, difficulty, user=None, ip_address=None, previous_context=None):
        """
        Generate problem using community insights and user personalization
        """
        try:
            # Get community insights
            community_insights = self.pattern_analyzer.get_community_insights()
            
            # Get user personalization
            user_profile = self.pattern_analyzer.get_user_personalization(
                user=user, ip_address=ip_address
            )
            
            # Create enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(
                difficulty, community_insights, user_profile, previous_context
            )
            
            # Generate with Gemini
            result = self.base_gemini.generate_problem_chain_content(enhanced_prompt)
            
            if result:
                logger.info(f"Generated optimized problem for {difficulty} difficulty")
                return result
            else:
                # Fallback to basic generation
                logger.warning("Optimized generation failed, falling back to basic")
                return self._generate_fallback_problem(difficulty, community_insights)
                
        except Exception as e:
            logger.error(f"Error in optimized problem generation: {e}", exc_info=True)
            # Fallback to original method
            return self.base_gemini.generate_problem_chain_content(
                PROBLEM_CHAIN_START_PROMPTS.get(difficulty, PROBLEM_CHAIN_START_PROMPTS['medium'])
            )
    
    def generate_next_problem_optimized(self, previous_problem, user_solution, session_context):
        """
        Generate next problem using community patterns and user behavior
        """
        try:
            # Analyze user's solution pattern
            solution_analysis = self._analyze_solution_style(user_solution)
            
            # Get community insights for this problem type
            community_insights = self.pattern_analyzer.get_community_insights()
            
            # Create enhanced next prompt
            enhanced_prompt = self._create_enhanced_next_prompt(
                previous_problem, user_solution, solution_analysis, community_insights
            )
            
            result = self.base_gemini.generate_problem_chain_content(enhanced_prompt)
            
            if result:
                return result
            else:
                # Fallback to basic next generation
                basic_prompt = PROBLEM_CHAIN_NEXT_PROMPT.format(
                    previous_problem=previous_problem,
                    user_solution=user_solution
                )
                return self.base_gemini.generate_problem_chain_content(basic_prompt)
                
        except Exception as e:
            logger.error(f"Error in optimized next problem generation: {e}", exc_info=True)
            # Fallback
            basic_prompt = PROBLEM_CHAIN_NEXT_PROMPT.format(
                previous_problem=previous_problem,
                user_solution=user_solution
            )
            return self.base_gemini.generate_problem_chain_content(basic_prompt)
    
    def _create_enhanced_prompt(self, difficulty, community_insights, user_profile, previous_context):
        """Create enhanced prompt using community and user data"""
        
        base_prompt = PROBLEM_CHAIN_START_PROMPTS.get(difficulty, PROBLEM_CHAIN_START_PROMPTS['medium'])
        
        # Add community insights
        enhancement = "\n\nCOMMUNITY INSIGHTS:"
        
        # High-performing problem patterns
        high_performers = community_insights.get('high_performing_problems', [])
        if high_performers:
            enhancement += f"\nToplulukta başarılı problem türleri (ortalama {high_performers[0].get('rating', 0):.1f}/5 puan):"
            for problem in high_performers[:2]:
                problem_snippet = problem['problem_text'][:100] + "..." if len(problem['problem_text']) > 100 else problem['problem_text']
                enhancement += f"\n- {problem_snippet}"
        
        # User personalization
        if user_profile.get('personalization_available'):
            enhancement += f"\n\nKULLANICI PROFİLİ:"
            enhancement += f"\n- Öğrenme stili: {user_profile.get('learning_style', 'balanced')}"
            enhancement += f"\n- Ortalama problem süresi: {user_profile.get('avg_engagement_time', 60):.0f} saniye"
            
            if user_profile.get('learning_style') == 'fast':
                enhancement += "\n- BU KULLANICI: Hızlı çözüm arayan tip, daha direkt problemler üret"
            elif user_profile.get('learning_style') == 'methodical':
                enhancement += "\n- BU KULLANICI: Metoduk düşünen tip, daha detaylı problemler üret"
            elif user_profile.get('learning_style') == 'engaged':
                enhancement += "\n- BU KULLANICI: Egzersizleri seven tip, yaratıcı problemler üret"
        
        # Optimization guidelines
        enhancement += "\n\nOPTİMİZASYON TALİMATLARI:"
        enhancement += "\n- Topluluk verilerine göre optimize et"
        enhancement += "\n- Kullanıcı profiline uygun zorluk seviyesi"
        enhancement += "\n- Başarılı problem kalıplarını kullan"
        enhancement += "\n- Düşük performanslı pattern'lerden kaçın"
        
        return base_prompt + enhancement
    
    def _create_enhanced_next_prompt(self, previous_problem, user_solution, solution_analysis, community_insights):
        """Create enhanced next problem prompt"""
        
        base_prompt = PROBLEM_CHAIN_NEXT_PROMPT.format(
            previous_problem=previous_problem,
            user_solution=user_solution
        )
        
        enhancement = "\n\nCÖZÜM ANALİZİ:"
        enhancement += f"\n- Çözüm stili: {solution_analysis.get('style', 'balanced')}"
        enhancement += f"\n- Çözüm uzunluğu: {solution_analysis.get('length', 'orta')}"
        enhancement += f"\n- Yaratıcılık seviyesi: {solution_analysis.get('creativity', 'orta')}"
        
        # Adaptation suggestions
        if solution_analysis.get('style') == 'technical':
            enhancement += "\n- Sonraki problem daha teknik odaklı olsun"
        elif solution_analysis.get('style') == 'creative':
            enhancement += "\n- Sonraki problem yaratıcılığı test etsin"
        elif solution_analysis.get('style') == 'practical':
            enhancement += "\n- Sonraki problem pratik uygulama odaklı olsun"
        
        # Community patterns
        high_performers = community_insights.get('high_performing_problems', [])
        if high_performers:
            enhancement += f"\n\nTOPLULUK BAŞARILI PATTERNLERİ:"
            enhancement += f"\n- En başarılı problem türlerini referans al"
            enhancement += f"\n- Ortalama {high_performers[0].get('rating', 0):.1f}/5 puan alan pattern'leri kullan"
        
        return base_prompt + enhancement
    
    def _analyze_solution_style(self, solution_text):
        """Analyze user's solution to understand their thinking style"""
        try:
            solution = solution_text.lower().strip()
            
            # Determine solution style
            technical_keywords = ['sistem', 'algoritma', 'process', 'method', 'analiz', 'veri']
            creative_keywords = ['yaratıcı', 'farklı', 'yenilikçi', 'sanat', 'tasarım', 'hayal']
            practical_keywords = ['basit', 'kolay', 'hızlı', 'direkt', 'pratik', 'uygulamalı']
            
            technical_score = sum(1 for keyword in technical_keywords if keyword in solution)
            creative_score = sum(1 for keyword in creative_keywords if keyword in solution)
            practical_score = sum(1 for keyword in practical_keywords if keyword in solution)
            
            if technical_score > creative_score and technical_score > practical_score:
                style = 'technical'
            elif creative_score > practical_score:
                style = 'creative'
            elif practical_score > 0:
                style = 'practical'
            else:
                style = 'balanced'
            
            # Determine solution length category
            word_count = len(solution.split())
            if word_count < 10:
                length = 'kısa'
            elif word_count > 30:
                length = 'uzun'
            else:
                length = 'orta'
            
            # Creativity level based on unique words and solution length
            unique_words = len(set(solution.split()))
            if unique_words > word_count * 0.7 and word_count > 15:
                creativity = 'yüksek'
            elif unique_words < word_count * 0.5:
                creativity = 'düşük'
            else:
                creativity = 'orta'
            
            return {
                'style': style,
                'length': length,
                'creativity': creativity,
                'word_count': word_count,
                'unique_words': unique_words
            }
            
        except Exception as e:
            logger.error(f"Error analyzing solution style: {e}")
            return {'style': 'balanced', 'length': 'orta', 'creativity': 'orta'}
    
    def _generate_fallback_problem(self, difficulty, community_insights):
        """Generate fallback problem using community insights"""
        try:
            high_performers = community_insights.get('high_performing_problems', [])
            
            if high_performers:
                # Use a high-performing problem as template
                template_problem = random.choice(high_performers[:3])
                
                # Create a variation prompt
                variation_prompt = f"""
                Bu başarılı problemden esinlen ama YENİ bir problem oluştur:
                
                BAŞARILI PROBLEM ÖRNEĞİ: {template_problem['problem_text']}
                (Bu problem {template_problem['rating']:.1f}/5 puan aldı)
                
                Benzer yapıda ama tamamen farklı içerikte {difficulty} seviyede yeni problem üret.
                Aynı problem türü ve yapısını kullan ama konuyu değiştir.
                """
                
                return self.base_gemini.generate_problem_chain_content(variation_prompt)
            else:
                # Use original prompt
                return self.base_gemini.generate_problem_chain_content(
                    PROBLEM_CHAIN_START_PROMPTS.get(difficulty, PROBLEM_CHAIN_START_PROMPTS['medium'])
                )
                
        except Exception as e:
            logger.error(f"Error in fallback generation: {e}")
            return None


class ProblemQualityPredictor:
    """
    Predicts how well a generated problem might perform
    """
    
    @staticmethod
    def predict_problem_success(problem_text, difficulty):
        """
        Predict success rate of a problem based on community patterns
        Returns score 0-100
        """
        try:
            # Get similar problems from community data
            from .models import CommunityProblemMetrics
            
            # Simple keyword-based similarity (can be enhanced with ML later)
            problem_words = set(problem_text.lower().split())
            
            similar_problems = CommunityProblemMetrics.objects.filter(
                difficulty_level=difficulty,
                total_attempts__gte=3
            )
            
            similarity_scores = []
            for existing_problem in similar_problems:
                existing_words = set(existing_problem.problem_text.lower().split())
                common_words = problem_words.intersection(existing_words)
                similarity = len(common_words) / max(len(problem_words), len(existing_words), 1)
                
                if similarity > 0.1:  # At least 10% word similarity
                    similarity_scores.append({
                        'similarity': similarity,
                        'success_rate': existing_problem.success_rate,
                        'rating': existing_problem.avg_rating
                    })
            
            if similarity_scores:
                # Weighted average based on similarity
                total_weight = sum(s['similarity'] for s in similarity_scores)
                predicted_success = sum(
                    s['success_rate'] * s['similarity'] for s in similarity_scores
                ) / total_weight
                
                predicted_rating = sum(
                    s['rating'] * s['similarity'] for s in similarity_scores
                ) / total_weight
                
                # Combine success rate and rating for overall score
                overall_score = (predicted_success * 0.6) + (predicted_rating * 20 * 0.4)
                
                return min(100, max(0, overall_score))
            
            # Default prediction for new problem types
            return 50  # Neutral prediction
            
        except Exception as e:
            logger.error(f"Error predicting problem success: {e}")
            return 50
