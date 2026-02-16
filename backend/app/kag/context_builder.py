from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

from app.kag.traversal_engine import TraversalContext, TraversalResult, ConceptNode
from app.kag.gap_analyzer import GapAnalysisResult, GapPriority, GapType
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ReasoningContext:
    target_concept: Dict[str, Any]
    dependency_chain: List[Dict[str, Any]]
    user_knowledge_state: Dict[str, Any]
    knowledge_gaps: List[Dict[str, Any]]
    readiness_score: float
    can_proceed: bool
    confidence_level: str
    response_type: str
    guidance_instructions: List[str]
    constraints: List[str] = field(default_factory=list)


class ContextBuilder:
    
    def __init__(self):
        self._min_threshold = settings.MIN_MASTERY_THRESHOLD
    
    def _concept_to_dict(self, concept: ConceptNode) -> Dict[str, Any]:
        return {
            "id": concept.id,
            "name": concept.name,
            "description": concept.description,
            "domain": concept.domain,
            "grade_level": concept.grade_level,
            "difficulty": concept.difficulty,
            "keywords": concept.keywords
        }
    
    def _determine_response_type(
        self,
        traversal: TraversalContext,
        gap_analysis: Optional[GapAnalysisResult]
    ) -> str:
        if traversal.result == TraversalResult.CONCEPT_NOT_FOUND:
            return "refuse"
        
        if gap_analysis is None:
            return "refuse"
        
        if gap_analysis.can_proceed:
            return "explain"
        
        critical_count = len(gap_analysis.critical_gaps)
        if critical_count > 0:
            return "bridge_gaps"
        
        return "bridge_gaps"
    
    def _get_confidence_level(self, score: float) -> str:
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _build_constraints(self, response_type: str) -> List[str]:
        base_constraints = [
            "You MUST ONLY use the information provided in this context.",
            "You CANNOT add, invent, or assume any knowledge not explicitly stated.",
            "You CANNOT bypass the reasoning chain - follow the dependencies.",
            "If information is missing, acknowledge the limitation - do not fabricate.",
            "Your role is VERBALIZATION ONLY - expressing structured reasoning in natural language.",
            "You must preserve the dependency order when explaining concepts.",
            "You must acknowledge knowledge gaps explicitly when they exist."
        ]
        
        type_specific = {
            "explain": [
                "Explain the target concept using the dependency chain provided.",
                "Reference prerequisite concepts in order of dependency.",
                "Use examples from the context only."
            ],
            "bridge_gaps": [
                "You MUST explain the knowledge gaps BEFORE the target concept.",
                "Start with the most critical gaps identified.",
                "Provide a learning path based on the gap analysis.",
                "Do not explain the target concept until gaps are addressed."
            ],
            "refuse": [
                "You MUST refuse to provide an explanation.",
                "State clearly that the concept was not found in the knowledge graph.",
                "Suggest the user verify the concept name or check their curriculum.",
                "Do NOT attempt to explain using external knowledge."
            ]
        }
        
        return base_constraints + type_specific.get(response_type, [])
    
    def _build_guidance(
        self,
        response_type: str,
        traversal: TraversalContext,
        gap_analysis: Optional[GapAnalysisResult]
    ) -> List[str]:
        guidance = []
        
        if response_type == "explain":
            guidance.extend([
                f"Begin by briefly establishing the prerequisite knowledge.",
                f"Then explain the target concept: {traversal.target_concept.name}",
                f"Connect the prerequisites to the target concept explicitly.",
                f"Use analogies that build on concepts the user already knows."
            ])
            
            if traversal.dependency_chain:
                prereq_names = [c.name for c in traversal.dependency_chain.prerequisites[:3]]
                if prereq_names:
                    guidance.append(
                        f"Key prerequisites to reference: {', '.join(prereq_names)}"
                    )
        
        elif response_type == "bridge_gaps" and gap_analysis:
            guidance.extend([
                f"The user wants to learn: {traversal.target_concept.name}",
                f"However, they have {gap_analysis.total_gaps} knowledge gap(s).",
                f"You must address these gaps before explaining the target.",
                "Structure your response as a learning path."
            ])
            
            for gap in gap_analysis.critical_gaps[:3]:
                guidance.append(
                    f"CRITICAL GAP: {gap.concept.name} - {gap.recommended_action}"
                )
            
            guidance.append(
                f"User readiness score: {gap_analysis.readiness_score:.0%}. "
                f"Estimated time to ready: {gap_analysis.estimated_time_to_ready} minutes."
            )
        
        elif response_type == "refuse":
            guidance.extend([
                "State that the concept could not be found in the knowledge graph.",
                "This is NOT an error - it's the correct behavior for unknown concepts.",
                f"Original query was: '{traversal.error_message}'",
                "Suggest the user check spelling or verify the concept exists in their curriculum."
            ])
        
        return guidance
    
    def _build_user_knowledge_state(
        self,
        traversal: TraversalContext,
        gap_analysis: Optional[GapAnalysisResult]
    ) -> Dict[str, Any]:
        mastered = []
        struggling = []
        
        for concept_id, mastery in traversal.user_mastery_state.items():
            if mastery >= self._min_threshold:
                mastered.append({"concept_id": concept_id, "mastery": mastery})
            else:
                struggling.append({"concept_id": concept_id, "mastery": mastery})
        
        state = {
            "mastered_concepts_count": len(mastered),
            "struggling_concepts_count": len(struggling),
            "total_known_concepts": len(traversal.user_mastery_state),
            "readiness_score": traversal.confidence_score
        }
        
        if gap_analysis:
            state["gaps_identified"] = gap_analysis.total_gaps
            state["critical_gaps_count"] = len(gap_analysis.critical_gaps)
            state["can_proceed"] = gap_analysis.can_proceed
        
        return state
    
    def _build_gap_context(
        self,
        gap_analysis: Optional[GapAnalysisResult]
    ) -> List[Dict[str, Any]]:
        if not gap_analysis:
            return []
        
        gaps = []
        
        for gap in gap_analysis.critical_gaps + gap_analysis.secondary_gaps:
            gap_info = {
                "concept_name": gap.concept.name,
                "concept_id": gap.concept.id,
                "priority": gap.priority.value,
                "type": gap.gap_type.value,
                "distance_to_target": gap.distance_to_target,
                "current_mastery": gap.current_mastery,
                "impact_score": gap.impact_score,
                "recommended_action": gap.recommended_action
            }
            
            if gap.related_struggles:
                gap_info["previous_errors"] = gap.related_struggles[:3]
            
            gaps.append(gap_info)
        
        return gaps
    
    def build_context(
        self,
        traversal: TraversalContext,
        gap_analysis: Optional[GapAnalysisResult]
    ) -> ReasoningContext:
        logger.info("Building reasoning context for LLM verbalization")
        
        response_type = self._determine_response_type(traversal, gap_analysis)
        
        target_context = {}
        if traversal.target_concept:
            target_context = self._concept_to_dict(traversal.target_concept)
        
        dependency_context = []
        if traversal.dependency_chain:
            dependency_context = [
                self._concept_to_dict(c) 
                for c in traversal.dependency_chain.prerequisites
            ]
        
        user_state = self._build_user_knowledge_state(traversal, gap_analysis)
        gap_context = self._build_gap_context(gap_analysis)
        confidence = self._get_confidence_level(traversal.confidence_score)
        constraints = self._build_constraints(response_type)
        guidance = self._build_guidance(response_type, traversal, gap_analysis)
        
        can_proceed = False
        if gap_analysis:
            can_proceed = gap_analysis.can_proceed
        
        context = ReasoningContext(
            target_concept=target_context,
            dependency_chain=dependency_context,
            user_knowledge_state=user_state,
            knowledge_gaps=gap_context,
            readiness_score=traversal.confidence_score,
            can_proceed=can_proceed,
            confidence_level=confidence,
            response_type=response_type,
            guidance_instructions=guidance,
            constraints=constraints
        )
        
        logger.info(f"Context built: response_type={response_type}, "
                   f"gaps={len(gap_context)}, confidence={confidence}")
        
        return context
    
    def format_for_llm(self, context: ReasoningContext) -> str:
        prompt_parts = [
            "# KAG REASONING CONTEXT",
            "",
            "You are a KAG (Knowledge Augmented Generation) verbalization engine.",
            "Your ONLY role is to express the following structured reasoning in natural language.",
            "You MUST NOT add, invent, or assume any knowledge not in this context.",
            "",
            "---",
            "",
            "## RESPONSE TYPE",
            f"`{context.response_type}`",
            ""
        ]
        
        if context.target_concept:
            prompt_parts.extend([
                "## TARGET CONCEPT",
                f"Name: {context.target_concept.get('name', 'N/A')}",
                f"Domain: {context.target_concept.get('domain', 'N/A')}",
                f"Grade Level: {context.target_concept.get('grade_level', 'N/A')}",
                f"Description: {context.target_concept.get('description', 'N/A')}",
                ""
            ])
        
        if context.dependency_chain:
            prompt_parts.extend([
                "## DEPENDENCY CHAIN",
                "(Prerequisites in order - must be referenced in explanation)",
                ""
            ])
            for i, dep in enumerate(context.dependency_chain, 1):
                prompt_parts.append(
                    f"{i}. {dep.get('name', 'Unknown')} "
                    f"[{dep.get('domain', 'General')}]"
                )
            prompt_parts.append("")
        
        prompt_parts.extend([
            "## USER KNOWLEDGE STATE",
            f"Known concepts: {context.user_knowledge_state.get('total_known_concepts', 0)}",
            f"Readiness score: {context.readiness_score:.0%}",
            f"Can proceed: {context.can_proceed}",
            ""
        ])
        
        if context.knowledge_gaps:
            prompt_parts.extend([
                "## KNOWLEDGE GAPS",
                "(Must be addressed before target concept)",
                ""
            ])
            for gap in context.knowledge_gaps:
                prompt_parts.extend([
                    f"### {gap['concept_name']} [{gap['priority'].upper()}]",
                    f"- Type: {gap['type']}",
                    f"- Current mastery: {gap['current_mastery']:.0%}",
                    f"- Distance to target: {gap['distance_to_target']}",
                    f"- Action: {gap['recommended_action']}",
                    ""
                ])
        
        prompt_parts.extend([
            "## VERBALIZATION GUIDANCE",
            ""
        ])
        for instruction in context.guidance_instructions:
            prompt_parts.append(f"- {instruction}")
        prompt_parts.append("")
        
        prompt_parts.extend([
            "## STRICT CONSTRAINTS",
            ""
        ])
        for constraint in context.constraints:
            prompt_parts.append(f"- {constraint}")
        prompt_parts.append("")
        
        prompt_parts.extend([
            "---",
            "",
            "Based on the above context, provide your verbalization:",
            ""
        ])
        
        return "\n".join(prompt_parts)
