import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../data/models/academic_models.dart';
import '../../../../data/repositories/academic_repository.dart';

class DashboardViewModel extends ChangeNotifier {
  final AcademicRepository repository;

  DashboardViewModel({required this.repository});

  SystemHealthStatus? _health;
  SystemHealthStatus? get health => _health;

  List<CourseModel> _courses = [];
  List<CourseModel> get courses => _courses;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  bool _isSyncing = false;
  bool get isSyncing => _isSyncing;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  final Map<String, bool> _busyAssignments = {};
  bool isAssignmentBusy(String id) => _busyAssignments[id] == true;

  bool _onlyPending = false;
  bool get onlyPending => _onlyPending;

  void toggleOnlyPending(bool val) {
    _onlyPending = val;
    notifyListeners();
  }

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    final savedUrl = prefs.getString('backend_base_url');
    if (savedUrl != null && savedUrl.isNotEmpty) {
      repository.apiService.updateBaseUrl(savedUrl);
    }
    await refreshAll();
  }

  Future<void> updateBackendUrl(String newUrl) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('backend_base_url', newUrl.trim());
    repository.apiService.updateBaseUrl(newUrl.trim());
    await refreshAll();
  }

  Future<void> refreshAll({bool verifySaia = false}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      _health = await repository.getHealth(verifySaia: verifySaia);
      _courses = await repository.getCourses();
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<String> syncSaiaLive() async {
    _isSyncing = true;
    _errorMessage = null;
    notifyListeners();
    try {
      _courses = await repository.syncWithSaia();
      _health = await repository.getHealth(verifySaia: true);
      return 'Sincronización con SAIA completada.';
    } catch (e) {
      final msg = e.toString().replaceFirst('Exception: ', '');
      _errorMessage = msg;
      return 'Error al sincronizar: $msg';
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }

  Future<void> toggleTokenSwitch(String assignmentId, bool allow) async {
    final updated = await repository.updateControls(
      assignmentId,
      allowTokenSpend: allow,
    );
    _replaceAssignmentInMemory(updated);
  }

  Future<void> changeTaskMode(String assignmentId, String mode) async {
    final updated = await repository.updateControls(
      assignmentId,
      taskMode: mode,
    );
    _replaceAssignmentInMemory(updated);
  }

  Future<AssignmentModel> runResearch(String assignmentId) async {
    _busyAssignments[assignmentId] = true;
    notifyListeners();
    try {
      final updated = await repository.executeResearch(assignmentId);
      _replaceAssignmentInMemory(updated);
      _health = await repository.getHealth();
      return updated;
    } finally {
      _busyAssignments[assignmentId] = false;
      notifyListeners();
    }
  }

  Future<AssignmentModel> runResolution(String assignmentId) async {
    _busyAssignments[assignmentId] = true;
    notifyListeners();
    try {
      final updated = await repository.executeResolution(assignmentId);
      _replaceAssignmentInMemory(updated);
      _health = await repository.getHealth();
      return updated;
    } finally {
      _busyAssignments[assignmentId] = false;
      notifyListeners();
    }
  }

  Future<AssignmentModel> addExternalTopic({
    required String title,
    required String descriptionText,
    required String categoryName,
    required String taskMode,
    List<String> filePaths = const [],
  }) async {
    final created = await repository.createExternalAssignment(
      title: title,
      descriptionText: descriptionText,
      categoryName: categoryName,
      taskMode: taskMode,
      filePaths: filePaths,
    );
    await refreshAll();
    return created;
  }

  void _replaceAssignmentInMemory(AssignmentModel updated) {
    _courses = _courses.map((course) {
      if (course.id != updated.courseId) return course;
      final newActs = course.assignments
          .map((a) => a.id == updated.id ? updated : a)
          .toList();
      return CourseModel(
        id: course.id,
        name: course.name,
        totalGrade: course.totalGrade,
        isExternal: course.isExternal,
        assignments: newActs,
      );
    }).toList();
    notifyListeners();
  }
}
