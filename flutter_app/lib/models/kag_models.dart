/// KAG Platform - Flutter Data Models
/// Models for the KAG Learning Platform Flutter application

/// Student model representing a learner
class Student {
  final String studentId;
  final String name;
  final int gradeLevel;
  final String learningStyle;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  Student({
    required this.studentId,
    required this.name,
    required this.gradeLevel,
    this.learningStyle = 'visual',
    this.createdAt,
    this.updatedAt,
  });

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      studentId: json['student_id'] ?? '',
      name: json['name'] ?? '',
      gradeLevel: json['grade_level'] ?? 1,
      learningStyle: json['learning_style'] ?? 'visual',
      createdAt: json['created_at'] != null 
          ? DateTime.tryParse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.tryParse(json['updated_at']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'student_id': studentId,
    'name': name,
    'grade_level': gradeLevel,
    'learning_style': learningStyle,
  };
}

/// Concept model representing a knowledge graph concept
class Concept {
  final String id;
  final String name;
  final String? description;
  final String? domain;
  final int? gradeLevel;
  final double? difficulty;
  final List<String> keywords;
  final String? curriculumCode;
  final int? estimatedTimeMinutes;

  Concept({
    required this.id,
    required this.name,
    this.description,
    this.domain,
    this.gradeLevel,
    this.difficulty,
    this.keywords = const [],
    this.curriculumCode,
    this.estimatedTimeMinutes,
  });

  factory Concept.fromJson(Map<String, dynamic> json) {
    return Concept(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'],
      domain: json['domain'],
      gradeLevel: json['grade_level'],
      difficulty: (json['difficulty'] as num?)?.toDouble(),
      keywords: (json['keywords'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
      curriculumCode: json['curriculum_code'],
      estimatedTimeMinutes: json['estimated_time_minutes'],
    );
  }

  String get difficultyLabel {
    if (difficulty == null) return 'Unknown';
    if (difficulty! < 0.3) return 'Easy';
    if (difficulty! < 0.6) return 'Medium';
    if (difficulty! < 0.8) return 'Hard';
    return 'Advanced';
  }
}

/// Knowledge gap model
class KnowledgeGap {
  final String conceptId;
  final String conceptName;
  final GapPriority priority;
  final GapType gapType;
  final int distanceToTarget;
  final double currentMastery;
  final String recommendedAction;
  final List<String> relatedStruggles;

  KnowledgeGap({
    required this.conceptId,
    required this.conceptName,
    required this.priority,
    required this.gapType,
    required this.distanceToTarget,
    required this.currentMastery,
    required this.recommendedAction,
    this.relatedStruggles = const [],
  });

  factory KnowledgeGap.fromJson(Map<String, dynamic> json) {
    return KnowledgeGap(
      conceptId: json['concept_id'] ?? '',
      conceptName: json['concept_name'] ?? '',
      priority: GapPriority.fromString(json['priority'] ?? 'medium'),
      gapType: GapType.fromString(json['type'] ?? 'missing_prerequisite'),
      distanceToTarget: json['distance_to_target'] ?? 0,
      currentMastery: (json['current_mastery'] as num?)?.toDouble() ?? 0.0,
      recommendedAction: json['recommended_action'] ?? '',
      relatedStruggles: (json['related_struggles'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
    );
  }
}

/// Gap priority enum
enum GapPriority {
  critical,
  high,
  medium,
  low;

  static GapPriority fromString(String value) {
    return GapPriority.values.firstWhere(
      (e) => e.name == value.toLowerCase(),
      orElse: () => GapPriority.medium,
    );
  }
}

/// Gap type enum
enum GapType {
  missingPrerequisite,
  forgotten,
  weakUnderstanding,
  misconception;

  static GapType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'missing_prerequisite':
        return GapType.missingPrerequisite;
      case 'forgotten':
        return GapType.forgotten;
      case 'weak_understanding':
        return GapType.weakUnderstanding;
      case 'misconception':
        return GapType.misconception;
      default:
        return GapType.missingPrerequisite;
    }
  }
}

/// Response type enum
enum ResponseType {
  explain,
  bridgeGaps,
  refuse;

  static ResponseType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'explain':
        return ResponseType.explain;
      case 'bridge_gaps':
        return ResponseType.bridgeGaps;
      case 'refuse':
        return ResponseType.refuse;
      default:
        return ResponseType.refuse;
    }
  }
}

/// KAG Learning response model
class LearningResponse {
  final String studentId;
  final String query;
  final String response;
  final ResponseType responseType;
  final Concept? targetConcept;
  final List<Concept> prerequisites;
  final List<KnowledgeGap> knowledgeGaps;
  final double readinessScore;
  final bool canProceed;
  final List<String> reasoningPath;
  final Map<String, int>? llmUsage;

  LearningResponse({
    required this.studentId,
    required this.query,
    required this.response,
    required this.responseType,
    this.targetConcept,
    this.prerequisites = const [],
    this.knowledgeGaps = const [],
    this.readinessScore = 0.0,
    this.canProceed = false,
    this.reasoningPath = const [],
    this.llmUsage,
  });

