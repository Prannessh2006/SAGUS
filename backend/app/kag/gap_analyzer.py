from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from app.graph.neo4j_client import Neo4jClient
from app.graph.cypher_queries import queries
from app.kag.traversal_engine import ConceptNode, TraversalContext, TraversalResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class GapPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapType(Enum):
    MISSING_PREREQUISITE = "missing_prerequisite"
    FORGOTTEN = "forgotten"
    WEAK_UNDERSTANDING = "weak_understanding"
    MISCONCEPTION = "misconception"


@dataclass
class KnowledgeGap:
    concept: ConceptNode
    priority: GapPriority
    gap_type: GapType
    distance_to_target: int
    current_mastery: float
    impact_score: float
    recommended_action: str
    related_struggles: List[str] = field(default_factory=list)


@dataclass
class GapAnalysisResult:
    target_concept: ConceptNode
    total_gaps: int
    critical_gaps: List[KnowledgeGap]
    secondary_gaps: List[KnowledgeGap]
    readiness_score: float
    can_proceed: bool
    recommended_learning_path: List[str]
    estimated_time_to_ready: int
    analysis_confidence: float


class GapAnalyzer:
    
    def __init__(self, neo4j_client: Neo4jClient):
        self._client = neo4j_client
        self._mastery_threshold = settings.MIN_MASTERY_THRESHOLD
    
    def classify_gap_type(self,mastery_level: Optional[float],has_struggle_record: bool) -> GapType:
        if mastery_level is None:
            return GapType.MISSING_PREREQUISITE
        elif has_struggle_record:
            return GapType.MISCONCEPTION
        elif mastery_level < 0.3:
            return GapType.WEAK_UNDERSTANDING
        else:
            return GapType.FORGOTTEN
    
    def calculate_priority(self,gap_type: GapType,distance_to_target: int,current_mastery: Optional[float]) -> GapPriority:
        if distance_to_target == 1:
            distance_priority = 3
        elif distance_to_target <= 3:
            distance_priority = 2
        else:
            distance_priority = 1
        
        type_priority = {
            GapType.MISCONCEPTION: 4,
            GapType.MISSING_PREREQUISITE: 3,
            GapType.WEAK_UNDERSTANDING: 2,
            GapType.FORGOTTEN: 1
        }.get(gap_type, 1)
        
        if current_mastery is None:
            mastery_factor = 3
        elif current_mastery < 0.3:
            mastery_factor = 2
        else:
            mastery_factor = 1
        
        total_score = distance_priority + type_priority + mastery_factor
        
        if total_score >= 8:
            return GapPriority.CRITICAL
        elif total_score >= 6:
            return GapPriority.HIGH
        elif total_score >= 4:
            return GapPriority.MEDIUM
        else:
            return GapPriority.LOW
    
    def generate_recommendation(self,gap: KnowledgeGap) -> str:
        
        concept_name = gap.concept.name
        
        recommendations = {
            GapType.MISSING_PREREQUISITE: {
                GapPriority.CRITICAL: f"CRITICAL: Learn '{concept_name}' first - it is a direct prerequisite for the target concept. This must be addressed before proceeding.",
                GapPriority.HIGH: f"HIGH: Study '{concept_name}' before continuing. This foundational concept is essential for understanding the target.",
                GapPriority.MEDIUM: f"Study '{concept_name}' to build a stronger foundation for the target concept.",
                GapPriority.LOW: f"Consider reviewing '{concept_name}' for better understanding."
            },
            GapType.MISCONCEPTION: {
                GapPriority.CRITICAL: f"CRITICAL: Address misconceptions in '{concept_name}'. Previous errors indicate fundamental misunderstanding that will block progress.",
                GapPriority.HIGH: f"HIGH: Review '{concept_name}' carefully. Your previous struggles suggest a misconception that needs correction.",
                GapPriority.MEDIUM: f"Review '{concept_name}' with focus on correcting previous errors.",
                GapPriority.LOW: f"Light review of '{concept_name}' may help clarify any remaining confusion."
            },
            GapType.WEAK_UNDERSTANDING: {
                GapPriority.CRITICAL: f"CRITICAL: Your understanding of '{concept_name}' is very weak. This concept must be strengthened before proceeding.",
                GapPriority.HIGH: f"HIGH: Reinforce your understanding of '{concept_name}'. Practice more exercises on this topic.",
                GapPriority.MEDIUM: f"Practice more problems involving '{concept_name}' to strengthen your understanding.",
                GapPriority.LOW: f"Additional practice on '{concept_name}' would be beneficial."
            },
            GapType.FORGOTTEN: {
                GapPriority.CRITICAL: f"CRITICAL: You've forgotten '{concept_name}' which is essential. Immediate review required.",
                GapPriority.HIGH: f"HIGH: Refresh your knowledge of '{concept_name}' - you've studied this before but mastery has decreased.",
                GapPriority.MEDIUM: f"Review '{concept_name}' to refresh your previous learning.",
                GapPriority.LOW: f"A quick review of '{concept_name}' may be helpful."
            }
        }
        
        return recommendations.get(gap.gap_type, {}).get(gap.priority, f"Review '{concept_name}'")
    
    async def get_user_struggles(self,student_id: str) -> Dict[str, List[str]]:
        result = await self._client.execute_query(
            queries.GET_STUDENT_STRUGGLES,
            {"student_id": student_id}
        )
        
        struggles = {}
        for record in result:
            concept_id = record['concept_id']
            error_patterns = record.get('error_patterns', [])
            struggles[concept_id] = error_patterns
        
        return struggles
    
    async def analyze_gaps(self,traversal_context: TraversalContext,student_id: str) -> GapAnalysisResult:
        if traversal_context.result == TraversalResult.CONCEPT_NOT_FOUND:
            raise ValueError("Cannot analyze gaps: concept not found in knowledge graph")
        
        target = traversal_context.target_concept
        gaps = traversal_context.knowledge_gaps
        mastery_state = traversal_context.user_mastery_state
        
        struggles = await self.get_user_struggles(student_id)
        
        critical_result = await self._client.execute_query(
            queries.GET_CRITICAL_GAPS,
            {
                "student_id": student_id,
                "concept_id": target.id,
                "threshold": self._mastery_threshold
            }
        )
        
        distance_map = {}
        for record in critical_result:
            prereq_id = record['prereq'].get('id')
            distance = record['distance']
            if prereq_id:
                distance_map[prereq_id] = distance
        
        analyzed_gaps: List[KnowledgeGap] = []
        
        for gap_concept in gaps:
            gap_id = gap_concept.id
            current_mastery = mastery_state.get(gap_id)
            has_struggle = gap_id in struggles
            distance = distance_map.get(gap_id, 99)
            
            gap_type = self.classify_gap_type(current_mastery, has_struggle)
            priority = self.calculate_priority(gap_type, distance, current_mastery)
            
            impact = self._calculate_impact_score(
                priority, 
                gap_type, 
                distance, 
                current_mastery
            )
            
            gap = KnowledgeGap(
                concept=gap_concept,
                priority=priority,
                gap_type=gap_type,
                distance_to_target=distance,
                current_mastery=current_mastery or 0.0,
                impact_score=impact,
                recommended_action="",
                related_struggles=struggles.get(gap_id, [])
            )
            
            gap.recommended_action = self.generate_recommendation(gap)
            analyzed_gaps.append(gap)
        
        priority_order = {
            GapPriority.CRITICAL: 0,
            GapPriority.HIGH: 1,
            GapPriority.MEDIUM: 2,
            GapPriority.LOW: 3
        }
        
        analyzed_gaps.sort(
            key=lambda g: (priority_order[g.priority], -g.impact_score)
        )
        
        critical_gaps = [g for g in analyzed_gaps if g.priority in 
                        (GapPriority.CRITICAL, GapPriority.HIGH)]
        secondary_gaps = [g for g in analyzed_gaps if g.priority in 
                         (GapPriority.MEDIUM, GapPriority.LOW)]
        
        readiness = traversal_context.confidence_score
        can_proceed = len(critical_gaps) == 0 and readiness >= 0.5
        
        learning_path = self._build_learning_path(analyzed_gaps)
        estimated_time = self._estimate_time_to_ready(analyzed_gaps)
        
        return GapAnalysisResult(
            target_concept=target,
            total_gaps=len(analyzed_gaps),
            critical_gaps=critical_gaps,
            secondary_gaps=secondary_gaps,
            readiness_score=readiness,
            can_proceed=can_proceed,
            recommended_learning_path=learning_path,
            estimated_time_to_ready=estimated_time,
            analysis_confidence=self._calculate_analysis_confidence(analyzed_gaps)
        )
    
    def _calculate_impact_score(self,priority: GapPriority,gap_type: GapType,distance: int,current_mastery: Optional[float]) -> float:
        priority_score = {
            GapPriority.CRITICAL: 1.0,
            GapPriority.HIGH: 0.75,
            GapPriority.MEDIUM: 0.5,
            GapPriority.LOW: 0.25
        }.get(priority, 0.5)
        
        distance_factor = 1.0 / max(distance, 1)
        mastery_factor = 1.0 - (current_mastery or 0.0)
        
        return priority_score * 0.5 + distance_factor * 0.3 + mastery_factor * 0.2
    
    def _build_learning_path(self,gaps: List[KnowledgeGap]) -> List[str]:
        sorted_gaps = sorted(
            gaps,
            key=lambda g: (-g.distance_to_target, g.priority.value)
        )
        
        return [g.concept.name for g in sorted_gaps]
    
    def _estimate_time_to_ready(self,gaps: List[KnowledgeGap]) -> int:
        time_estimates = {
            GapType.MISSING_PREREQUISITE: 45,
            GapType.MISCONCEPTION: 30,
            GapType.WEAK_UNDERSTANDING: 25,
            GapType.FORGOTTEN: 15
        }
        
        total_time = sum(
            time_estimates.get(g.gap_type, 30) for g in gaps
        )
        
        return total_time
    
    def _calculate_analysis_confidence(self,gaps: List[KnowledgeGap]) -> float:
        if not gaps:
            return 1.0
        
        gaps_with_mastery = sum(1 for g in gaps if g.current_mastery > 0)
        gaps_with_struggles = sum(1 for g in g.related_struggles for g in gaps)
        
        confidence = 0.7
        
        if gaps_with_mastery > 0:
            confidence += 0.15
        
        if gaps_with_struggles > 0:
            confidence += 0.15
        
        return min(confidence, 1.0)
