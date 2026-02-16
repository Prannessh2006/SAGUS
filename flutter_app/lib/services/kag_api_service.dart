/// KAG Platform - API Service
/// Service for communicating with the KAG backend API

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/kag_models.dart';

class KagApiService {
  final String baseUrl;
  final http.Client _client;

  KagApiService({
  this.baseUrl = 'http://127.0.0.1:8000/api/v1',
  http.Client? client,
}) : _client = client ?? http.Client();

  /// Create a new student
  Future<Student> createStudent(Student student) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/student/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(student.toJson()),
    );

    if (response.statusCode == 200) {
      return Student.fromJson(jsonDecode(response.body));
    }
    throw _handleError(response);
  }

  /// Get student by ID
  Future<Student> getStudent(String studentId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/student/$studentId'),
    );

    if (response.statusCode == 200) {
      return Student.fromJson(jsonDecode(response.body));
    }
    throw _handleError(response);
  }

  /// Get student's knowledge state
  Future<KnowledgeState> getKnowledgeState(String studentId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/student/$studentId/knowledge-state'),
    );

    if (response.statusCode == 200) {
      return KnowledgeState.fromJson(jsonDecode(response.body));
    }
    throw _handleError(response);
  }

  /// Update concept mastery
  Future<void> updateMastery({
    required String studentId,
    required String conceptId,
    required double masteryLevel,
    double confidence = 0.5,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/student/$studentId/mastery'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'concept_id': conceptId,
        'mastery_level': masteryLevel,
        'confidence': confidence,
      }),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Record a struggle
  Future<void> recordStruggle({
    required String studentId,
    required String conceptId,
    required String errorPattern,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/student/$studentId/struggle'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'concept_id': conceptId,
        'error_pattern': errorPattern,
      }),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Get recommended concepts
  Future<List<Concept>> getRecommendedConcepts(String studentId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/student/$studentId/recommended'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final recommendations = data['recommendations'] as List;
      return recommendations.map((e) => Concept.fromJson(e)).toList();
    }
    throw _handleError(response);
  }

  /// KAG Learning interaction - Main endpoint
  Future<LearningResponse> askQuestion({
    required String studentId,
    required String query,
    Map<String, dynamic>? context,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/learning/ask'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'student_id': studentId,
        'query': query,
        'context': context,
      }),
    );

    if (response.statusCode == 200) {
      return LearningResponse.fromJson(jsonDecode(response.body));
    }
    throw _handleError(response);
  }

  /// Search concepts
  Future<List<Concept>> searchConcepts({
    required String query,
    String? domain,
    int? gradeLevel,
  }) async {
    final uri = Uri.parse('$baseUrl/learning/concepts/search').replace(
      queryParameters: {
        'q': query,
        if (domain != null) 'domain': domain,
        if (gradeLevel != null) 'grade_level': gradeLevel.toString(),
      },
    );

    final response = await _client.get(uri);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final results = data['results'] as List;
      return results.map((e) => Concept.fromJson(e)).toList();
    }
    throw _handleError(response);
  }

  /// Get concept by ID
  Future<Concept> getConcept(String conceptId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/learning/concepts/$conceptId'),
    );

    if (response.statusCode == 200) {
      return Concept.fromJson(jsonDecode(response.body));
    }
    throw _handleError(response);
  }

  /// Get concept dependencies
  Future<Map<String, dynamic>> getConceptDependencies(String conceptId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/learning/concepts/$conceptId/dependencies'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw _handleError(response);
  }

  /// Get all domains
  Future<Map<String, dynamic>> getDomains() async {
    final response = await _client.get(
      Uri.parse('$baseUrl/learning/domains'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw _handleError(response);
  }

  /// Check readiness for a concept
  Future<Map<String, dynamic>> checkReadiness({
    required String studentId,
    required String conceptId,
  }) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/learning/readiness/$studentId/$conceptId'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw _handleError(response);
  }

  /// Create assessment
  Future<Map<String, dynamic>> createAssessment({
    required String studentId,
    required String conceptId,
    required List<Map<String, dynamic>> questions,
    String assessmentType = 'quiz',
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/assessment/create'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'student_id': studentId,
        'concept_id': conceptId,
        'assessment_type': assessmentType,
        'questions': questions,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw _handleError(response);
  }

  /// Submit assessment
  Future<AssessmentResult> submitAssessment({
    required String assessmentId,
    required String studentId,
    required List<Map<String, dynamic>> answers,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/assessment/submit'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'assessment_id': assessmentId,
        'student_id': studentId,
        'answers': answers,
      }),
    );

    if (response.statusCode == 200) {
      return AssessmentResult.fromJson(jsonDecode(response.body));
    }
    throw _handleError(response);
  }

  /// Get mastery report
  Future<Map<String, dynamic>> getMasteryReport(String studentId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/assessment/report/$studentId'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw _handleError(response);
  }

  Exception _handleError(http.Response response) {
    final message = jsonDecode(response.body)['detail'] ?? 'Unknown error';
    return Exception('API Error ${response.statusCode}: $message');
  }

  void dispose() {
    _client.close();
  }
}
