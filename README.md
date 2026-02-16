# KAG Learning Platform

**Knowledge Augmented Generation (KAG)** - A personalized AI learning platform that combines Knowledge Graph reasoning with LLM verbalization for adaptive education.

## 🎯 What is KAG?

KAG is **NOT** a chatbot, RAG system, LMS, or fine-tuned model. It is a **deterministic reasoning engine**:

```
Knowledge Graph + User Cognition → Deterministic Reasoning → LLM Verbalization
```

### Core Principles

1. **Graph-Based Reasoning**: All knowledge comes from the Neo4j knowledge graph
2. **User State Mapping**: Student's cognitive state is tracked and mapped to concepts
3. **Dependency Traversal**: Prerequisites are traversed before any explanation
4. **Gap Detection**: System identifies what the student doesn't know
5. **LLM as Voice**: The LLM only verbalizes - it never supplies knowledge
6. **Graceful Refusal**: When reasoning fails, the system refuses to answer

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flutter Frontend                          │
│                    (MVVM Architecture)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  KAG Engine │  │ Groq Client │  │   PySpark Analytics     │ │
│  │  (Graph     │→ │ (Verbalize  │  │   (Offline Processing)  │ │
│  │   Reasoning)│  │  Only)      │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Neo4j Knowledge Graph                        │
│   ┌──────────┐    ┌──────────┐    ┌──────────────────────────┐ │
│   │ Concept  │───▶│ REQUIRES │───▶│  Student Cognitive State │ │
│   │  Nodes   │    │   Edges  │    │  (MASTERS/STRUGGLES_WITH)│ │
│   └──────────┘    └──────────┘    └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
kag-platform/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py              # Configuration management
│   │   ├── graph/
│   │   │   ├── neo4j_client.py        # Neo4j async client
│   │   │   └── cypher_queries.py      # All Cypher query templates
│   │   ├── kag/
│   │   │   ├── traversal_engine.py    # Graph traversal & reasoning
│   │   │   ├── gap_analyzer.py        # Knowledge gap analysis
│   │   │   └── context_builder.py     # LLM context preparation
│   │   ├── llm/
│   │   │   └── groq_client.py         # Groq API client
│   │   ├── analytics/
│   │   │   └── pyspark_jobs.py        # PySpark batch processing
│   │   ├── routers/
│   │   │   ├── student.py             # Student management API
│   │   │   ├── learning.py            # Core KAG learning API
│   │   │   └── assessment.py          # Assessment API
│   │   ├── schemas/
│   │   │   └── models.py              # Pydantic data models
│   │   ├── data/
│   │   │   └── curriculum_dataset.py  # Sample curriculum data
│   │   ├── scripts/
│   │   │   └── ingest_data.py         # Data ingestion script
│   │   └── main.py                    # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── flutter_app/
│   ├── lib/
│   │   ├── models/
│   │   │   └── kag_models.dart        # Data models
│   │   ├── viewmodels/
│   │   │   ├── user_viewmodel.dart    # User state management
│   │   │   └── chat_viewmodel.dart    # Chat state management
│   │   ├── views/
│   │   │   ├── home_view.dart         # Dashboard view
│   │   │   └── chat_view.dart         # Learning interaction view
│   │   ├── services/
│   │   │   └── kag_api_service.dart   # API client
│   │   └── main.dart                  # Flutter entry point
│   └── pubspec.yaml
├── docker-compose.yml
├── .env
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd kag-platform

# Environment is already configured with your API key
# No need to copy .env.example
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- Neo4j on ports 7474 (HTTP UI) and 7687 (Bolt)
- FastAPI backend on port 8000

### 3. Ingest Curriculum Data

```bash
# Wait for Neo4j to be ready (about 30 seconds)
docker-compose exec api python -m app.scripts.ingest_data
```

### 4. Access the Platform

- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (neo4j / kagpassword123)
- **API Root**: http://localhost:8000/

## 📚 API Endpoints

### Learning (Core KAG)

```bash
# Ask a question (main KAG endpoint)
POST /api/v1/learning/ask
{
  "student_id": "student_001",
  "query": "Linear Equations"
}

# Search concepts
GET /api/v1/learning/concepts/search?q=equation

# Get concept details
GET /api/v1/learning/concepts/{concept_id}

# Get concept dependencies
GET /api/v1/learning/concepts/{concept_id}/dependencies

# Check readiness
GET /api/v1/learning/readiness/{student_id}/{concept_id}
```

### Student Management

