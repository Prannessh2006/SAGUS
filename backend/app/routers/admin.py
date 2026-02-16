from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.graph.neo4j_client import Neo4jClient, get_neo4j_client
from fastapi import APIRouter, Depends
from app.graph.neo4j_client import Neo4jClient, get_neo4j_client
from app.data.curriculum_dataset import load_sample_curriculum

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/load-curriculum")
async def load_curriculum(neo4j: Neo4jClient = Depends(get_neo4j_client)):
    await load_sample_curriculum(neo4j)
    return {"status": "Curriculum Loaded Successfully"}


class ConceptCreate(BaseModel):
    id: str
    name: str
    domain: str
    description: str
    difficulty: int = 1


class PrerequisiteCreate(BaseModel):
    concept_id: str
    requires_id: str


class MasteryCreate(BaseModel):
    student_id: str
    concept_id: str
    mastery_level: float


@router.post("/concept")
async def create_concept(data: ConceptCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)):
    query = """
    MERGE (c:Concept {id: $id})
    SET c.name = $name,
        c.domain = $domain,
        c.description = $description,
        c.difficulty = $difficulty
    """
    await neo4j.execute_query(query, data.dict())
    return {"status": "Concept created", "concept": data.id}


@router.post("/prerequisite")
async def add_prerequisite(data: PrerequisiteCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)):
    query = """
    MATCH (c:Concept {id:$concept_id})
    MATCH (p:Concept {id:$requires_id})
    MERGE (c)-[:REQUIRES]->(p)
    """
    await neo4j.execute_query(query, data.dict())
    return {"status": "Prerequisite linked"}


@router.post("/student/mastery")
async def add_mastery(data: MasteryCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)):
    query = """
    MERGE (s:Student {id:$student_id})
    WITH s
    MATCH (c:Concept {id:$concept_id})
    MERGE (s)-[m:MASTERS]->(c)
    SET m.mastery_level = $mastery_level
    """
    await neo4j.execute_query(query, data.dict())
    return {"status": "Mastery recorded"}
