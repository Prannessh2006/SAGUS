from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.graph.neo4j_client import Neo4jClient, get_neo4j_client

router = APIRouter()

class KnowledgeIngestRequest(BaseModel):
    title: str
    content: str
    domain: str = "general"


@router.post("/ingest")
async def ingest_knowledge(request: KnowledgeIngestRequest, neo4j: Neo4jClient = Depends(get_neo4j_client)):
    query = """
    CREATE (c:Concept {
        id: $id,
        name: $name,
        description: $description,
        domain: $domain
    })
    RETURN c
    """

    await neo4j.execute_query(query, {
        "id": request.title.lower().replace(" ", "_"),
        "name": request.title,
        "description": request.content,
        "domain": request.domain
    })

    return {"status": "Concept ingested successfully"}