  factory LearningResponse.fromJson(Map<String, dynamic> json) {
    return LearningResponse(
      studentId: json['student_id'] ?? '',
      query: json['query'] ?? '',
      response: json['response'] ?? '',
      responseType: ResponseType.fromString(json['response_type'] ?? 'refuse'),
      targetConcept: json['target_concept'] != null
          ? Concept.fromJson(json['target_concept'])
          : null,
      prerequisites: (json['prerequisites'] as List<dynamic>?)
          ?.map((e) => Concept.fromJson(e))
          .toList() ?? [],
      knowledgeGaps: (json['knowledge_gaps'] as List<dynamic>?)
          ?.map((e) => KnowledgeGap.fromJson(e))
          .toList() ?? [],
      readinessScore: (json['readiness_score'] as num?)?.toDouble() ?? 0.0,
      canProceed: json['can_proceed'] ?? false,
      reasoningPath: (json['reasoning_path'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
      llmUsage: json['llm_usage'] != null
          ? Map<String, int>.from(json['llm_usage'])
          : null,
    );
  }
}

/// Mastery record model
class MasteryRecord {
  final String conceptId;
  final String conceptName;
  final double masteryLevel;
  final double confidence;
  final DateTime? assessedAt;

  MasteryRecord({
    required this.conceptId,
    required this.conceptName,
    required this.masteryLevel,
    required this.confidence,
    this.assessedAt,
  });

  factory MasteryRecord.fromJson(Map<String, dynamic> json) {
    return MasteryRecord(
      conceptId: json['concept_id'] ?? '',
      conceptName: json['concept_name'] ?? '',
      masteryLevel: (json['mastery_level'] as num?)?.toDouble() ?? 0.0,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      assessedAt: json['assessed_at'] != null
          ? DateTime.tryParse(json['assessed_at'])
          : null,
    );
  }
}

/// Knowledge state model
class KnowledgeState {
  final String studentId;
  final List<MasteryRecord> masteredConcepts;
  final List<StruggleRecord> strugglingConcepts;
  final int totalConceptsKnown;
  final Map<String, dynamic> gradeProgress;

  KnowledgeState({
    required this.studentId,
    this.masteredConcepts = const [],
    this.strugglingConcepts = const [],
    this.totalConceptsKnown = 0,
    this.gradeProgress = const {},
  });

  factory KnowledgeState.fromJson(Map<String, dynamic> json) {
    return KnowledgeState(
      studentId: json['student_id'] ?? '',
      masteredConcepts: (json['mastered_concepts'] as List<dynamic>?)
          ?.map((e) => MasteryRecord.fromJson(e))
          .toList() ?? [],
      strugglingConcepts: (json['struggling_concepts'] as List<dynamic>?)
          ?.map((e) => StruggleRecord.fromJson(e))
          .toList() ?? [],
      totalConceptsKnown: json['total_concepts_known'] ?? 0,
      gradeProgress: json['grade_progress'] ?? {},
    );
  }
}

/// Struggle record model
class StruggleRecord {
  final String conceptId;
  final String conceptName;
  final int struggleCount;
  final List<String> errorPatterns;

  StruggleRecord({
    required this.conceptId,
    required this.conceptName,
    required this.struggleCount,
    this.errorPatterns = const [],
  });

  factory StruggleRecord.fromJson(Map<String, dynamic> json) {
    return StruggleRecord(
      conceptId: json['concept_id'] ?? '',
      conceptName: json['concept_name'] ?? '',
      struggleCount: json['struggle_count'] ?? 0,
      errorPatterns: (json['error_patterns'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
    );
  }
}

/// Assessment result model
class AssessmentResult {
  final String assessmentId;
  final String studentId;
  final String conceptId;
  final double score;
  final double masteryLevel;
  final int questionsCorrect;
  final int questionsTotal;
  final List<QuestionFeedback> feedback;
  final List<String> recommendations;

  AssessmentResult({
    required this.assessmentId,
    required this.studentId,
    required this.conceptId,
    required this.score,
    required this.masteryLevel,
    required this.questionsCorrect,
    required this.questionsTotal,
    this.feedback = const [],
    this.recommendations = const [],
  });

  factory AssessmentResult.fromJson(Map<String, dynamic> json) {
    return AssessmentResult(
      assessmentId: json['assessment_id'] ?? '',
      studentId: json['student_id'] ?? '',
      conceptId: json['concept_id'] ?? '',
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      masteryLevel: (json['mastery_level'] as num?)?.toDouble() ?? 0.0,
      questionsCorrect: json['questions_correct'] ?? 0,
      questionsTotal: json['questions_total'] ?? 0,
      feedback: (json['feedback'] as List<dynamic>?)
          ?.map((e) => QuestionFeedback.fromJson(e))
          .toList() ?? [],
      recommendations: (json['recommendations'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
    );
  }
}

/// Question feedback model
class QuestionFeedback {
  final String questionId;
  final String question;
  final String studentAnswer;
  final String correctAnswer;
  final bool isCorrect;
  final String? explanation;

  QuestionFeedback({
    required this.questionId,
    required this.question,
    required this.studentAnswer,
    required this.correctAnswer,
    required this.isCorrect,
    this.explanation,
  });

  factory QuestionFeedback.fromJson(Map<String, dynamic> json) {
    return QuestionFeedback(
      questionId: json['question_id'] ?? '',
      question: json['question'] ?? '',
      studentAnswer: json['student_answer'] ?? '',
      correctAnswer: json['correct_answer'] ?? '',
      isCorrect: json['is_correct'] ?? false,
      explanation: json['explanation'],
    );
  }
}
