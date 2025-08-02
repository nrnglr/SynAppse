"""
Daily Brain Health Tip Service
Manages cached daily brain health tips with 24-hour renewal cycle
"""

from django.core.cache import cache
from services.gemini_service import GeminiService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DailyBrainTipService:
    """
    Service for managing daily brain health tips with 24-hour caching
    """
    
    CACHE_KEY = "daily_brain_tip"
    CACHE_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds
    
    @classmethod
    def get_daily_tip(cls):
        """
        Get today's brain health tip from cache or generate new one
        Returns dict with tip and metadata
        """
        try:
            # Try to get from cache first
            cached_tip = cache.get(cls.CACHE_KEY)
            
            if cached_tip:
                logger.info("Returning cached daily brain tip")
                return cached_tip
            
            # Generate new tip if not in cache
            logger.info("Generating new daily brain tip")
            return cls._generate_and_cache_tip()
            
        except Exception as e:
            logger.error(f"Error in get_daily_tip: {e}", exc_info=True)
            return cls._get_fallback_tip()
    
    @classmethod
    def _generate_and_cache_tip(cls):
        """
        Generate new tip using AI and cache it
        """
        try:
            gemini_service = GeminiService()
            tip_text = gemini_service.generate_daily_brain_tip()
            
            if tip_text:
                tip_data = {
                    'tip': tip_text,
                    'generated_at': datetime.now().isoformat(),
                    'is_fallback': False
                }
                
                # Cache for 24 hours
                cache.set(cls.CACHE_KEY, tip_data, cls.CACHE_TIMEOUT)
                logger.info("New daily brain tip generated and cached")
                return tip_data
            else:
                logger.warning("AI failed to generate tip, using fallback")
                return cls._get_fallback_tip()
                
        except Exception as e:
            logger.error(f"Error generating daily tip: {e}", exc_info=True)
            return cls._get_fallback_tip()
    
    @classmethod
    def _get_fallback_tip(cls):
        """
        Return fallback tip when AI generation fails
        """
        return {
            'tip': "Bugün aldığın önemli bir kararda, yapay zeka yardımı almadan önce kendi görüşünü not et.",
            'generated_at': datetime.now().isoformat(),
            'is_fallback': True
        }
    
    @classmethod
    def force_regenerate(cls):
        """
        Force regenerate daily tip (for admin use)
        """
        cache.delete(cls.CACHE_KEY)
        return cls.get_daily_tip()
