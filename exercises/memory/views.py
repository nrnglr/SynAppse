from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

from .models import MemorySession
from .prompts import get_topic_generation_prompt, get_text_generation_prompt, get_evaluation_prompt
from services.gemini_service import GeminiService
from users.activity_utils import create_exercise_activity, complete_exercise_activity

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MemoryStartView(APIView):
    """
    Start Memory Exercise
    - Create new session with difficulty
    - Generate 3 topic options via Gemini API
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            difficulty = data.get('difficulty')
            
            # Validate difficulty
            if difficulty not in ['easy', 'medium', 'hard']:
                return JsonResponse({
                    'error': 'Invalid difficulty level'
                }, status=400)
            
            # Create new memory session
            session = MemorySession.objects.create(difficulty=difficulty)
            
            # Create user activity tracking (if user is authenticated)
            activity = create_exercise_activity(
                user=request.user if request.user.is_authenticated else None,
                exercise_type='memory',
                difficulty=difficulty,
                session_id=str(session.session_id)
            )
            
            # Generate topic options via Gemini API
            try:
                gemini_service = GeminiService()
                prompt = get_topic_generation_prompt(difficulty)
                
                ai_response = gemini_service.generate_content(prompt)
                
                # Parse AI response to extract topic options
                topic_options = self._parse_topic_options(ai_response)
                
                # Save topic options to session
                session.topic_options = topic_options
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'session_id': str(session.session_id),
                    'difficulty': difficulty,
                    'topic_options': topic_options,
                    'ai_response': ai_response
                })
                
            except Exception as ai_error:
                logger.error(f"Gemini API Error: {ai_error}")
                
                # Fallback topic options if AI fails
                fallback_topics = self._get_fallback_topics(difficulty)
                session.topic_options = fallback_topics
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'session_id': str(session.session_id),
                    'difficulty': difficulty,
                    'topic_options': fallback_topics,
                    'fallback': True
                })
                
        except Exception as e:
            logger.error(f"Memory Start Error: {e}")
            return JsonResponse({
                'error': 'Failed to start memory exercise'
            }, status=500)
    
    def _parse_topic_options(self, ai_response):
        """Parse AI response to extract 3 topic options"""
        try:
            # Extract topics from AI response format
            # Expected format: [ A ] Topic1    [ B ] Topic2    [ C ] Topic3
            lines = ai_response.split('\n')
            topics = []
            
            for line in lines:
                if '[ A ]' in line:
                    topic = line.split('[ A ]')[1].strip()
                    if '[ B ]' in topic:
                        topic = topic.split('[ B ]')[0].strip()
                    topics.append({'id': 'A', 'name': topic})
                elif '[ B ]' in line:
                    topic = line.split('[ B ]')[1].strip()
                    if '[ C ]' in topic:
                        topic = topic.split('[ C ]')[0].strip()
                    topics.append({'id': 'B', 'name': topic})
                elif '[ C ]' in line:
                    topic = line.split('[ C ]')[1].strip()
                    topics.append({'id': 'C', 'name': topic})
            
            if len(topics) == 3:
                return topics
            else:
                # If parsing fails, extract topics differently
                return self._extract_topics_fallback(ai_response)
                
        except Exception as e:
            logger.error(f"Topic parsing error: {e}")
            return self._get_fallback_topics('medium')
    
    def _extract_topics_fallback(self, text):
        """Fallback topic extraction method"""
        # Simple extraction based on brackets
        import re
        pattern = r'\[\s*[ABC]\s*\]\s*([^[\]]+?)(?=\s*\[\s*[ABC]\s*\]|$)'
        matches = re.findall(pattern, text)
        
        topics = []
        for i, match in enumerate(matches[:3]):
            topics.append({
                'id': ['A', 'B', 'C'][i],
                'name': match.strip()
            })
        
        return topics if len(topics) == 3 else self._get_fallback_topics('medium')
    
    def _get_fallback_topics(self, difficulty):
        """Fallback topics if AI generation fails"""
        fallback_sets = {
            'easy': [
                {'id': 'A', 'name': 'Hayvanlar'},
                {'id': 'B', 'name': 'Uzay'},
                {'id': 'C', 'name': 'İnsan Vücudu'}
            ],
            'medium': [
                {'id': 'A', 'name': 'Psikoloji'},
                {'id': 'B', 'name': 'Bilim'},
                {'id': 'C', 'name': 'Teknoloji'}
            ],
            'hard': [
                {'id': 'A', 'name': 'Felsefe'},
                {'id': 'B', 'name': 'Kuantum Fiziği'},
                {'id': 'C', 'name': 'Nöroloji'}
            ]
        }
        
        return fallback_sets.get(difficulty, fallback_sets['medium'])


@method_decorator(csrf_exempt, name='dispatch')
class MemoryGenerateView(APIView):
    """
    Generate Memory Text
    - Find session by session_id
    - Generate educational text based on selected topic
    - Extract keywords for later evaluation
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            session_id = data.get('session_id')
            selected_topic_id = data.get('topic_id')  # A, B, or C
            
            # Validate inputs
            if not session_id or not selected_topic_id:
                return JsonResponse({
                    'error': 'session_id and topic_id are required'
                }, status=400)
            
            # Find session
            try:
                session = MemorySession.objects.get(session_id=session_id)
            except MemorySession.DoesNotExist:
                return JsonResponse({
                    'error': 'Session not found'
                }, status=404)
            
            # Find selected topic from options
            selected_topic_name = None
            for topic in session.topic_options:
                if topic.get('id') == selected_topic_id:
                    selected_topic_name = topic.get('name')
                    break
            
            if not selected_topic_name:
                return JsonResponse({
                    'error': 'Invalid topic selection'
                }, status=400)
            
            # Generate text via Gemini API
            try:
                gemini_service = GeminiService()
                prompt = get_text_generation_prompt(session.difficulty, selected_topic_name)
                
                ai_response = gemini_service.generate_content(prompt)
                
                # Extract clean text and keywords
                clean_text, keywords = self._process_generated_text(ai_response)
                
                # Update session with generated content
                session.selected_topic = selected_topic_name
                session.original_text = clean_text
                session.text_keywords = keywords
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'session_id': str(session.session_id),
                    'selected_topic': selected_topic_name,
                    'text': clean_text,
                    'keywords': keywords,
                    'word_count': len(clean_text.split())
                })
                
            except Exception as ai_error:
                logger.error(f"Text generation error: {ai_error}")
                
                # Fallback text if AI fails
                fallback_text, fallback_keywords = self._get_fallback_text(
                    session.difficulty, selected_topic_name
                )
                
                session.selected_topic = selected_topic_name
                session.original_text = fallback_text
                session.text_keywords = fallback_keywords
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'session_id': str(session.session_id),
                    'selected_topic': selected_topic_name,
                    'text': fallback_text,
                    'keywords': fallback_keywords,
                    'fallback': True
                })
                
        except Exception as e:
            logger.error(f"Memory Generate Error: {e}")
            return JsonResponse({
                'error': 'Failed to generate memory text'
            }, status=500)
    
    def _process_generated_text(self, ai_response):
        """Extract clean text and identify keywords from AI response"""
        try:
            # Remove formatting and extract clean text
            lines = ai_response.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip lines with emojis, formatting, or metadata
                if (line and 
                    not line.startswith('📖') and 
                    not line.startswith('Konu:') and
                    not line.startswith('#') and
                    not line.startswith('**') and
                    len(line) > 10):
                    # Remove quotes if present
                    line = line.strip('"').strip("'")
                    text_lines.append(line)
            
            # Join text
            clean_text = ' '.join(text_lines).strip()
            
            # Extract potential keywords (simple approach)
            keywords = self._extract_keywords(clean_text)
            
            return clean_text, keywords
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            return ai_response.strip(), []
    
    def _extract_keywords(self, text):
        """Simple keyword extraction from text"""
        import re
        
        # Split into words and filter meaningful terms
        words = re.findall(r'\b[A-Za-zçğıöşüÇĞIİÖŞÜ]{4,}\b', text)
        
        # Common stop words to exclude
        stop_words = {
            'olan', 'olan', 'için', 'daha', 'çok', 'gibi', 'olan', 'bir', 
            'bu', 'o', 'da', 'de', 'ile', 'kadar', 'sonra', 'önce',
            'şey', 'kişi', 'insan', 'oldu', 'olur', 'var', 'yok'
        }
        
        # Filter and get unique meaningful words
        keywords = []
        seen = set()
        
        for word in words:
            word_lower = word.lower()
            if (word_lower not in stop_words and 
                word_lower not in seen and
                len(word) >= 4):
                keywords.append(word)
                seen.add(word_lower)
                
                if len(keywords) >= 8:  # Limit keywords
                    break
        
        return keywords[:5]  # Return top 5 keywords
    
    def _get_fallback_text(self, difficulty, topic):
        """Fallback text if AI generation fails"""
        fallback_texts = {
            'easy': {
                'Hayvanlar': ("Köpekler insanlığın en eski dostlarından biridir. Binlerce yıl önce kurdlardan evcilleştirildiler. Köpeklerin koku alma duyusu insanlardan 40 kat daha güçlüdür. Bu nedenle poliste, itfaiyede ve hastanelerde çalışabilirler. Köpekler sadık, akıllı ve eğitilebilir hayvanlardır. İnsanlarla güçlü bağlar kurarlar ve ailenin bir parçası olurlar. Farklı ırklarda köpekler vardır ve her birinin kendine özgü özellikleri bulunur.", 
                ['köpek', 'evcil', 'koku', 'sadık', 'eğitim']),
                
                'Uzay': ("Güneş sistemimizde sekiz gezegen bulunur. En büyüğü Jüpiter, en küçüğü ise Merkür'dür. Mars kırmızı rengiyle ünlüdür ve üzerinde su olduğu düşünülür. Satürn'ün etrafında güzel halkalar vardır. Dünya'dan ay'a gitmek üç gün sürer. Uzayda sesler duyulmaz çünkü hava yoktur. Astronotlar uzayda ağırlıksız kalırlar ve yüzerler.", 
                ['gezegen', 'Mars', 'Satürn', 'astronot', 'ağırlıksız'])
            },
            'medium': {
                'Psikoloji': ("Kalabalık etkisi, insanların grup halindeyken bireysel sorumluluklarını azalttığı psikolojik bir olgudur. Bu durumda kişiler, 'başkası yapar' düşüncesiyle hareket etmezler. 1964'te New York'ta Kitty Genovese olayında 38 kişi bir kadının saldırıya uğradığını görmesine rağmen kimse yardım çağırmamıştır. Araştırmacılar bu olayı inceleyerek 'sorumluluk dağılımı' kavramını geliştirmişlerdir. Ne kadar çok kişi olursa, herkesin sorumluluğu o kadar azalır.", 
                ['kalabalık', 'sorumluluk', 'grup', 'davranış', 'dağılım'])
            }
        }
        
        if difficulty in fallback_texts and topic in fallback_texts[difficulty]:
            return fallback_texts[difficulty][topic]
        
        # Default fallback
        return ("Bu konu hakkında genel bilgi vermek gerekirse, konuyla ilgili temel kavramlar ve örnekler bulunmaktadır. Detaylı inceleme yapıldığında farklı perspektifler ortaya çıkar.", 
                ['konu', 'kavram', 'örnek', 'perspektif', 'analiz'])


