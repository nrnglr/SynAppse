import os
import logging
from supabase import create_client, Client
from django.conf import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Service for interacting with Supabase
    """
    
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            raise Exception("Supabase credentials not set in environment variables.")
        
        self.client: Client = create_client(url, key)
    
    def save_exercise(self, table_name: str, exercise_data: dict) -> dict:
        """
        Save exercise to Supabase
        """
        try:
            response = self.client.table(table_name).insert(exercise_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Supabase save error: {e}")
            return None
    
    def get_exercises(self, table_name: str, filters: dict = None) -> list:
        """
        Get exercises from Supabase
        """
        try:
            query = self.client.table(table_name).select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.order('created_at', desc=True).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Supabase get error: {e}")
            return []
    
    def update_exercise(self, table_name: str, exercise_id: int, update_data: dict) -> dict:
        """
        Update exercise in Supabase
        """
        try:
            response = self.client.table(table_name).update(update_data).eq('id', exercise_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Supabase update error: {e}")
            return None
