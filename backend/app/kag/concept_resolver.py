from rapidfuzz import process, fuzz

class ConceptResolver:

    def __init__(self, neo4j):
        self.neo4j = neo4j

    async def resolve(self, user_query: str):
        records = await self.neo4j.execute_query(
            "MATCH (c:Concept) RETURN c.name AS name"
        )

        names = [r["name"] for r in records]

        if not names:
            return "__fallback__"

        match, score, _ = process.extractOne(
            user_query,
            names,
            scorer=fuzz.WRatio
        )

        if score < 80:
            return None

        return match
