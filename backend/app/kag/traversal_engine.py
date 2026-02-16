from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

from app.graph.neo4j_client import Neo4jClient
from app.graph.cypher_queries import queries
from app.core.config import settings

logger = logging.getLogger(__name__)


class TraversalResult(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CONCEPT_NOT_FOUND = "concept_not_found"


@dataclass
class ConceptNode:
    id: str
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    grade_level: Optional[int] = None
    difficulty: Optional[float] = None
    curriculum_code: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    
    @classmethod
    def from_neo4j(cls, data: Dict[str, Any]) -> 'ConceptNode':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description'),
            domain=data.get('domain'),
            grade_level=data.get('grade_level'),
            difficulty=data.get('difficulty'),
            curriculum_code=data.get('curriculum_code'),
            keywords=data.get('keywords', [])
        )


@dataclass
class DependencyChain:
    target_concept: ConceptNode
    prerequisites: List[ConceptNode]
    chain_depth: int
    is_complete: bool
    missing_concepts: List[str] = field(default_factory=list)


@dataclass
class TraversalContext:
    result: TraversalResult
    target_concept: Optional[ConceptNode] = None
    dependency_chain: Optional[DependencyChain] = None
    user_mastery_state: Dict[str, float] = field(default_factory=dict)
    knowledge_gaps: List[ConceptNode] = field(default_factory=list)
    reasoning_path: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    error_message: Optional[str] = None


