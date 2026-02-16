/// KAG Platform - User View Model
/// Manages user state and student operations

import 'package:flutter/foundation.dart';
import '../models/kag_models.dart';
import '../services/kag_api_service.dart';

enum UserStatus {
  initial,
  loading,
  authenticated,
  error,
}

class UserViewModel extends ChangeNotifier {
  final KagApiService _apiService;
  
  UserStatus _status = UserStatus.initial;
  Student? _currentStudent;
  KnowledgeState? _knowledgeState;
  List<Concept> _recommendedConcepts = [];
  String? _errorMessage;

  UserViewModel({KagApiService? apiService})
      : _apiService = apiService ?? KagApiService();

  // Getters
  UserStatus get status => _status;
  Student? get currentStudent => _currentStudent;
  KnowledgeState? get knowledgeState => _knowledgeState;
  List<Concept> get recommendedConcepts => _recommendedConcepts;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _currentStudent != null;

  /// Create a new student account
  Future<void> createStudent({
    required String studentId,
    required String name,
    required int gradeLevel,
    String learningStyle = 'visual',
  }) async {
    _status = UserStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      final student = Student(
        studentId: studentId,
        name: name,
        gradeLevel: gradeLevel,
        learningStyle: learningStyle,
      );

      _currentStudent = await _apiService.createStudent(student);
      _status = UserStatus.authenticated;
      
      // Load initial knowledge state
      await loadKnowledgeState();
      await loadRecommendations();
    } catch (e) {
      _status = UserStatus.error;
      _errorMessage = e.toString();
    }

    notifyListeners();
  }

  /// Load existing student by ID
  Future<void> loadStudent(String studentId) async {
    _status = UserStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentStudent = await _apiService.getStudent(studentId);
      _status = UserStatus.authenticated;
      
      // Load knowledge state and recommendations
      await loadKnowledgeState();
      await loadRecommendations();
    } catch (e) {
      _status = UserStatus.error;
      _errorMessage = e.toString();
    }

    notifyListeners();
  }

  /// Load student's knowledge state
  Future<void> loadKnowledgeState() async {
    if (_currentStudent == null) return;

    try {
      _knowledgeState = await _apiService.getKnowledgeState(
        _currentStudent!.studentId,
      );
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading knowledge state: $e');
    }
  }

  /// Load recommended concepts
  Future<void> loadRecommendations() async {
    if (_currentStudent == null) return;

    try {
      _recommendedConcepts = await _apiService.getRecommendedConcepts(
        _currentStudent!.studentId,
      );
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading recommendations: $e');
    }
  }

  /// Update mastery for a concept
  Future<void> updateMastery({
    required String conceptId,
    required double masteryLevel,
    double confidence = 0.5,
  }) async {
    if (_currentStudent == null) return;

    try {
      await _apiService.updateMastery(
        studentId: _currentStudent!.studentId,
        conceptId: conceptId,
        masteryLevel: masteryLevel,
        confidence: confidence,
      );
      
      // Refresh knowledge state
      await loadKnowledgeState();
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
    }
  }

  /// Record a struggle with a concept
  Future<void> recordStruggle({
    required String conceptId,
    required String errorPattern,
  }) async {
    if (_currentStudent == null) return;

    try {
      await _apiService.recordStruggle(
        studentId: _currentStudent!.studentId,
        conceptId: conceptId,
        errorPattern: errorPattern,
      );
      
      // Refresh knowledge state
      await loadKnowledgeState();
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
    }
  }

  /// Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Logout
  void logout() {
    _currentStudent = null;
    _knowledgeState = null;
    _recommendedConcepts = [];
    _status = UserStatus.initial;
    _errorMessage = null;
    notifyListeners();
  }
}
