from ai.gemini.service import GeminiService

from ai.prompts.critical import generate_critical_exercise as get_critical_prompt
from ai.prompts.memory import generate_memory_exercise as get_memory_prompt
from ai.prompts.creativity import generate_creativity_exercise as get_creativity_prompt
from ai.prompts.strategy import generate_strategy_exercise as get_strategy_prompt

gemini_service = GeminiService()

def generate_critical_exercise():
    prompt = get_critical_prompt()
    return gemini_service.generate_text(prompt)

def generate_memory_exercise():
    prompt = get_memory_prompt()
    return gemini_service.generate_text(prompt)

def generate_creativity_exercise():
    prompt = get_creativity_prompt()
    return gemini_service.generate_text(prompt)

def generate_strategy_exercise():
    prompt = get_strategy_prompt()
    return gemini_service.generate_text(prompt)
