import 'dart:convert';
import 'package:http/http.dart' as http;

class KagApiService {
  // ⚠️ IMPORTANT — Use your laptop IP, NOT localhost
  static const String baseUrl = "http://172.26.81.188:8000";

  static Future<Map<String, dynamic>> askKag(
      String studentId, String query) async {
    final url = Uri.parse("$baseUrl/api/v1/learning/ask");

    final response = await http.post(
      url,
      headers: {
        "Content-Type": "application/json",
      },
      body: jsonEncode({
        "student_id": studentId,
        "query": query,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to connect to KAG API");
    }
  }
}