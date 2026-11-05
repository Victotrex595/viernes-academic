import '../models/academic_models.dart';
import '../services/api_service.dart';

class AcademicRepository {
  final ApiService apiService;

  AcademicRepository({required this.apiService});

  Future<SystemHealthStatus> getHealth({bool verifySaia = false}) async {
    final json = await apiService.fetchHealth(verifySaia: verifySaia);
    return SystemHealthStatus.fromJson(json);
  }

  Future<List<CourseModel>> getCourses() async {
    final json = await apiService.fetchCourses();
    final list = (json['courses'] as List<dynamic>? ?? []);
    return list
        .map((c) => CourseModel.fromJson(c as Map<String, dynamic>))
        .toList();
  }

  Future<List<CourseModel>> syncWithSaia() async {
    final json = await apiService.syncSaia();
    final list = (json['courses'] as List<dynamic>? ?? []);
    return list
        .map((c) => CourseModel.fromJson(c as Map<String, dynamic>))
        .toList();
  }

  Future<bool> updateCookie(String cookie) async {
    final json = await apiService.updateSaiaCookie(cookie);
    return json['session_active'] == true;
  }

  Future<AssignmentModel> updateControls(
    String assignmentId, {
    bool? allowTokenSpend,
    String? taskMode,
  }) async {
    final json = await apiService.updateAssignmentControls(
      assignmentId,
      allowTokenSpend: allowTokenSpend,
      taskMode: taskMode,
    );
    return AssignmentModel.fromJson(json['assignment'] as Map<String, dynamic>);
  }

  Future<AssignmentModel> executeResearch(String assignmentId) async {
    final json = await apiService.runFourPillarsResearch(assignmentId);
    return AssignmentModel.fromJson(json['assignment'] as Map<String, dynamic>);
  }

  Future<AssignmentModel> executeResolution(String assignmentId) async {
    final json = await apiService.runConsensusResolution(assignmentId);
    return AssignmentModel.fromJson(json['assignment'] as Map<String, dynamic>);
  }

  Future<AssignmentModel> createExternalAssignment({
    required String title,
    required String descriptionText,
    required String categoryName,
    required String taskMode,
    List<String> filePaths = const [],
  }) async {
    final json = await apiService.createExternalTopic(
      title: title,
      descriptionText: descriptionText,
      categoryName: categoryName,
      taskMode: taskMode,
      filePaths: filePaths,
    );
    return AssignmentModel.fromJson(json['assignment'] as Map<String, dynamic>);
  }
}
