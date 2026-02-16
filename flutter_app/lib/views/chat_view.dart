/// KAG Platform - Chat View
/// Learning interaction interface

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/user_viewmodel.dart';
import '../viewmodels/chat_viewmodel.dart';
import '../models/kag_models.dart';

class ChatView extends StatefulWidget {
  const ChatView({super.key});

  @override
  State<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<ChatView> {
  final _queryController = TextEditingController();
  final _scrollController = ScrollController();
  late ChatViewModel _chatVM;

  @override
  void initState() {
    super.initState();
    _chatVM = ChatViewModel();
    
    // Set student ID from user viewmodel
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userVM = context.read<UserViewModel>();
      if (userVM.currentStudent != null) {
        _chatVM.setStudentId(userVM.currentStudent!.studentId);
      }
    });
  }

  @override
  void dispose() {
    _queryController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _chatVM,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('KAG Learning'),
          backgroundColor: Colors.deepPurple,
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: () => _showClearDialog(context),
              tooltip: 'Clear Chat',
            ),
          ],
        ),
        body: Column(
          children: [
            // KAG Status Banner
            _buildKAGBanner(context),
            
            // Messages
            Expanded(
              child: Consumer<ChatViewModel>(
                builder: (context, chatVM, child) {
                  if (chatVM.messages.isEmpty) {
                    return _buildEmptyState(context);
                  }
                  
                  return ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: chatVM.messages.length,
                    itemBuilder: (context, index) {
                      final message = chatVM.messages[index];
                      return _buildMessageBubble(context, message, chatVM);
                    },
                  );
                },
              ),
            ),
            
            // Response Details Panel
            Consumer<ChatViewModel>(
              builder: (context, chatVM, child) {
                final response = chatVM.lastKagResponse;
                if (response != null && !chatVM.isLoading) {
                  return _buildResponseDetails(context, response);
                }
                return const SizedBox.shrink();
              },
            ),
            
            // Input Area
            _buildInputArea(context),
          ],
        ),
      ),
    );
  }

  Widget _buildKAGBanner(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.deepPurple[50],
      child: Row(
        children: [
          Icon(Icons.info_outline, size: 16, color: Colors.deepPurple[700]),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'KAG: Knowledge Graph + User Cognition → Reasoning → LLM Expression',
              style: TextStyle(
                fontSize: 11,
                color: Colors.deepPurple[700],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.school_outlined,
              size: 80,
              color: Colors.grey[300],
            ),
            const SizedBox(height: 16),
            Text(
              'Ask me about any concept!',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Try asking about:\n• "Linear Equations"\n• "Quadratic Formula"\n• "Pythagorean Theorem"',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(
    BuildContext context,
    ChatMessage message,
    ChatViewModel chatVM,
  ) {
    final isUser = message.isUser;
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: isUser 
            ? MainAxisAlignment.end 
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.deepPurple,
              child: Icon(Icons.psychology, size: 16, color: Colors.white),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser 
                    ? Colors.deepPurple 
                    : Colors.grey[100],
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.content,
                    style: TextStyle(
                      color: isUser ? Colors.white : Colors.black87,
                    ),
                  ),
                  if (message.kagResponse != null) ...[
                    const SizedBox(height: 8),
                    _buildResponseMetadata(context, message.kagResponse!),
                  ],
                ],
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.grey[300],
              child: Icon(Icons.person, size: 16, color: Colors.grey[700]),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResponseMetadata(BuildContext context, LearningResponse response) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                _getResponseIcon(response.responseType),
                size: 14,
                color: _getResponseColor(response.responseType),
              ),
              const SizedBox(width: 4),
              Text(
                'Type: ${response.responseType.name}',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          if (response.targetConcept != null) ...[
            const SizedBox(height: 4),
            Text(
              'Target: ${response.targetConcept!.name}',
              style: const TextStyle(fontSize: 11),
            ),
          ],
          if (response.knowledgeGaps.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Gaps: ${response.knowledgeGaps.length}',
              style: const TextStyle(fontSize: 11),
            ),
          ],
        ],
      ),
    );
  }

  IconData _getResponseIcon(ResponseType type) {
    switch (type) {
      case ResponseType.explain:
        return Icons.lightbulb;
      case ResponseType.bridgeGaps:
        return Icons.build;
      case ResponseType.refuse:
        return Icons.block;
    }
  }

  Color _getResponseColor(ResponseType type) {
    switch (type) {
      case ResponseType.explain:
        return Colors.green;
      case ResponseType.bridgeGaps:
        return Colors.orange;
      case ResponseType.refuse:
        return Colors.red;
    }
  }

  Widget _buildResponseDetails(BuildContext context, LearningResponse response) {
    return Container(
      constraints: const BoxConstraints(maxHeight: 200),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        border: Border(
          top: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Text(
                  'Reasoning Details',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Chip(
                  label: Text(
                    '${(response.readinessScore * 100).toInt()}% Ready',
                    style: const TextStyle(fontSize: 11),
                  ),
                  backgroundColor: response.canProceed 
                      ? Colors.green[100] 
                      : Colors.orange[100],
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // Knowledge Gaps
            if (response.knowledgeGaps.isNotEmpty) ...[
              Text(
                'Knowledge Gaps:',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.grey[700],
                ),
              ),
              const SizedBox(height: 4),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: response.knowledgeGaps.take(5).map((gap) {
                  return Chip(
                    label: Text(
                      gap.conceptName,
                      style: const TextStyle(fontSize: 10),
                    ),
                    backgroundColor: _getPriorityColor(gap.priority),
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  );
                }).toList(),
              ),
            ],
            
            // Prerequisites
            if (response.prerequisites.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Prerequisites: ${response.prerequisites.map((p) => p.name).join(", ")}',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getPriorityColor(GapPriority priority) {
    switch (priority) {
      case GapPriority.critical:
        return Colors.red[100]!;
      case GapPriority.high:
        return Colors.orange[100]!;
      case GapPriority.medium:
        return Colors.yellow[100]!;
      case GapPriority.low:
        return Colors.green[100]!;
    }
  }

  Widget _buildInputArea(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _queryController,
                decoration: InputDecoration(
                  hintText: 'Ask about a concept...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
                onSubmitted: (_) => _sendQuery(),
                textInputAction: TextInputAction.send,
              ),
            ),
            const SizedBox(width: 8),
            Consumer<ChatViewModel>(
              builder: (context, chatVM, child) {
                return FloatingActionButton(
                  onPressed: chatVM.isLoading ? null : _sendQuery,
                  backgroundColor: Colors.deepPurple,
                  child: chatVM.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.send, color: Colors.white),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  void _sendQuery() {
    final query = _queryController.text.trim();
    if (query.isEmpty) return;

    _chatVM.sendQuery(query);
    _queryController.clear();
    
    // Scroll to bottom
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _showClearDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Chat'),
        content: const Text('Are you sure you want to clear the chat history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              _chatVM.clearHistory();
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
}