```bash
# Create student
POST /api/v1/student/

# Get student
GET /api/v1/student/{student_id}

# Get knowledge state
GET /api/v1/student/{student_id}/knowledge-state

# Update mastery
POST /api/v1/student/{student_id}/mastery

# Record struggle
POST /api/v1/student/{student_id}/struggle
```

### Assessment

```bash
# Create assessment
POST /api/v1/assessment/create

# Submit assessment
POST /api/v1/assessment/submit

# Get mastery report
GET /api/v1/assessment/report/{student_id}
```

## 🔬 KAG Reasoning Flow

When a student asks about a concept:

```
1. CONCEPT RESOLUTION
   └─► Find concept in knowledge graph
   └─► If not found → REFUSE

2. DEPENDENCY TRAVERSAL
   └─► Get all prerequisite concepts
   └─► Build dependency chain

3. USER STATE MAPPING
   └─► Get student's mastery state
   └─► Map to dependency chain

4. GAP ANALYSIS
   └─► Identify missing prerequisites
   └─► Calculate readiness score
   └─► Prioritize gaps

5. CONTEXT BUILDING
   └─► Structure reasoning for LLM
   └─► Apply strict constraints
   └─► Set response type

6. LLM VERBALIZATION
   └─► Express reasoning in natural language
   └─► LLM CANNOT add knowledge
```

## 🧠 Knowledge Graph Schema

### Nodes

```cypher
(:Concept {
  id: string,
  name: string,
  description: string,
  domain: string,
  grade_level: int,
  difficulty: float,
  keywords: [string],
  curriculum_code: string
})

(:Student {
  id: string,
  name: string,
  grade_level: int,
  learning_style: string
})

(:Example {id: string, content: string})
(:Formula {id: string, expression: string})
```

### Relationships

```cypher
(:Concept)-[:REQUIRES {strength: float}]->(:Concept)
(:Concept)-[:BUILDS_ON]->(:Concept)
(:Concept)-[:HAS_EXAMPLE]->(:Example)
(:Concept)-[:HAS_FORMULA]->(:Formula)
(:Student)-[:MASTERS {mastery_level: float, confidence: float}]->(:Concept)
(:Student)-[:STRUGGLES_WITH {struggle_count: int, error_patterns: [string]}]->(:Concept)
```

## 🔧 Configuration

Key environment variables (in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://neo4j:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `kagpassword123` |
| `GROQ_API_KEY` | Groq API key | (required) |
| `GROQ_MODEL` | Groq model name | `llama-3.3-70b-versatile` |
| `GROQ_TEMPERATURE` | LLM temperature | `0.1` |
| `MAX_DEPENDENCY_DEPTH` | Max traversal depth | `10` |
| `MIN_MASTERY_THRESHOLD` | Minimum mastery to proceed | `0.7` |

## 📱 Flutter App

### Run the App

```bash
cd flutter_app

# Get dependencies
flutter pub get

# Run on Chrome (web)
flutter run -d chrome

# Run on iOS simulator
flutter run -d ios

# Run on Android emulator
flutter run -d android
```

### Configure API URL

Edit `lib/services/kag_api_service.dart`:

```dart
KagApiService({
  this.baseUrl = 'http://YOUR_HOST:8000/api/v1',  // Change this
});
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### API Testing

Use the Swagger UI at http://localhost:8000/docs

## 📊 Sample Curriculum

The platform includes a sample Mathematics curriculum covering:

- **Grades 1-5**: Basic arithmetic, multiplication, fractions, decimals
- **Grades 6-8**: Ratios, percentages, equations, linear functions
- **Grades 9-12**: Quadratics, trigonometry, calculus

Plus introductory Physics concepts.

## 🔄 PySpark Analytics

Offline batch processing for:

- Curriculum data validation
- Difficulty calibration
- Learning pattern analysis
- Graph partitioning

Run with:
```bash
docker-compose exec api python -c "
from app.analytics.pyspark_jobs import SparkAnalyticsEngine
engine = SparkAnalyticsEngine()
# Run analytics jobs...
"
```

## 🛡️ KAG Constraints

The system enforces these critical constraints:

1. **No External Knowledge**: LLM cannot use knowledge outside the graph
2. **Dependency Order**: Concepts must be explained in dependency order
3. **Gap Acknowledgment**: All gaps must be explicitly addressed
4. **Refusal on Failure**: System refuses when reasoning cannot proceed
5. **Verbalization Only**: LLM role is strictly to express, not to know

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📧 Support

For issues and questions, please open a GitHub issue.
#   S A G U S  
 