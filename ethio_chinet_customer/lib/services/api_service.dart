import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/post.dart';

class ApiService {
  static const String baseUrl = "http://localhost:8000/api";

  // Get available posts for driver
  Future<List<Post>> getAvailablePosts() async {
    final response = await http.get(Uri.parse("$baseUrl/posts/available/"));

    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Post.fromJson(json)).toList();
    } else {
      throw Exception("Failed to load posts");
    }
  }
}
