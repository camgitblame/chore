"""
RAG-based advice generator
"""
import os
from typing import Optional, List, Dict, Any
from .ollama_client import OllamaClient
from .vector_store import VectorStore, initialize_knowledge_base


class AdviceGenerator:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.vector_store = VectorStore()
        self.advice_enabled = os.getenv("ADVICE_ENABLED", "true").lower() == "true"
        
        # Initialize knowledge base if needed
        if self.advice_enabled and self.vector_store.is_available():
            initialize_knowledge_base(self.vector_store)
    
    def is_available(self) -> bool:
        """Check if advice generation is available"""
        return (
            self.advice_enabled and 
            self.ollama_client.is_available() and
            self.vector_store.is_available()
        )
    
    def get_chore_advice(self, chore: Dict[str, Any], user_context: str = "") -> Optional[str]:
        """Generate advice for a specific chore"""
        if not self.is_available():
            return self._get_fallback_advice(chore)
        
        # Create search query
        chore_title = chore.get("title", "")
        chore_steps = " ".join(chore.get("steps", []))
        search_query = f"{chore_title} {chore_steps} {user_context}".strip()
        
        # Search for relevant advice
        relevant_docs = self.vector_store.search(search_query, n_results=3)
        
        # Build context for LLM
        context = self._build_context(chore, relevant_docs, user_context)
        
        # Generate advice using Ollama
        system_prompt = """You are a helpful assistant specializing in household chores and organization. 
        You provide practical, actionable advice for people who may have ADHD or autism spectrum conditions.
        Keep your advice concise, encouraging, and easy to follow. Focus on helpful tips and modifications.
        
        IMPORTANT: Do not use any markdown formatting like **bold**, *italic*, or other special characters.
        Use plain text only. Format lists with simple bullet points (•) or numbers."""

        prompt = f"""Based on the chore information and relevant tips below, provide helpful advice for completing this chore:

{context}

Provide 2-3 practical tips that would be most helpful for this specific chore. Keep your response concise and encouraging.
Use bullet points (•) for lists, not markdown formatting."""

        advice = self.ollama_client.generate(prompt, system_prompt)
        
        if advice:
            return advice
        else:
            return self._get_fallback_advice(chore)
    
    def _build_context(self, chore: Dict[str, Any], relevant_docs: List[Dict[str, Any]], user_context: str) -> str:
        """Build context for LLM prompt"""
        context_parts = []
        
        # Chore information
        context_parts.append(f"Chore: {chore.get('title', 'Unknown')}")
        context_parts.append(f"Estimated time: {chore.get('time_min', 0)} minutes")
        
        if chore.get("items"):
            context_parts.append(f"Required items: {', '.join(chore['items'])}")
        
        if chore.get("steps"):
            context_parts.append("Steps:")
            for i, step in enumerate(chore["steps"], 1):
                context_parts.append(f"  {i}. {step}")
        
        # User context
        if user_context:
            context_parts.append(f"User context: {user_context}")
        
        # Relevant tips from knowledge base
        if relevant_docs:
            context_parts.append("\nRelevant tips:")
            for doc in relevant_docs:
                context_parts.append(f"- {doc['text']}")
        
        return "\n".join(context_parts)
    
    def _get_fallback_advice(self, chore: Dict[str, Any]) -> str:
        """Provide fallback advice when RAG is not available"""
        chore_title = chore.get("title", "this chore").lower()
        time_estimate = chore.get("time_min", 0)
        
        advice_templates = {
            "kitchen": [
                "Start by gathering all necessary items before beginning.",
                "Work from top to bottom and left to right for efficiency.",
                "Take breaks if needed - it's better to pace yourself!"
            ],
            "cleaning": [
                "Put on some energizing music to make the task more enjoyable.",
                "Break the task into smaller steps if it feels overwhelming.",
                "Reward yourself with something nice when you're done!"
            ],
            "laundry": [
                "Set timers for washing and drying cycles so you don't forget.",
                "Fold clothes immediately after drying to prevent wrinkles.",
                "Keep a basket handy for items that need special attention."
            ]
        }
        
        # Try to match chore type
        advice = []
        for category, tips in advice_templates.items():
            if category in chore_title:
                advice = tips[:2]
                break
        
        if not advice:
            advice = [
                "Take your time and focus on one step at a time.",
                "Remember that done is better than perfect!"
            ]
        
        if time_estimate > 15:
            advice.append("Consider taking a short break halfway through if needed.")
        
        return "\n".join([f"• {tip}" for tip in advice])


# Global instance
advice_generator = AdviceGenerator()
