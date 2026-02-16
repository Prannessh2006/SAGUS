import logging
import json

logger = logging.getLogger(__name__)


class AutoIngestor:
    def __init__(self, neo4j, groq):
        self.neo4j = neo4j
        self.groq = groq

    async def ingest_concept(self, concept_name: str):
        logger.info(f"Auto-ingesting new concept: {concept_name}")

        prompt = f"""
Return STRICT JSON.

Extract academic knowledge for:
{concept_name}

Format:
{{
  "name": "...",
  "description": "...",
  "domain": "...",
  "prerequisites": ["...", "..."]
}}
"""

        llm_result = await self.groq.raw_completion(prompt)

        raw = llm_result["content"].strip()
        raw = raw.replace("```json", "").replace("```", "")

        try:
            data = json.loads(raw)
        except Exception:
            logger.error(f"Invalid JSON from LLM:\n{raw}")
            raise RuntimeError("LLM returned invalid JSON")

        name = data["name"]
        description = data.get("description", "")
        domain = data.get("domain", "General")
        prerequisites = data.get("prerequisites", [])

        await self.neo4j.execute_query(
            """
            MERGE (c:Concept {name: $name})
            SET c.description = $description,
                c.domain = $domain
            """,
            {
                "name": name,
                "description": description,
                "domain": domain,
            }
        )

        for prereq in prerequisites:
            await self.neo4j.execute_query(
                """
                MERGE (p:Concept {name: $prereq})
                MERGE (c:Concept {name: $name})
                MERGE (p)-[:PREREQUISITE_OF]->(c)
                """,
                {
                    "name": name,
                    "prereq": prereq,
                }
            )

        logger.info(f"Concept '{name}' successfully ingested.")
