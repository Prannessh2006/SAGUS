/// KAG Platform - Home View
/// Main dashboard view showing student progress and recommendations

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/user_viewmodel.dart';
import '../models/kag_models.dart';
import 'chat_view.dart';

class HomeView extends StatefulWidget {
  const HomeView({super.key});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  final _studentIdController = TextEditingController();
  final _nameController = TextEditingController();
  int _selectedGrade = 7;
  String _selectedStyle = 'visual';
  
  @override
  void dispose() {
    _studentIdController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<UserViewModel>(
      builder: (context, userVM, child) {
        if (userVM.isAuthenticated) {
          return _buildDashboard(context, userVM);
        }
        return _buildLoginScreen(context, userVM);
      },
    );
  }

  Widget _buildLoginScreen(BuildContext context, UserViewModel userVM) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('KAG Learning Platform'),
        centerTitle: true,
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Card(
              elevation: 8,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.school,
                      size: 64,
                      color: Colors.deepPurple,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Knowledge Augmented Generation',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.deepPurple,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Personalized Learning Through Graph Reasoning',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    
                    // Student ID
                    TextField(
                      controller: _studentIdController,
                      decoration: const InputDecoration(
                        labelText: 'Student ID',
                        hintText: 'e.g., student_001',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.badge),
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Name
                    TextField(
                      controller: _nameController,
                      decoration: const InputDecoration(
                        labelText: 'Your Name',
                        hintText: 'Enter your full name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Grade Level
                    DropdownButtonFormField<int>(
                      value: _selectedGrade,
                      decoration: const InputDecoration(
                        labelText: 'Grade Level',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.grade),
                      ),
                      items: List.generate(12, (i) => i + 1)
                          .map((g) => DropdownMenuItem(
                                value: g,
                                child: Text('Grade $g'),
                              ))
                          .toList(),
                      onChanged: (v) => setState(() => _selectedGrade = v!),
                    ),
                    const SizedBox(height: 16),
                    
                    // Learning Style
                    DropdownButtonFormField<String>(
                      value: _selectedStyle,
                      decoration: const InputDecoration(
                        labelText: 'Learning Style',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.psychology),
                      ),
                      items: ['visual', 'auditory', 'kinesthetic', 'reading', 'multimodal']
                          .map((s) => DropdownMenuItem(
                                value: s,
                                child: Text(s[0].toUpperCase() + s.substring(1)),
                              ))
                          .toList(),
                      onChanged: (v) => setState(() => _selectedStyle = v!),
                    ),
                    const SizedBox(height: 24),
                    
                    // Error message
                    if (userVM.errorMessage != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red[50],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.error, color: Colors.red[700]),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                userVM.errorMessage!,
                                style: TextStyle(color: Colors.red[700]),
                              ),
                            ),
                          ],
                        ),
                      ),
                    if (userVM.errorMessage != null) const SizedBox(height: 16),
                    
                    // Create Account Button
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        onPressed: userVM.status == UserStatus.loading
                            ? null
                            : () => _createAccount(userVM),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurple,
                          foregroundColor: Colors.white,
                        ),
                        child: userVM.status == UserStatus.loading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : const Text('Create Account'),
                      ),
                    ),
                    const SizedBox(height: 12),
                    
                    // Or existing user
                    TextButton(
                      onPressed: () => _showLoginDialog(context, userVM),
                      child: const Text('Already have an ID? Login instead'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDashboard(BuildContext context, UserViewModel userVM) {
    final student = userVM.currentStudent!;
    final knowledgeState = userVM.knowledgeState;
    
    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome, ${student.name}'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => userVM.logout(),
            tooltip: 'Logout',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Student info card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundColor: Colors.deepPurple,
                      child: Text(
                        student.name[0].toUpperCase(),
                        style: const TextStyle(
                          fontSize: 24,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            student.name,
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          Text(
                            'Grade ${student.gradeLevel} • ${student.learningStyle[0].toUpperCase()}${student.learningStyle.substring(1)} Learner',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Knowledge State Section
            Text(
              'Your Knowledge State',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    context,
                    'Concepts Mastered',
                    knowledgeState?.totalConceptsKnown.toString() ?? '0',
                    Colors.green,
                    Icons.check_circle,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildStatCard(
                    context,
                    'Struggling Areas',
                    knowledgeState?.strugglingConcepts.length.toString() ?? '0',
                    Colors.orange,
                    Icons.warning,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Recommended Concepts
            Text(
              'Recommended Next Steps',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            
            if (userVM.recommendedConcepts.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Center(
                    child: Text(
                      'Start exploring to get personalized recommendations!',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ),
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: userVM.recommendedConcepts.length,
                itemBuilder: (context, index) {
                  final concept = userVM.recommendedConcepts[index];
                  return _buildConceptCard(context, concept);
                },
              ),
            const SizedBox(height: 24),
            
            // Start Learning Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: () => _navigateToChat(context),
                icon: const Icon(Icons.chat),
                label: const Text('Start Learning'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    Color color,
    IconData icon,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConceptCard(BuildContext context, Concept concept) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.deepPurple[100],
          child: Icon(
            _getDomainIcon(concept.domain),
            color: Colors.deepPurple,
          ),
        ),
        title: Text(concept.name),
        subtitle: Text(
          '${concept.domain ?? "General"} • ${concept.difficultyLabel}',
          style: TextStyle(color: Colors.grey[600]),
        ),
        trailing: Chip(
          label: Text('Grade ${concept.gradeLevel ?? "?"}'),
          backgroundColor: Colors.grey[200],
        ),
        onTap: () => _showConceptDetail(context, concept),
      ),
    );
  }

  IconData _getDomainIcon(String? domain) {
    switch (domain?.toLowerCase()) {
      case 'mathematics':
        return Icons.calculate;
      case 'physics':
        return Icons.science;
      case 'chemistry':
        return Icons.biotech;
      case 'biology':
        return Icons.eco;
      default:
        return Icons.book;
    }
  }

  void _createAccount(UserViewModel userVM) {
    if (_studentIdController.text.isEmpty || _nameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
      );
      return;
    }
    
    userVM.createStudent(
      studentId: _studentIdController.text.trim(),
      name: _nameController.text.trim(),
      gradeLevel: _selectedGrade,
      learningStyle: _selectedStyle,
    );
  }

  void _showLoginDialog(BuildContext context, UserViewModel userVM) {
    final idController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Login'),
        content: TextField(
          controller: idController,
          decoration: const InputDecoration(
            labelText: 'Student ID',
            hintText: 'e.g., student_001',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              userVM.loadStudent(idController.text.trim());
            },
            child: const Text('Login'),
          ),
        ],
      ),
    );
  }

  void _navigateToChat(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ChatView()),
    );
  }

  void _showConceptDetail(BuildContext context, Concept concept) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(concept.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Domain: ${concept.domain ?? "General"}'),
            Text('Grade Level: ${concept.gradeLevel ?? "N/A"}'),
            Text('Difficulty: ${concept.difficultyLabel}'),
            if (concept.description != null) ...[
              const SizedBox(height: 8),
              Text(concept.description!),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _navigateToChat(context);
            },
            child: const Text('Learn This'),
          ),
        ],
      ),
    );
  }
}
