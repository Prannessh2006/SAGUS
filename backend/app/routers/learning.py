from fastapi import APIRouter, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

from app.graph.neo4j_client import Neo4jClient, get_neo4j_client
from app.kag.traversal_engine import TraversalEngine, TraversalResult
from app.kag.gap_analyzer import GapAnalyzer
from app.kag.context_builder import ContextBuilder
from app.kag.concept_resolver import ConceptResolver
from app.kag.auto_ingest import AutoIngestor
from app.llm.groq_client import GroqClient, get_groq_client

router = APIRouter()
logger = logging.getLogger(__name__)


class LearningRequest(BaseModel):
    student_id: str
    query: str
    context: Optional[Dict[str, Any]] = None


class LearningResponse(BaseModel):
    student_id: str
    query: str
    response: str
    response_type: str
    target_concept: Optional[Dict[str, Any]]
    prerequisites: List[Dict[str, Any]]
    knowledge_gaps: List[Dict[str, Any]]
    readiness_score: float
    can_proceed: bool
    reasoning_path: List[str]
    llm_usage: Optional[Dict[str, int]]


@router.post("/ask", response_model=LearningResponse)
async def kag_learning_interaction(request: LearningRequest, neo4j: Neo4jClient = Depends(get_neo4j_client), groq: GroqClient = Depends(get_groq_client)) -> Dict[str, Any]:
    logger.info("=== KAG PIPELINE START ===")
    logger.info(f"Student: {request.student_id}")
    logger.info(f"Query: {request.query}")

    traversal_engine = TraversalEngine(neo4j)
    gap_analyzer = GapAnalyzer(neo4j)
    context_builder = ContextBuilder()
    resolver = ConceptResolver(neo4j)
    ingestor = AutoIngestor(neo4j, groq)

    resolved_concept = await resolver.resolve(request.query)

    if not resolved_concept:
        logger.info("Concept not found → triggering Auto-Ingestion")
        await ingestor.ingest_concept(request.query)
        resolved_concept = request.query
        logger.info(f"Concept '{request.query}' ingested dynamically")

    traversal_context = await traversal_engine.traverse(resolved_concept, request.student_id)

    if traversal_context.result == TraversalResult.CONCEPT_NOT_FOUND:
        return {
            "student_id": request.student_id,
            "query": request.query,
            "response": "Concept still not found after ingestion.",
            "response_type": "refuse",
            "target_concept": None,
            "prerequisites": [],
            "knowledge_gaps": [],
            "readiness_score": 0.0,
            "can_proceed": False,
            "reasoning_path": ["Concept not found"],
            "llm_usage": None
        }

    gap_analysis = await gap_analyzer.analyze_gaps(traversal_context, request.student_id)

    reasoning_context = context_builder.build_context(traversal_context, gap_analysis)

    llm_response = await groq.verbalize(reasoning_context, request.query)

    target_concept = None
    if traversal_context.target_concept:
        target_concept = {
            "id": traversal_context.target_concept.id,
            "name": traversal_context.target_concept.name,
            "domain": traversal_context.target_concept.domain,
            "description": traversal_context.target_concept.description
        }

    prerequisites = [
        {"id": c.id, "name": c.name, "domain": c.domain}
        for c in traversal_context.dependency_chain.prerequisites
    ] if traversal_context.dependency_chain else []

    knowledge_gaps = [
        {
            "concept_id": g.concept.id,
            "concept_name": g.concept.name,
            "priority": g.priority.value,
            "type": g.gap_type.value,
            "recommended_action": g.recommended_action
        }
        for g in gap_analysis.critical_gaps + gap_analysis.secondary_gaps
    ]

    return {
        "student_id": request.student_id,
        "query": request.query,
        "response": llm_response.content,
        "response_type": reasoning_context.response_type,
        "target_concept": target_concept,
        "prerequisites": prerequisites,
        "knowledge_gaps": knowledge_gaps,
        "readiness_score": traversal_context.confidence_score,
        "can_proceed": gap_analysis.can_proceed,
        "reasoning_path": traversal_context.reasoning_path,
        "llm_usage": llm_response.usage
    }
