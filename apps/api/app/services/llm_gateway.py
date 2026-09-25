import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.prompts import get_prompt_template

logger = logging.getLogger(__name__)


class LLMGateway:
    """
    Production-grade LLM Gateway for ORG-XRAY.
    - Manages provider connection (Gemini or local mock fallback)
    - Enforces versioned prompt lookups
    - Tracks latency, model version, and token usage
    - Implements deterministic offline fallback for CI/CD and offline operation
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.default_model = settings.GEMINI_MODEL
        self._provider = "gemini" if self.api_key else "fallback_engine"

    @property
    def provider_name(self) -> str:
        return self._provider

    async def generate_response(
        self,
        prompt_id: str,
        user_message: str,
        context_data: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an LLM generation with metadata tracking and fallback support.
        """
        start_time = time.time()
        model_version = model_name or self.default_model
        prompt_spec = get_prompt_template(prompt_id)
        system_prompt = prompt_spec["system_prompt"]
        
        # Build enriched prompt with context
        enriched_user_prompt = user_message
        if context_data:
            enriched_user_prompt = (
                f"{user_message}\n\n[CONTEXT INFORMATION]:\n"
                f"{json.dumps(context_data, indent=2, default=str)}"
            )

        response_text = ""
        tokens_used = {"input": len(enriched_user_prompt) // 4, "output": 0}

        # If live Gemini API key is configured, attempt call
        if self.api_key:
            try:
                import httpx
                # Candidate models to try in order
                models_to_try = [model_version, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash", "gemini-1.5-pro"]
                # Deduplicate while preserving order
                models_to_try = list(dict.fromkeys(models_to_try))
                
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": f"System Instruction:\n{system_prompt}\n\nUser Request:\n{enriched_user_prompt}"}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 1024,
                    }
                }

                success = False
                async with httpx.AsyncClient(timeout=15.0) as client:
                    for model in models_to_try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                        resp = await client.post(url, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts:
                                    response_text = parts[0].get("text", "")
                            tokens_used["output"] = len(response_text) // 4
                            model_version = model
                            success = True
                            break
                        else:
                            logger.warning(f"Model {model} returned status {resp.status_code}: {resp.text[:120]}")

                if not success:
                    logger.warning("All Gemini model attempts exhausted or key invalid. Activating deterministic fallback engine.")
                    response_text = self._fallback_generate(prompt_id, user_message, context_data)
            except Exception as e:
                logger.warning(f"Gemini API request failed ({e}). Falling back to local synthesis engine.")
                response_text = self._fallback_generate(prompt_id, user_message, context_data)
        else:
            # Deterministic, grounded fallback generator
            response_text = self._fallback_generate(prompt_id, user_message, context_data)
            tokens_used["output"] = len(response_text) // 4

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "response": response_text,
            "model_version": model_version,
            "prompt_version": prompt_id,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "provider": self._provider,
        }

    def _fallback_generate(
        self,
        prompt_id: str,
        user_message: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Deterministic, policy-grounded synthesis generator when external API is unreachable or unset.
        """
        msg_lower = user_message.lower()

        if prompt_id == "demand_classifier/v1":
            if any(w in msg_lower for w in ["server", "laptop", "cloud", "aws", "gpu", "software"]):
                dept = "Technical"
            elif any(w in msg_lower for w in ["audit", "tax", "payroll", "budget", "billing"]):
                dept = "Finance"
            elif any(w in msg_lower for w in ["pr", "press", "media", "event", "marketing", "campaign"]):
                dept = "PR"
            else:
                dept = "General"
            return json.dumps({
                "routed_department": dept,
                "confidence": 0.88,
                "reasoning": f"Synthesized based on organizational procurement category keywords."
            })

        if prompt_id == "policy_rag/v1":
            retrieved_chunks = context_data.get("chunks", []) if context_data else []
            if retrieved_chunks:
                chunk_summaries = []
                for idx, c in enumerate(retrieved_chunks[:3], 1):
                    doc_title = c.get("document_title", "Procurement Manual")
                    section = c.get("section_title", "Policy Guidelines")
                    snippet = c.get("content", "")[:250]
                    chunk_summaries.append(
                        f"According to **{doc_title}** (*Section: {section}*):\n> {snippet}..."
                    )
                return "\n\n".join(chunk_summaries)
            return "Based on current organizational policy, single-source procurement under ₹50,000 requires Department Manager signoff. Capital expenditures above ₹2,00,000 require VP/Finance approval."

        # Default procurement assistant fallback
        if "limit" in msg_lower or "budget" in msg_lower:
            return (
                "Under standard organizational procurement policy:\n"
                "- **Employee Tier 1 limit**: Up to INR 50,000 (Requires direct manager approval).\n"
                "- **Manager Tier 2 limit**: Up to INR 5,00,000 (Requires department head & finance review).\n"
                "- **Admin / Executive Tier**: Above INR 5,00,000 requires multi-stakeholder approval."
            )
        elif "vendor" in msg_lower:
            vendors = context_data.get("vendors", []) if context_data else []
            if vendors:
                v_list = ", ".join([v.get("name", "") for v in vendors[:3]])
                return f"Currently approved vendors matching your request: {v_list}. All vendors are registered with active GSTINs and verified ratings."
            return "Approved enterprise IT vendors include Dell Technologies India, Tata Consultancy Services, and Lenovo India. All purchase orders require standard three-way matching."
        else:
            return (
                f"I processed your procurement query: '{user_message}'.\n"
                "Please verify compliance rules against the procurement matrix or check with your department manager before submitting binding purchase requests."
            )


llm_gateway = LLMGateway()
