import 'package:flutter/material.dart';
import 'services/kag_api.dart';

void main() {
  runApp(const KagApp());
}

class KagApp extends StatelessWidget {
  const KagApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "KAG Learning",
      theme: ThemeData.dark(),
      home: const LearningScreen(),
    );
  }
}

class LearningScreen extends StatefulWidget {
  const LearningScreen({super.key});

  @override
  State<LearningScreen> createState() => _LearningScreenState();
}

class _LearningScreenState extends State<LearningScreen> {
  final TextEditingController controller = TextEditingController();
  String response = "";
  bool loading = false;

  Future<void> askKag() async {
    setState(() {
      loading = true;
      response = "";
    });

    try {
      final result = await KagApi.askQuestion(
        studentId: "student_001",
        query: controller.text,
      );

      setState(() {
        response = result["response"];
      });
    } catch (e) {
      setState(() {
        response = "❌ Could not reach backend";
      });
    }

    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("KAG Learning System")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: "Ask a Concept",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: askKag,
              child: const Text("Ask KAG"),
            ),
            const SizedBox(height: 20),
            if (loading) const CircularProgressIndicator(),
            Expanded(
              child: SingleChildScrollView(
                child: Text(response),
              ),
            )
          ],
        ),
      ),
    );
  }
}