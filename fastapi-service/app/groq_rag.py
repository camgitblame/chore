import json
import os
import numpy as np
from typing import List, Dict
from groq import Groq

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class GroqRAG:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.knowledge_base = self._load_knowledge()

    def _load_knowledge(self) -> List[Dict]:
        """Load knowledge base from JSON file"""
        knowledge_file = os.path.join(
            os.path.dirname(__file__), "rag", "knowledge_base.json"
        )

        if not os.path.exists(knowledge_file):
            return []

        try:
            with open(knowledge_file, "r") as f:
                data = json.load(f)
                return data.get("knowledge", [])
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return []

    def _simple_search(self, query: str, top_k: int = 3) -> List[str]:
        """Simple keyword-based search (no embeddings needed)"""
        if not self.knowledge_base:
            return []

        query_lower = query.lower()

        # Score each knowledge entry
        scored_entries = []
        for entry in self.knowledge_base:
            score = 0
            entry_text = f"{entry.get('category', '')} {entry.get('tip', '')} {entry.get('context', '')}".lower()

            # Simple keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 3:  # Skip short words
                    score += entry_text.count(word)

            if score > 0:
                scored_entries.append((score, entry.get("tip", "")))

        # Sort by score and return top_k
        scored_entries.sort(reverse=True, key=lambda x: x[0])
        return [tip for _, tip in scored_entries[:top_k]]

    def get_advice(self, chore: Dict, user_context: str = "") -> str:
        """Generate advice using Groq API"""
        if not self.client:
            return self._fallback_advice(chore)

        try:
            # Get relevant knowledge
            query = f"{chore.get('title', '')} {' '.join(chore.get('items', []))} {user_context}"
            relevant_tips = self._simple_search(query, top_k=3)

            # Build context
            context = (
                "\n".join([f"- {tip}" for tip in relevant_tips])
                if relevant_tips
                else "No specific tips available."
            )

            # Create prompt
            prompt = f"""You are a helpful household assistant. Give concise, practical advice for this chore.

Chore: {chore.get('title', 'Unknown')}
Items needed: {', '.join(chore.get('items', []))}
Steps: {', '.join(chore.get('steps', [])[:3])}
User context: {user_context or 'None'}

Relevant tips:
{context}

Provide 2-3 helpful tips in a friendly, encouraging tone. Keep it under 150 words."""

            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast & free
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful household assistant that gives concise, practical advice.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=200,
                top_p=0.9,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Groq API error: {e}")
            return self._fallback_advice(chore)

    def _fallback_advice(self, chore: Dict) -> str:
        """Fallback advice when Groq is unavailable"""
        tips = [
            "Break the task into smaller steps to make it less overwhelming.",
            "Set a timer and work in focused bursts - even 10 minutes makes a difference!",
            "Put on some music or a podcast to make the time go faster.",
            "Remember: done is better than perfect. Just getting started is the hardest part!",
        ]

        chore_name = chore.get("title", "this task")
        time_estimate = chore.get("time_min", 10)

        return (
            f"Great choice working on {chore_name}! This should take about {time_estimate} minutes. "
            + " ".join(tips[:2])
        )

    def is_available(self) -> bool:
        """Check if Groq API is configured"""
        return bool(GROQ_API_KEY and self.client)


# Global instance
groq_rag = GroqRAG()