@method_decorator(csrf_exempt, name='dispatch')
class MemorySubmitView(APIView):
    """
    Submit Memory Responses
    - Receive user recall, keywords, and synthesis
    - Store responses in session
    - Prepare for evaluation
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            session_id = data.get('session_id')
            user_recall = data.get('user_recall', '')
            user_keywords = data.get('user_keywords', [])
            reading_time = data.get('reading_time', 0)
            
            # Validate inputs
            if not session_id:
                return JsonResponse({
                    'error': 'session_id is required'
                }, status=400)
            
            # Find session
            try:
                session = MemorySession.objects.get(session_id=session_id)
            except MemorySession.DoesNotExist:
                return JsonResponse({
                    'error': 'Session not found'
                }, status=404)
            
            # Validate that we have text to evaluate against
            if not session.original_text:
                return JsonResponse({
                    'error': 'No text found for evaluation'
                }, status=400)
            
            # Clean and validate user inputs
            user_recall = user_recall.strip()
            
            # Ensure we have at least recall content
            if not user_recall:
                return JsonResponse({
                    'error': 'Recall text must be provided'
                }, status=400)
            
            # Clean keywords list
            if isinstance(user_keywords, str):
                user_keywords = [kw.strip() for kw in user_keywords.split(',') if kw.strip()]
            elif not isinstance(user_keywords, list):
                user_keywords = []
            
            # Limit to 3 keywords max
            user_keywords = user_keywords[:3]
            
            # Update session with user responses
            session.user_recall = user_recall
            session.user_keywords = user_keywords
            session.reading_time = reading_time
            session.save()
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.session_id),
                'message': 'Responses saved successfully',
                'ready_for_evaluation': True
            })
            
        except Exception as e:
            logger.error(f"Memory Submit Error: {e}")
            return JsonResponse({
                'error': 'Failed to save responses'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MemoryCompleteView(APIView):
    """
    Complete Memory Exercise
    - Evaluate user performance via Gemini API
    - Calculate scores and provide feedback
    - Mark session as completed
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            session_id = data.get('session_id')
            
            # Validate input
            if not session_id:
                return JsonResponse({
                    'error': 'session_id is required'
                }, status=400)
            
            # Find session
            try:
                session = MemorySession.objects.get(session_id=session_id)
            except MemorySession.DoesNotExist:
                return JsonResponse({
                    'error': 'Session not found'
                }, status=404)
            
            # Validate session has required data
            if not session.original_text or not session.user_recall:
                return JsonResponse({
                    'error': 'Incomplete session data for evaluation'
                }, status=400)
            
            # Evaluate performance via Gemini API
            try:
                gemini_service = GeminiService()
                prompt = get_evaluation_prompt(
                    session.original_text,
                    session.text_keywords,
                    session.user_recall,
                    session.user_keywords,
                    session.user_question or "",  # Use Q&A instead of synthesis
                    "question"  # Updated type
                )
                
                ai_response = gemini_service.generate_content(prompt)
                
                # Parse evaluation response
                evaluation_data = self._parse_evaluation_response(ai_response)
                
                # Add overall score to scores if not present
                scores = evaluation_data.get('scores', {})
                if 'overall' not in scores:
                    scores['overall'] = self._calculate_overall_score(scores)
                
                # Update session with results
                session.scores = scores
                session.ai_feedback = evaluation_data.get('feedback', '')
                session.alternative_keywords = evaluation_data.get('alternative_keywords', [])
                session.is_completed = True
                session.save()
                
                # Calculate overall score
                overall_score = session.get_overall_score()
                
                # Complete user activity tracking
                complete_exercise_activity(
                    user=request.user if request.user.is_authenticated else None,
                    session_id=str(session.session_id),
                    scores=session.scores,
                    overall_score=overall_score,
                    exercise_data={
                        'original_text': session.original_text,
                        'user_recall': session.user_recall,
                        'user_keywords': session.user_keywords,
                        'user_question': session.user_question,
                        'ai_answer': session.ai_answer,
                        'reading_time': session.reading_time
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'session_id': str(session.session_id),
                    'evaluation': {
                        'scores': session.scores,
                        'overall_score': overall_score,
                        'feedback': session.ai_feedback,
                        'alternative_keywords': session.alternative_keywords,
                        'comparison': {
                            'original_text': session.original_text,
                            'user_recall': session.user_recall,
                            'original_keywords': session.text_keywords,
                            'user_keywords': session.user_keywords,
                            'user_question': session.user_question or '',
                            'ai_answer': session.ai_answer or ''
                        }
                    },
                    'completed': True
                })
                
            except Exception as ai_error:
                logger.error(f"Evaluation error: {ai_error}")
                
                # Fallback evaluation if AI fails
                fallback_scores = self._get_fallback_evaluation(session)
                # Add overall score to fallback
                fallback_scores['overall'] = self._calculate_overall_score(fallback_scores)
                
                session.scores = fallback_scores
                session.ai_feedback = "Değerlendirme tamamlandı. Devam ettiğiniz için teşekkürler!"
                session.is_completed = True
                session.save()
                
                # Complete user activity tracking (fallback)
                complete_exercise_activity(
                    user=request.user if request.user.is_authenticated else None,
                    session_id=str(session.session_id),
                    scores=fallback_scores,
                    overall_score=session.get_overall_score(),
                    exercise_data={
                        'original_text': session.original_text,
                        'user_recall': session.user_recall,
                        'user_keywords': session.user_keywords,
                        'user_question': session.user_question,
                        'ai_answer': session.ai_answer,
                        'reading_time': session.reading_time,
                        'fallback': True
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'session_id': str(session.session_id),
                    'evaluation': {
                        'scores': fallback_scores,
                        'overall_score': session.get_overall_score(),
                        'feedback': session.ai_feedback,
                        'alternative_keywords': [],
                        'comparison': {
                            'original_text': session.original_text or '',
                            'user_recall': session.user_recall or '',
                            'original_keywords': session.text_keywords or [],
                            'user_keywords': session.user_keywords or [],
                            'user_question': session.user_question or '',
                            'ai_answer': session.ai_answer or ''
                        },
                        'fallback': True
                    },
                    'completed': True
                })
                
        except Exception as e:
            logger.error(f"Memory Complete Error: {e}")
            return JsonResponse({
                'error': 'Failed to complete memory exercise'
            }, status=500)
    
    def _parse_evaluation_response(self, ai_response):
        """Parse AI evaluation response (expects JSON format)"""
        try:
            # Try to extract JSON from response
            import re
            
            # Look for JSON block in response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no code block, try to find JSON directly
                json_str = ai_response.strip()
            
            # Parse JSON
            evaluation_data = json.loads(json_str)
            
            # Validate required fields
            if 'scores' not in evaluation_data:
                raise ValueError("No scores in evaluation")
            
            return evaluation_data
            
        except Exception as e:
            logger.error(f"Evaluation parsing error: {e}")
            # Return default structure
            return {
                'scores': {'recall': 7, 'keywords': 6},
                'feedback': 'Değerlendirme tamamlandı.',
                'alternative_keywords': []
            }
    
    def _calculate_overall_score(self, scores):
        """Calculate overall score from individual scores"""
        score_values = [
            scores.get('recall', 0),
            scores.get('keywords', 0)
        ]
        return round(sum(score_values) / len(score_values), 1) if score_values else 0
    
    def _get_fallback_evaluation(self, session):
        """Fallback evaluation scoring if AI fails"""
        # Simple rule-based scoring
        recall_score = min(10, max(1, len(session.user_recall.split()) // 5))
        keyword_score = min(10, max(1, len(session.user_keywords) * 3))
        
        return {
            'recall': recall_score,
            'keywords': keyword_score
        }


@method_decorator(csrf_exempt, name='dispatch')
class MemoryQuestionView(APIView):
    """
    Handle Q&A for Memory Exercise
    - Validate if question is relevant to the text
    - Generate AI answer if question is relevant
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            session_id = data.get('session_id')
            user_question = data.get('question', '').strip()
            
            # Validate inputs
            if not session_id or not user_question:
                return JsonResponse({
                    'error': 'session_id and question are required'
                }, status=400)
            
            # Find session
            try:
                session = MemorySession.objects.get(session_id=session_id)
            except MemorySession.DoesNotExist:
                return JsonResponse({
                    'error': 'Session not found'
                }, status=404)
            
            # Validate that we have text to validate against
            if not session.original_text:
                return JsonResponse({
                    'error': 'No text found for validation'
                }, status=400)
            
            # Use Gemini to validate question relevance and generate answer
            try:
                gemini_service = GeminiService()
                
                # Validation prompt
                validation_prompt = f"""
Metin: "{session.original_text}"

Kullanıcı Sorusu: "{user_question}"

Bu soru yukarıdaki metinle ilgili mi? Sadece "EVET" veya "HAYIR" ile cevapla.
Eğer EVET ise, soruya metne dayanarak kısa ve net bir cevap ver.

Format:
İLGİLİ: EVET/HAYIR
CEVAP: [Eğer ilgili ise kısa cevap]
"""
                
                ai_response = gemini_service.generate_content(validation_prompt)
                
                # Parse response
                is_relevant = False
                ai_answer = ""
                
                lines = ai_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('İLGİLİ:'):
                        is_relevant = 'EVET' in line.upper()
                    elif line.startswith('CEVAP:'):
                        ai_answer = line.replace('CEVAP:', '').strip()
                
                # Update session with Q&A
                session.user_question = user_question
                session.question_is_relevant = is_relevant
                session.ai_answer = ai_answer if is_relevant else "Soru metinle ilgili değil."
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'question_relevant': is_relevant,
                    'ai_answer': session.ai_answer,
                    'message': 'Soru kaydedildi ve cevaplandı' if is_relevant else 'Soru metinle ilgili değil'
                })
                
            except Exception as ai_error:
                logger.error(f"Q&A processing error: {ai_error}")
                
                # Fallback: Save question but mark as error
                session.user_question = user_question
                session.question_is_relevant = False
                session.ai_answer = "Teknik bir hata oluştu, sorunuz kaydedildi."
                session.save()
                
                return JsonResponse({
                    'success': True,
                    'question_relevant': False,
                    'ai_answer': session.ai_answer,
                    'message': 'Soru kaydedildi ama değerlendirilemedi'
                })
                
        except Exception as e:
            logger.error(f"Memory Question Error: {e}")
            return JsonResponse({
                'error': 'Soru işlenirken hata oluştu'
            }, status=500)