class TraversalEngine:
    def __init__(self, neo4j_client: Neo4jClient):
        """
        Initialize traversal engine.
        
        Args:
            neo4j_client: Connected Neo4j client instance
        """
        self._client = neo4j_client
        self._max_depth = settings.MAX_DEPENDENCY_DEPTH
    
    async def resolve_concept(self, concept_query: str) -> Optional[ConceptNode]:
        logger.info(f"Resolving concept: {concept_query}")
        
        result = await self._client.execute_query(
            queries.GET_CONCEPT_BY_ID,
            {"concept_id": concept_query}
        )
        
        if result:
            logger.info(f"Found concept by ID: {concept_query}")
            return ConceptNode.from_neo4j(result[0]['c'])
        

        result = await self._client.execute_query(
            queries.GET_CONCEPT_BY_NAME,
            {"name": concept_query}
        )
        
        if result:
            logger.info(f"Found concept by name: {result[0]['c']['name']}")
            return ConceptNode.from_neo4j(result[0]['c'])
        
        logger.warning(f"Concept not found in knowledge graph: {concept_query}")
        return None
    
    async def get_prerequisites(self, concept_id: str, max_depth: Optional[int] = None) -> List[ConceptNode]:
        
        depth = max_depth or self._max_depth
        logger.info(f"Traversing prerequisites for {concept_id} with max depth {depth}")
        
        result = await self._client.execute_query(
            queries.GET_PREREQUISITES,
            {
                "concept_id": concept_id,
                "max_depth": depth
            }
        )
        
        prerequisites = [
            ConceptNode.from_neo4j(record['prereq']) 
            for record in result
        ]
        
        logger.info(f"Found {len(prerequisites)} prerequisite concepts")
        return prerequisites
    
    async def build_dependency_chain(self, concept_id: str) -> DependencyChain:
    
        target_result = await self._client.execute_query(
            queries.GET_CONCEPT_BY_ID,
            {"concept_id": concept_id}
        )
        
        if not target_result:
            raise ValueError(f"Concept not found: {concept_id}")
        
        target = ConceptNode.from_neo4j(target_result[0]['c'])
        
        prerequisites = await self.get_prerequisites(concept_id)
        
        depth_result = await self._client.execute_query(
            queries.GET_DEPENDENCY_CHAIN,
            {"concept_id": concept_id}
        )
        
        max_depth = 0
        if depth_result:
            depths = [r['depth'] for r in depth_result]
            max_depth = max(depths) if depths else 0
        
        return DependencyChain(
            target_concept=target,
            prerequisites=prerequisites,
            chain_depth=max_depth,
            is_complete=True,  # Complete traversal
            missing_concepts=[]
        )
    
    async def get_user_mastery_state(self, student_id: str) -> Dict[str, float]:
    
        result = await self._client.execute_query(
            queries.GET_STUDENT_MASTERY,
            {"student_id": student_id}
        )
        
        mastery_state = {
            record['concept_id']: record['mastery_level']
            for record in result
        }
        
        logger.info(f"Retrieved mastery state for {len(mastery_state)} concepts")
        return mastery_state
    
    async def find_knowledge_gaps(self,student_id: str,concept_id: str,threshold: Optional[float] = None) -> List[ConceptNode]:

        mastery_threshold = threshold or settings.MIN_MASTERY_THRESHOLD
        
        result = await self._client.execute_query(
            queries.FIND_KNOWLEDGE_GAPS,
            {
                "student_id": student_id,
                "concept_id": concept_id,
                "threshold": mastery_threshold
            }
        )
        
        gaps = [
            ConceptNode.from_neo4j(record['gap_concept'])
            for record in result
        ]
        
        logger.info(f"Found {len(gaps)} knowledge gaps for {concept_id}")
        return gaps
    
    async def calculate_readiness(self,student_id: str,concept_id: str,threshold: Optional[float] = None) -> float:
        
        mastery_threshold = threshold or settings.MIN_MASTERY_THRESHOLD
        
        result = await self._client.execute_query(
            queries.CALCULATE_READINESS_SCORE,
            {
                "student_id": student_id,
                "concept_id": concept_id,
                "threshold": mastery_threshold
            }
        )
        
        if result:
            return result[0].get('readiness_score', 0.0)
        return 0.0
    
    async def traverse(
        self,
        concept_query: str,
        student_id: str
    ) -> TraversalContext:
    
        logger.info(f"Starting KAG traversal for: {concept_query}")
        
        context = TraversalContext(result=TraversalResult.FAILED)
        
        target_concept = await self.resolve_concept(concept_query)
        if not target_concept:
            context.result = TraversalResult.CONCEPT_NOT_FOUND
            context.error_message = (
                f"Unable to locate concept '{concept_query}' in knowledge graph. "
                "System cannot proceed with reasoning. Please verify the concept name "
                "or check if it exists in your curriculum."
            )
            return context
        
        context.target_concept = target_concept
        context.reasoning_path.append(f"Resolved: {target_concept.name}")
        
        try:
            dependency_chain = await self.build_dependency_chain(target_concept.id)
            context.dependency_chain = dependency_chain
            context.reasoning_path.append(
                f"Dependency chain: {len(dependency_chain.prerequisites)} prerequisites"
            )
        except Exception as e:
            context.error_message = f"Failed to build dependency chain: {str(e)}"
            return context
        
        user_mastery = await self.get_user_mastery_state(student_id)
        context.user_mastery_state = user_mastery
        context.reasoning_path.append(
            f"User mastery: {len(user_mastery)} concepts known"
        )
        

        knowledge_gaps = await self.find_knowledge_gaps(student_id, target_concept.id)
        context.knowledge_gaps = knowledge_gaps
        context.reasoning_path.append(
            f"Knowledge gaps: {len(knowledge_gaps)} missing prerequisites"
        )
        
        readiness = await self.calculate_readiness(student_id, target_concept.id)
        
        if len(knowledge_gaps) == 0:
            context.result = TraversalResult.SUCCESS
            context.confidence_score = 1.0
        elif readiness >= settings.GAP_SIGNIFICANCE_THRESHOLD:
            context.result = TraversalResult.PARTIAL
            context.confidence_score = readiness
        else:
            context.result = TraversalResult.PARTIAL
            context.confidence_score = readiness
        
        logger.info(
            f"Traversal complete: {context.result.value}, "
            f"confidence={context.confidence_score:.2f}"
        )
        
        return context
