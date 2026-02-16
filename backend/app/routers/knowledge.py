from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.graph.neo4j_client import Neo4jClient, get_neo4j_client

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge"])

class ConceptCreate(BaseModel):
    id: str
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None

class RelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation: str = "PREREQUISITE_OF"

@router.post("/concept")
async def create_concept(data: ConceptCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)):
    query = """
    MERGE (c:Concept {id:$id})
    SET c.name=$name,
        c.domain=$domain,
        c.description=$description
    """
    await neo4j.execute_query(query, data.dict())
    return {"status": "concept_added", "id": data.id}

@router.post("/relation")
async def create_relation(data: RelationCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)):
    query = f"""
    MATCH (a:Concept {{id:$source_id}})
    MATCH (b:Concept {{id:$target_id}})
    MERGE (a)-[:{data.relation}]->(b)
    """
    await neo4j.execute_query(query, data.dict())
    return {"status": "relation_created"}
