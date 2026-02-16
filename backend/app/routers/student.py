from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import Response

from app.graph.neo4j_client import Neo4jClient, get_neo4j_client
from app.graph.cypher_queries import queries

router = APIRouter()


@router.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str) -> Response:
    return Response(status_code=200)


class StudentCreate(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., description="Student's full name")
    grade_level: int = Field(..., ge=1, le=12, description="Current grade level")
    learning_style: Optional[str] = Field(default="visual", description="Preferred learning style")


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    learning_style: Optional[str] = None


class MasteryUpdate(BaseModel):
    concept_id: str
    mastery_level: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class StruggleRecord(BaseModel):
    concept_id: str
    error_pattern: str = Field(..., description="Description of the error pattern")


class StudentResponse(BaseModel):
    student_id: str
    name: str
    grade_level: int
    learning_style: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class KnowledgeStateResponse(BaseModel):
    student_id: str
    mastered_concepts: List[Dict[str, Any]]
    struggling_concepts: List[Dict[str, Any]]
    total_concepts_known: int
    grade_progress: Dict[str, float]


@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    result = await neo4j.execute_query(
        queries.CREATE_STUDENT,
        {
            "student_id": student.student_id,
            "name": student.name,
            "grade_level": student.grade_level,
            "learning_style": student.learning_style
        }
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to create student")

    student_data = result[0]['s']
    return {
        "student_id": student_data['id'],
        "name": student_data['name'],
        "grade_level": student_data['grade_level'],
        "learning_style": student_data['learning_style'],
        "created_at": str(student_data.get('created_at', '')),
        "updated_at": str(student_data.get('updated_at', ''))
    }


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    result = await neo4j.execute_query(queries.GET_STUDENT, {"student_id": student_id})

    if not result:
        raise HTTPException(status_code=404, detail=f"Student not found: {student_id}")

    student_data = result[0]['s']
    return {
        "student_id": student_data['id'],
        "name": student_data['name'],
        "grade_level": student_data['grade_level'],
        "learning_style": student_data.get('learning_style', 'visual'),
        "created_at": str(student_data.get('created_at', '')),
        "updated_at": str(student_data.get('updated_at', ''))
    }


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, update: StudentUpdate, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    set_clauses = []
    params = {"student_id": student_id}

    if update.name:
        set_clauses.append("s.name = $name")
        params["name"] = update.name
    if update.grade_level:
        set_clauses.append("s.grade_level = $grade_level")
        params["grade_level"] = update.grade_level
    if update.learning_style:
        set_clauses.append("s.learning_style = $learning_style")
        params["learning_style"] = update.learning_style

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No update fields provided")

    set_clauses.append("s.updated_at = datetime()")

    query = f"""
    MATCH (s:Student {{id: $student_id}})
    SET {', '.join(set_clauses)}
    RETURN s
    """

    result = await neo4j.execute_query(query, params)

    if not result:
        raise HTTPException(status_code=404, detail=f"Student not found: {student_id}")

    student_data = result[0]['s']
    return {
        "student_id": student_data['id'],
        "name": student_data['name'],
        "grade_level": student_data['grade_level'],
        "learning_style": student_data.get('learning_style', 'visual'),
        "created_at": str(student_data.get('created_at', '')),
        "updated_at": str(student_data.get('updated_at', ''))
    }


@router.get("/{student_id}/knowledge-state", response_model=KnowledgeStateResponse)
async def get_knowledge_state(student_id: str, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    student = await neo4j.execute_query(queries.GET_STUDENT, {"student_id": student_id})

    if not student:
        raise HTTPException(status_code=404, detail=f"Student not found: {student_id}")

    mastered = await neo4j.execute_query(queries.GET_STUDENT_MASTERY, {"student_id": student_id})
    struggles = await neo4j.execute_query(queries.GET_STUDENT_STRUGGLES, {"student_id": student_id})

    grade_level = student[0]['s']['grade_level']
    progress = await neo4j.execute_query(
        queries.GET_LEARNING_PROGRESS,
        {"student_id": student_id, "domain": "Mathematics", "grade_level": grade_level}
    )

    grade_progress = {}
    if progress:
        grade_progress = {
            "total_concepts": progress[0].get('total_concepts', 0),
            "mastered_concepts": progress[0].get('mastered_count', 0),
            "progress_percentage": progress[0].get('progress_percentage', 0)
        }

    return {
        "student_id": student_id,
        "mastered_concepts": [
            {
                "concept_id": m['concept_id'],
                "concept_name": m['concept_name'],
                "mastery_level": m['mastery_level'],
                "confidence": m['confidence']
            }
            for m in mastered
        ],
        "struggling_concepts": [
            {
                "concept_id": s['concept_id'],
                "concept_name": s['concept_name'],
                "struggle_count": s['struggle_count'],
                "error_patterns": s['error_patterns']
            }
            for s in struggles
        ],
        "total_concepts_known": len(mastered),
        "grade_progress": grade_progress
    }


@router.post("/{student_id}/mastery")
async def update_mastery(student_id: str, mastery: MasteryUpdate, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    concept = await neo4j.execute_query(queries.GET_CONCEPT_BY_ID, {"concept_id": mastery.concept_id})

    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept not found: {mastery.concept_id}")

    result = await neo4j.execute_query(
        queries.UPDATE_MASTERY,
        {
            "student_id": student_id,
            "concept_id": mastery.concept_id,
            "mastery_level": mastery.mastery_level,
            "confidence": mastery.confidence
        }
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to update mastery")

    return {
        "status": "success",
        "student_id": student_id,
        "concept_id": mastery.concept_id,
        "mastery_level": mastery.mastery_level,
        "message": f"Mastery updated to {mastery.mastery_level:.0%}"
    }


@router.post("/{student_id}/struggle")
async def record_struggle(student_id: str, struggle: StruggleRecord, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    result = await neo4j.execute_query(
        queries.RECORD_STRUGGLE,
        {
            "student_id": student_id,
            "concept_id": struggle.concept_id,
            "error_pattern": struggle.error_pattern
        }
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to record struggle")

    return {
        "status": "success",
        "student_id": student_id,
        "concept_id": struggle.concept_id,
        "message": "Struggle pattern recorded"
    }


@router.get("/{student_id}/recommended")
async def get_recommended_concepts(student_id: str, threshold: float = 0.7, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    result = await neo4j.execute_query(
        queries.GET_RECOMMENDED_NEXT_CONCEPTS,
        {"student_id": student_id, "threshold": threshold}
    )

    recommendations = [
        {
            "concept_id": r['potential']['id'],
            "name": r['potential']['name'],
            "domain": r['potential'].get('domain'),
            "difficulty": r['potential'].get('difficulty')
        }
        for r in result
    ]

    return {
        "student_id": student_id,
        "recommendations": recommendations,
        "count": len(recommendations)
    }
