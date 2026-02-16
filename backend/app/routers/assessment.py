from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uuid

from app.graph.neo4j_client import Neo4jClient, get_neo4j_client
from app.graph.cypher_queries import queries
from app.kag.traversal_engine import TraversalEngine
from app.kag.gap_analyzer import GapAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)


class AssessmentCreate(BaseModel):
    student_id: str
    concept_id: str
    assessment_type: str = Field(default="quiz", description="Type: quiz, exercise, exam, practice")
    questions: List[Dict[str, Any]]


class AnswerSubmission(BaseModel):
    assessment_id: str
    student_id: str
    answers: List[Dict[str, Any]] = Field(..., description="List of answers with question_id and response")


class AssessmentResult(BaseModel):
    assessment_id: str
    student_id: str
    concept_id: str
    score: float
    mastery_level: float
    questions_correct: int
    questions_total: int
    feedback: List[Dict[str, Any]]
    recommendations: List[str]


class MasteryReport(BaseModel):
    student_id: str
    report_date: str
    domain_progress: Dict[str, Dict[str, Any]]
    recent_improvements: List[Dict[str, Any]]
    areas_struggling: List[Dict[str, Any]]
    recommended_focus: List[str]


active_assessments: Dict[str, Dict[str, Any]] = {}


@router.post("/create", response_model=Dict[str, Any])
async def create_assessment(assessment: AssessmentCreate, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    concept = await neo4j.execute_query(queries.GET_CONCEPT_BY_ID, {"concept_id": assessment.concept_id})
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept not found: {assessment.concept_id}")

    student = await neo4j.execute_query(queries.GET_STUDENT, {"student_id": assessment.student_id})
    if not student:
        raise HTTPException(status_code=404, detail=f"Student not found: {assessment.student_id}")

    assessment_id = f"assess_{uuid.uuid4().hex[:12]}"

    active_assessments[assessment_id] = {
        "assessment_id": assessment_id,
        "student_id": assessment.student_id,
        "concept_id": assessment.concept_id,
        "assessment_type": assessment.assessment_type,
        "questions": assessment.questions,
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending"
    }

    return {
        "assessment_id": assessment_id,
        "concept_id": assessment.concept_id,
        "student_id": assessment.student_id,
        "question_count": len(assessment.questions),
        "status": "created",
        "message": "Assessment created successfully"
    }


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(submission: AnswerSubmission, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    assessment = active_assessments.get(submission.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment not found: {submission.assessment_id}")

    if assessment["student_id"] != submission.student_id:
        raise HTTPException(status_code=403, detail="Student ID mismatch")

    questions = assessment["questions"]
    total_questions = len(questions)
    correct_count = 0
    feedback = []

    for question in questions:
        question_id = question.get("id")
        correct_answer = question.get("correct_answer")

        student_answer = None
        for answer in submission.answers:
            if answer.get("question_id") == question_id:
                student_answer = answer.get("response")
                break

        is_correct = student_answer == correct_answer
        if is_correct:
            correct_count += 1

        feedback.append({
            "question_id": question_id,
            "question": question.get("text"),
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        })

    score = correct_count / total_questions if total_questions > 0 else 0
    mastery_level = score

    await neo4j.execute_query(
        queries.UPDATE_MASTERY,
        {
            "student_id": submission.student_id,
            "concept_id": assessment["concept_id"],
            "mastery_level": mastery_level,
            "confidence": min(score + 0.1, 1.0)
        }
    )

    for fb in feedback:
        if not fb["is_correct"]:
            error_pattern = f"Incorrect: chose '{fb['student_answer']}' over '{fb['correct_answer']}'"
            await neo4j.execute_query(
                queries.RECORD_STRUGGLE,
                {
                    "student_id": submission.student_id,
                    "concept_id": assessment["concept_id"],
                    "error_pattern": error_pattern
                }
            )

    traversal_engine = TraversalEngine(neo4j)
    gap_analyzer = GapAnalyzer(neo4j)

    recommendations = []

    if mastery_level < 0.7:
        traversal = await traversal_engine.traverse(assessment["concept_id"], submission.student_id)
        if traversal.knowledge_gaps:
            for gap in traversal.knowledge_gaps[:3]:
                recommendations.append(f"Review prerequisite: {gap.name}")
    else:
        next_concepts = await neo4j.execute_query(
            queries.GET_CONCEPTS_THAT_REQUIRE,
            {"concept_id": assessment["concept_id"]}
        )

        for concept in next_concepts[:3]:
            recommendations.append(f"Ready to learn: {concept['c']['name']}")

    assessment["status"] = "completed"
    assessment["score"] = score
    assessment["mastery_level"] = mastery_level

    return {
        "assessment_id": submission.assessment_id,
        "student_id": submission.student_id,
        "concept_id": assessment["concept_id"],
        "score": score,
        "mastery_level": mastery_level,
        "questions_correct": correct_count,
        "questions_total": total_questions,
        "feedback": feedback,
        "recommendations": recommendations
    }


@router.get("/report/{student_id}", response_model=MasteryReport)
async def get_mastery_report(student_id: str, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    student = await neo4j.execute_query(queries.GET_STUDENT, {"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail=f"Student not found: {student_id}")

    mastered = await neo4j.execute_query(queries.GET_STUDENT_MASTERY, {"student_id": student_id})
    struggles = await neo4j.execute_query(queries.GET_STUDENT_STRUGGLES, {"student_id": student_id})

    domain_progress = {}
    for record in mastered:
        concept = record
        domain = concept.get('domain', 'General')

        if domain not in domain_progress:
            domain_progress[domain] = {"concepts_mastered": 0, "total_mastery": 0.0, "concepts": []}

        domain_progress[domain]["concepts_mastered"] += 1
        domain_progress[domain]["total_mastery"] += record.get('mastery_level', 0)
        domain_progress[domain]["concepts"].append({
            "name": concept.get('concept_name'),
            "mastery": record.get('mastery_level')
        })

    for domain in domain_progress:
        count = domain_progress[domain]["concepts_mastered"]
        if count > 0:
            domain_progress[domain]["average_mastery"] = domain_progress[domain]["total_mastery"] / count

    recent_improvements = sorted(mastered, key=lambda x: x.get('mastery_level', 0), reverse=True)[:5]

    improvements = [{
        "concept_name": r.get('concept_name'),
        "mastery_level": r.get('mastery_level'),
        "confidence": r.get('confidence')
    } for r in recent_improvements]

    areas_struggling = [{
        "concept_name": s.get('concept_name'),
        "struggle_count": s.get('struggle_count'),
        "error_patterns": s.get('error_patterns', [])[:3]
    } for s in struggles[:5]]

    recommended_focus = [
        f"Focus on: {struggle.get('concept_name')} - {struggle.get('struggle_count', 0)} struggles recorded"
        for struggle in struggles[:3]
    ]

    return {
        "student_id": student_id,
        "report_date": datetime.utcnow().isoformat(),
        "domain_progress": domain_progress,
        "recent_improvements": improvements,
        "areas_struggling": areas_struggling,
        "recommended_focus": recommended_focus
    }


@router.get("/history/{student_id}")
async def get_assessment_history(student_id: str, limit: int = 10, neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    student_assessments = [
        {
            "assessment_id": aid,
            "concept_id": a["concept_id"],
            "assessment_type": a["assessment_type"],
            "score": a.get("score"),
            "mastery_level": a.get("mastery_level"),
            "created_at": a["created_at"],
            "status": a["status"]
        }
        for aid, a in active_assessments.items()
        if a["student_id"] == student_id
    ]

    student_assessments.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "student_id": student_id,
        "assessments": student_assessments[:limit],
        "total_count": len(student_assessments)
    }


@router.get("/analytics/difficulty-stats")
async def get_difficulty_stats(neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    result = await neo4j.execute_query(queries.GET_CONCEPT_DIFFICULTY_STATS)

    stats = [{
        "concept_id": r['concept_id'],
        "concept_name": r['concept_name'],
        "avg_mastery": round(r['avg_mastery'], 3) if r['avg_mastery'] else 0,
        "student_count": r['student_count'],
        "difficulty_score": round(r['difficulty_score'], 3) if r['difficulty_score'] else 0
    } for r in result]

    return {"difficulty_stats": stats, "total_concepts_analyzed": len(stats)}


@router.get("/analytics/struggle-patterns")
async def get_struggle_patterns(neo4j: Neo4jClient = Depends(get_neo4j_client)) -> Dict[str, Any]:
    result = await neo4j.execute_query(queries.GET_COMMON_STRUGGLE_PATTERNS)

    patterns = [{
        "concept_id": r['concept_id'],
        "concept_name": r['concept_name'],
        "struggle_count": r['struggle_count'],
        "error_patterns": r['all_patterns'][:5] if r['all_patterns'] else []
    } for r in result]

    return {"struggle_patterns": patterns, "total_patterns": len(patterns)}
