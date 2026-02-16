from groq import AsyncGroq
from typing import Optional, Dict
from dataclasses import dataclass
import logging

from app.core.config import settings
from app.kag.context_builder import ReasoningContext

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    response_type: str


class GroqClient:
    def __init__(self):
        self._client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self._model = settings.GROQ_MODEL
        self._max_tokens = settings.GROQ_MAX_TOKENS
        self._temperature = settings.GROQ_TEMPERATURE

        self._system_prompt = """
You are a KAG verbalization engine.
ONLY express reasoning. NEVER add knowledge.
"""

    async def raw_completion(self, prompt: str) -> dict:
        """
        Direct LLM call used ONLY for auto-ingestion.
        This bypasses KAG guardrails intentionally.
        """

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "You extract structured academic knowledge."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )

            content = completion.choices[0].message.content

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens,
                }
            }

        except Exception as e:
            logger.error(f"Groq raw completion failed: {str(e)}")
            raise RuntimeError("LLM extraction failed")

    async def verbalize(
        self,
        context: ReasoningContext,
        user_query: Optional[str] = None
    ) -> LLMResponse:

        logger.info("Starting KAG verbalization")

        prompt = self._format_context_prompt(context, user_query)

        completion = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature
        )

        msg = completion.choices[0]

        return LLMResponse(
            content=msg.message.content,
            model=completion.model,
            usage={
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            },
            finish_reason=msg.finish_reason,
            response_type=context.response_type
        )


    def _format_context_prompt(self, context: ReasoningContext, user_query: str) -> str:

        return f"""
User Query: {user_query}

Target Concept:
{context.target_concept}

Prerequisites:
{context.dependency_chain}

Knowledge Gaps:
{context.knowledge_gaps}

Explain naturally WITHOUT adding external knowledge.
"""



groq_client = GroqClient()


async def get_groq_client() -> GroqClient:
    return groq_client
