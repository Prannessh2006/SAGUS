/// KAG Platform - Chat View Model
/// Manages chat/learning interaction state

import 'package:flutter/foundation.dart';
import '../models/kag_models.dart';
import '../services/kag_api_service.dart';

enum ChatStatus {
  initial,
  loading,
  success,
  error,
}

class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final LearningResponse? kagResponse;

  ChatMessage({
    required this.content,
    required this.isUser,
    DateTime? timestamp,
    this.kagResponse,
  }) : timestamp = timestamp ?? DateTime.now();
}

class ChatViewModel extends ChangeNotifier {
  final KagApiService _apiService;
  
  ChatStatus _status = ChatStatus.initial;
  List<ChatMessage> _messages = [];
  String? _errorMessage;
  String? _currentStudentId;

  ChatViewModel({KagApiService? apiService})
      : _apiService = apiService ?? KagApiService();

  // Getters
  ChatStatus get status => _status;
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  String? get errorMessage => _errorMessage;
  bool get isLoading => _status == ChatStatus.loading;
  int get messageCount => _messages.length;

  /// Set the current student ID for queries
  void setStudentId(String studentId) {
    _currentStudentId = studentId;
  }

  /// Send a learning query
  Future<void> sendQuery(String query) async {
    if (_currentStudentId == null) {
      _errorMessage = 'No student selected. Please login first.';
      notifyListeners();
      return;
    }

    if (query.trim().isEmpty) return;

    // Add user message
    _messages.add(ChatMessage(
      content: query,
      isUser: true,
    ));
    
    _status = ChatStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      // Call KAG learning API
      final response = await _apiService.askQuestion(
        studentId: _currentStudentId!,
        query: query,
      );

      // Add KAG response
      _messages.add(ChatMessage(
        content: response.response,
        isUser: false,
        kagResponse: response,
      ));

      _status = ChatStatus.success;
    } catch (e) {
      _status = ChatStatus.error;
      _errorMessage = e.toString();
      
      // Add error message
      _messages.add(ChatMessage(
        content: 'Sorry, I encountered an error: ${e.toString()}',
        isUser: false,
      ));
    }

    notifyListeners();
  }

  /// Search for concepts
  Future<List<Concept>> searchConcepts(String query) async {
    try {
      return await _apiService.searchConcepts(query: query);
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return [];
    }
  }

  /// Get concept details
  Future<Concept?> getConcept(String conceptId) async {
    try {
      return await _apiService.getConcept(conceptId);
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }

  /// Get concept dependencies
  Future<Map<String, dynamic>?> getConceptDependencies(String conceptId) async {
    try {
      return await _apiService.getConceptDependencies(conceptId);
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }

  /// Check readiness for a concept
  Future<Map<String, dynamic>?> checkReadiness(String conceptId) async {
    if (_currentStudentId == null) return null;

    try {
      return await _apiService.checkReadiness(
        studentId: _currentStudentId!,
        conceptId: conceptId,
      );
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }

  /// Clear chat history
  void clearHistory() {
    _messages = [];
    _status = ChatStatus.initial;
    _errorMessage = null;
    notifyListeners();
  }

  /// Clear error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Get the last KAG response
  LearningResponse? get lastKagResponse {
    for (int i = _messages.length - 1; i >= 0; i--) {
      if (_messages[i].kagResponse != null) {
        return _messages[i].kagResponse;
      }
    }
    return null;
  }
}
