import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.graph.neo4j_client import Neo4jClient
from app.graph.cypher_queries import queries
from app.data.curriculum_dataset import get_all_concepts, get_all_relationships


async def create_constraints_and_indexes(client: Neo4jClient):
    print("Creating constraints and indexes...")
    await client.create_constraint("Concept", "id")
    await client.create_index("Concept", "name")
    await client.create_index("Concept", "domain")
    await client.create_index("Concept", "grade_level")
    await client.create_constraint("Student", "id")
    await client.create_constraint("Example", "id")
    await client.create_constraint("Formula", "id")
    print("Constraints and indexes created.")


async def ingest_concepts(client: Neo4jClient):
    concepts = get_all_concepts()
    print(f"Ingesting {len(concepts)} concepts...")
    for i, concept in enumerate(concepts):
        try:
            await client.execute_query(
                queries.CREATE_CONCEPT,
                {
                    "id": concept["id"],
                    "name": concept["name"],
                    "description": concept.get("description", ""),
                    "domain": concept.get("domain", "General"),
                    "grade_level": concept.get("grade_level", 1),
                    "difficulty": concept.get("difficulty", 0.5),
                    "keywords": concept.get("keywords", []),
                    "curriculum_code": concept.get("curriculum_code", ""),
                    "estimated_time_minutes": concept.get("estimated_time_minutes", 60)
                }
            )
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(concepts)} concepts")
        except Exception as e:
            print(f"  Error ingesting concept {concept['id']}: {e}")
    print(f"Successfully ingested {len(concepts)} concepts.")


async def ingest_relationships(client: Neo4jClient):
    relationships = get_all_relationships()
    print(f"Ingesting {len(relationships)} relationships...")
    for i, rel in enumerate(relationships):
        try:
            if rel["relationship_type"] == "REQUIRES":
                await client.execute_query(
                    queries.CREATE_REQUIRES_RELATION,
                    {
                        "source_id": rel["source_id"],
                        "target_id": rel["target_id"],
                        "strength": rel.get("strength", 1.0)
                    }
                )
            elif rel["relationship_type"] == "BUILDS_ON":
                await client.execute_query(
                    queries.CREATE_BUILDS_ON_RELATION,
                    {
                        "source_id": rel["source_id"],
                        "target_id": rel["target_id"]
                    }
                )
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/{len(relationships)} relationships")
        except Exception as e:
            print(f"  Error ingesting relationship {rel['source_id']} -> {rel['target_id']}: {e}")
    print(f"Successfully ingested {len(relationships)} relationships.")


async def create_sample_students(client: Neo4jClient):
    print("Creating sample students...")
    sample_students = [
        {"student_id": "student_001", "name": "Alice Johnson", "grade_level": 7, "learning_style": "visual"},
        {"student_id": "student_002", "name": "Bob Smith", "grade_level": 5, "learning_style": "kinesthetic"},
        {"student_id": "student_003", "name": "Carol Davis", "grade_level": 9, "learning_style": "auditory"},
        {"student_id": "student_004", "name": "David Wilson", "grade_level": 3, "learning_style": "reading"},
        {"student_id": "student_005", "name": "Eva Martinez", "grade_level": 11, "learning_style": "multimodal"},
    ]
    for student in sample_students:
        try:
            await client.execute_query(queries.CREATE_STUDENT, student)
            print(f"  Created student: {student['name']}")
        except Exception as e:
            print(f"  Error creating student {student['student_id']}: {e}")
    print("Sample students created.")


async def verify_ingestion(client: Neo4jClient):
    print("\nVerifying ingestion...")
    concept_result = await client.execute_query("MATCH (c:Concept) RETURN count(c) AS count")
    concept_count = concept_result[0]["count"] if concept_result else 0
    rel_result = await client.execute_query("MATCH ()-[r:REQUIRES]->() RETURN count(r) AS count")
    requires_count = rel_result[0]["count"] if rel_result else 0
    rel_result = await client.execute_query("MATCH ()-[r:BUILDS_ON]->() RETURN count(r) AS count")
    builds_on_count = rel_result[0]["count"] if rel_result else 0
    student_result = await client.execute_query("MATCH (s:Student) RETURN count(s) AS count")
    student_count = student_result[0]["count"] if student_result else 0

    print(f"\nIngestion Summary:")
    print(f"  - Concepts: {concept_count}")
    print(f"  - REQUIRES relationships: {requires_count}")
    print(f"  - BUILDS_ON relationships: {builds_on_count}")
    print(f"  - Sample students: {student_count}")

    print("\nTesting sample query...")
    test_result = await client.execute_query("""
        MATCH (c:Concept {id: 'math_g8_linear_equations'})-[:REQUIRES]->(prereq:Concept)
        RETURN c.name AS concept, collect(prereq.name) AS prerequisites
    """)
    if test_result:
        print(f"  Concept: {test_result[0]['concept']}")
        print(f"  Prerequisites: {test_result[0]['prerequisites']}")


async def main():
    print("=" * 60)
    print("KAG Platform - Data Ingestion Script")
    print("=" * 60)

    client = Neo4jClient()
    try:
        print("\nConnecting to Neo4j...")
        await client.connect()
        print("Connected successfully.")

        print("\nClearing existing data...")
        await client.clear_database()
        print("Database cleared.")

        await create_constraints_and_indexes(client)
        await ingest_concepts(client)
        await ingest_relationships(client)
        await create_sample_students(client)
        await verify_ingestion(client)

        print("\n" + "=" * 60)
        print("Data ingestion completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
