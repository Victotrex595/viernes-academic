import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  String _baseUrl;

  ApiService({String baseUrl = 'https://viernes-academic.onrender.com'})
      : _baseUrl = baseUrl.replaceAll(RegExp(r'/$'), '');

  String get baseUrl => _baseUrl;

  void updateBaseUrl(String url) {
    _baseUrl = url.trim().replaceAll(RegExp(r'/$'), '');
  }

  String buildDownloadUrl(String localPath) {
    final encoded = Uri.encodeQueryComponent(localPath);
    return '$_baseUrl/api/files/download?path=$encoded';
  }

  Future<Map<String, dynamic>> fetchHealth({bool verifySaia = false}) async {
    final uri = Uri.parse('$_baseUrl/api/health?verify_saia=$verifySaia');
    final resp = await http.get(uri).timeout(const Duration(seconds: 25));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> fetchCourses() async {
    final uri = Uri.parse('$_baseUrl/api/courses');
    final resp = await http.get(uri).timeout(const Duration(seconds: 25));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> syncSaia() async {
    final uri = Uri.parse('$_baseUrl/api/saia/sync');
    final resp = await http.post(uri).timeout(const Duration(seconds: 90));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> updateSaiaCookie(String cookie) async {
    final uri = Uri.parse('$_baseUrl/api/saia/cookie');
    final resp = await http
        .post(
          uri,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'moodle_session': cookie}),
        )
        .timeout(const Duration(seconds: 30));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> updateAssignmentControls(
    String assignmentId, {
    bool? allowTokenSpend,
    String? taskMode,
  }) async {
    final uri = Uri.parse('$_baseUrl/api/assignments/$assignmentId/controls');
    final payload = <String, dynamic>{};
    if (allowTokenSpend != null) payload['allow_token_spend'] = allowTokenSpend;
    if (taskMode != null) payload['task_mode'] = taskMode;
    final resp = await http
        .patch(
          uri,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(payload),
        )
        .timeout(const Duration(seconds: 15));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> runFourPillarsResearch(
    String assignmentId,
  ) async {
    final uri = Uri.parse('$_baseUrl/api/assignments/$assignmentId/research');
    final resp = await http.post(uri).timeout(const Duration(minutes: 4));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> runConsensusResolution(
    String assignmentId,
  ) async {
    final uri = Uri.parse('$_baseUrl/api/assignments/$assignmentId/resolve');
    final resp = await http.post(uri).timeout(const Duration(minutes: 5));
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> createExternalTopic({
    required String title,
    required String descriptionText,
    required String categoryName,
    required String taskMode,
    List<String> filePaths = const [],
  }) async {
    final uri = Uri.parse('$_baseUrl/api/external/create');
    final req = http.MultipartRequest('POST', uri)
      ..fields['title'] = title
      ..fields['description_text'] = descriptionText
      ..fields['category_name'] = categoryName
      ..fields['task_mode'] = taskMode;

    for (final fp in filePaths) {
      if (fp.isNotEmpty) {
        req.files.add(await http.MultipartFile.fromPath('files', fp));
      }
    }

    final streamed = await req.send().timeout(const Duration(seconds: 60));
    final resp = await http.Response.fromStream(streamed);
    return _decodeResponse(resp);
  }

  Future<Map<String, dynamic>> triggerDriveOAuth() async {
    final uri = Uri.parse('$_baseUrl/api/drive/oauth');
    final resp = await http.post(uri).timeout(const Duration(minutes: 2));
    return _decodeResponse(resp);
  }

  Map<String, dynamic> _decodeResponse(http.Response resp) {
    final body = utf8.decode(resp.bodyBytes);
    final decoded = jsonDecode(body) as Map<String, dynamic>;
    if (resp.statusCode >= 400) {
      throw Exception(decoded['detail'] ?? 'Error HTTP ${resp.statusCode}');
    }
    return decoded;
  }
}
