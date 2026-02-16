from typing import Dict, Any, List


class CypherQueries:
    
    CREATE_CONCEPT = """
    MERGE (c:Concept {id: $id})
    SET c.name = $name,
        c.description = $description,
        c.domain = $domain,
        c.grade_level = $grade_level,
        c.difficulty = $difficulty,
        c.keywords = $keywords,
        c.curriculum_code = $curriculum_code,
        c.estimated_time_minutes = $estimated_time_minutes,
        c.created_at = datetime(),
        c.updated_at = datetime()
    RETURN c
    """
    
    GET_CONCEPT_BY_ID = """
    MATCH (c:Concept {id: $concept_id})
    RETURN c
    """
    
    GET_CONCEPT_BY_NAME = """
    MATCH (c:Concept)
    WHERE toLower(c.name) CONTAINS toLower($name)
    RETURN c
    LIMIT 10
    """
    
    GET_CONCEPTS_BY_DOMAIN = """
    MATCH (c:Concept)
    WHERE c.domain = $domain AND c.grade_level = $grade_level
    RETURN c
    ORDER BY c.difficulty
    """
    
    GET_ALL_DOMAINS = """
    MATCH (c:Concept)
    RETURN DISTINCT c.domain AS domain, c.grade_level AS grade_level
    ORDER BY domain, grade_level
    """
    
    CREATE_REQUIRES_RELATION = """
    MATCH (source:Concept {id: $source_id})
    MATCH (target:Concept {id: $target_id})
    MERGE (source)-[r:REQUIRES]->(target)
    SET r.strength = $strength,
        r.created_at = datetime()
    RETURN r
    """
    
    CREATE_BUILDS_ON_RELATION = """
    MATCH (source:Concept {id: $source_id})
    MATCH (target:Concept {id: $target_id})
    MERGE (source)-[r:BUILDS_ON]->(target)
    SET r.created_at = datetime()
    RETURN r
    """
    
    CREATE_HAS_EXAMPLE_RELATION = """
    MATCH (concept:Concept {id: $concept_id})
    MERGE (example:Example {id: $example_id})
    SET example.content = $content,
        example.difficulty_level = $difficulty_level
    MERGE (concept)-[r:HAS_EXAMPLE]->(example)
    RETURN example
    """
    
    CREATE_FORMULA_RELATION = """
    MATCH (concept:Concept {id: $concept_id})
    MERGE (formula:Formula {id: $formula_id})
    SET formula.expression = $expression,
        formula.explanation = $explanation,
        formula.variables = $variables
    MERGE (concept)-[r:HAS_FORMULA]->(formula)
    RETURN formula
    """
    
    GET_PREREQUISITES = """
    MATCH (c:Concept {id: $concept_id})-[:REQUIRES*1..{max_depth}]->(prereq:Concept)
    RETURN DISTINCT prereq
    ORDER BY prereq.difficulty
    """
    
    GET_DEPENDENCY_CHAIN = """
    MATCH path = (c:Concept {id: $concept_id})-[:REQUIRES*]->(prereq:Concept)
    RETURN 
        [node in nodes(path) | node.id] AS concept_ids,
        [node in nodes(path) | node.name] AS concept_names,
        length(path) AS depth
    ORDER BY depth
    """
    
    GET_ALL_PREREQUISITES_TRANSITIVE = """
    MATCH (c:Concept {id: $concept_id})
    CALL apoc.transitive.closure(c, 'REQUIRES') YIELD node
    RETURN node AS prerequisite
    """
    
    GET_CONCEPTS_THAT_REQUIRE = """
    MATCH (c:Concept)-[:REQUIRES]->(prereq:Concept {id: $concept_id})
    RETURN c
    """
    
    GET_LEARNING_PATH = """
    MATCH (start:Concept {id: $start_id}), (end:Concept {id: $end_id})
    MATCH path = shortestPath((start)-[:REQUIRES|BUILDS_ON*]->(end))
    RETURN [node in nodes(path) | {id: node.id, name: node.name}] AS learning_path
    """
    
    CREATE_STUDENT = """
    MERGE (s:Student {id: $student_id})
    SET s.name = $name,
        s.grade_level = $grade_level,
        s.learning_style = $learning_style,
        s.created_at = coalesce(s.created_at, datetime()),
        s.updated_at = datetime()
    RETURN s
    """
    
    GET_STUDENT = """
    MATCH (s:Student {id: $student_id})
    RETURN s
    """
    
    UPDATE_MASTERY = """
    MATCH (s:Student {id: $student_id})
    MATCH (c:Concept {id: $concept_id})
    MERGE (s)-[r:MASTERS]->(c)
    SET r.mastery_level = $mastery_level,
        r.confidence = $confidence,
        r.assessed_at = datetime(),
        r.assessment_count = coalesce(r.assessment_count, 0) + 1
    RETURN r
    """
    
    RECORD_STRUGGLE = """
    MATCH (s:Student {id: $student_id})
    MATCH (c:Concept {id: $concept_id})
    MERGE (s)-[r:STRUGGLES_WITH]->(c)
    SET r.struggle_count = coalesce(r.struggle_count, 0) + 1,
        r.last_struggled = datetime(),
        r.error_patterns = coalesce(r.error_patterns, []) + $error_pattern
    RETURN r
    """
    
    GET_STUDENT_MASTERY = """
    MATCH (s:Student {id: $student_id})-[r:MASTERS]->(c:Concept)
    RETURN c.id AS concept_id, c.name AS concept_name, 
           r.mastery_level AS mastery_level, r.confidence AS confidence
    ORDER BY r.mastery_level DESC
    """
    
    GET_STUDENT_STRUGGLES = """
    MATCH (s:Student {id: $student_id})-[r:STRUGGLES_WITH]->(c:Concept)
    RETURN c.id AS concept_id, c.name AS concept_name,
           r.struggle_count AS struggle_count, r.error_patterns AS error_patterns
    ORDER BY r.struggle_count DESC
    """
    
    GET_STUDENT_KNOWLEDGE_STATE = """
    MATCH (s:Student {id: $student_id})
    OPTIONAL MATCH (s)-[m:MASTERS]->(mastered:Concept)
    OPTIONAL MATCH (s)-[st:STRUGGLES_WITH]->(struggled:Concept)
    RETURN 
        s AS student,
        collect(DISTINCT {concept: mastered, mastery: m}) AS mastered_concepts,
        collect(DISTINCT {concept: struggled, struggle: st}) AS struggled_concepts
    """
    
    FIND_KNOWLEDGE_GAPS = """
    MATCH (s:Student {id: $student_id})
    MATCH (target:Concept {id: $concept_id})
    MATCH (target)-[:REQUIRES*]->(prereq:Concept)
    WHERE NOT EXISTS {
        MATCH (s)-[m:MASTERS]->(prereq)
        WHERE m.mastery_level >= $threshold
    }
    RETURN prereq AS gap_concept
    ORDER BY prereq.difficulty
    """
    
    GET_CRITICAL_GAPS = """
    MATCH (s:Student {id: $student_id})
    MATCH (target:Concept {id: $concept_id})
    MATCH path = (target)-[:REQUIRES*]->(prereq:Concept)
    WHERE NOT EXISTS {
        MATCH (s)-[m:MASTERS]->(prereq)
        WHERE m.mastery_level >= $threshold
    }
    WITH prereq, length(path) AS distance
    ORDER BY distance DESC
    RETURN prereq, distance
    LIMIT 5
    """
    
    CALCULATE_READINESS_SCORE = """
    MATCH (s:Student {id: $student_id})
    MATCH (target:Concept {id: $concept_id})
    OPTIONAL MATCH (target)-[:REQUIRES]->(prereq:Concept)
    WITH target, collect(prereq) AS prerequisites
    OPTIONAL MATCH (s:Student {id: $student_id})-[m:MASTERS]->(prereq:Concept)
    WHERE prereq IN prerequisites AND m.mastery_level >= $threshold
    WITH count(prereq) AS mastered_prereqs, size(prerequisites) AS total_prereqs
    RETURN CASE 
        WHEN total_prereqs = 0 THEN 1.0 
        ELSE toFloat(mastered_prereqs) / toFloat(total_prereqs) 
    END AS readiness_score
    """
    
    GET_CONCEPT_DIFFICULTY_STATS = """
    MATCH (s:Student)-[m:MASTERS]->(c:Concept)
    WITH c, avg(m.mastery_level) AS avg_mastery, count(s) AS student_count
    RETURN c.id AS concept_id, c.name AS concept_name, 
           avg_mastery, student_count,
           1 - avg_mastery AS difficulty_score
    ORDER BY difficulty_score DESC
    """
    
    GET_COMMON_STRUGGLE_PATTERNS = """
    MATCH (s:Student)-[r:STRUGGLES_WITH]->(c:Concept)
    WITH c, count(s) AS struggle_count, 
         collect(DISTINCT r.error_patterns) AS all_patterns
    RETURN c.id AS concept_id, c.name AS concept_name,
           struggle_count, all_patterns
    ORDER BY struggle_count DESC
    LIMIT 20
    """
    
    GET_LEARNING_PROGRESS = """
    MATCH (s:Student {id: $student_id})
    MATCH (c:Concept)
    WHERE c.domain = $domain AND c.grade_level <= $grade_level
    WITH count(c) AS total_concepts
    OPTIONAL MATCH (s:Student {id: $student_id})-[m:MASTERS]->(mastered:Concept)
    WHERE mastered.domain = $domain AND mastered.grade_level <= $grade_level
    WITH total_concepts, count(mastered) AS mastered_count
    RETURN total_concepts, mastered_count,
           CASE WHEN total_concepts > 0 
                THEN toFloat(mastered_count) / toFloat(total_concepts)
                ELSE 0 END AS progress_percentage
    """
    
    GET_RECOMMENDED_NEXT_CONCEPTS = """
    MATCH (s:Student {id: $student_id})
    MATCH (potential:Concept)
    WHERE NOT EXISTS {(s)-[:MASTERS]->(potential)}
    AND NOT EXISTS {(s)-[:STRUGGLES_WITH]->(potential)}
    WITH potential, s
    OPTIONAL MATCH (potential)-[:REQUIRES]->(prereq:Concept)
    WITH potential, collect(prereq) AS prerequisites, s
    WHERE ALL(p IN prerequisites WHERE EXISTS {
        MATCH (s)-[m:MASTERS]->(p)
        WHERE m.mastery_level >= $threshold
    })
    RETURN potential
    ORDER BY potential.difficulty
    LIMIT 10
    """
    
    GET_DOMAIN_TAXONOMY = """
    MATCH (c:Concept)
    WITH c.domain AS domain, c.grade_level AS grade, collect(c) AS concepts
    RETURN domain, grade, 
           [c IN concepts | {id: c.id, name: c.name, difficulty: c.difficulty}] AS concept_list
    ORDER BY domain, grade
    """
    
    GET_CURRICULUM_STRUCTURE = """
    MATCH (c:Concept)
    WHERE c.curriculum_code STARTS WITH $curriculum_prefix
    RETURN c.curriculum_code AS code, c.name AS name, 
           c.domain AS domain, c.grade_level AS grade
    ORDER BY c.curriculum_code
    """


queries = CypherQueries()
