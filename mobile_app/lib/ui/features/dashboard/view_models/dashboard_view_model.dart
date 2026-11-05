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
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedUrl = prefs.getString('backend_base_url');
      if (savedUrl != null && savedUrl.trim().isNotEmpty) {
        repository.apiService.updateBaseUrl(savedUrl.trim());
      }
    } catch (e) {
      debugPrint('Error leyendo shared_preferences: $e');
    }
    await refreshAll();
  }

  Future<void> updateBackendUrl(String newUrl) async {
    final cleanUrl = newUrl.trim();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('backend_base_url', cleanUrl);
    } catch (e) {
      debugPrint('Error guardando shared_preferences: $e');
    }
    repository.apiService.updateBaseUrl(cleanUrl);
    await refreshAll();
  }

  Future<void> refreshAll({bool verifySaia = false}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    String? healthErr;
    String? coursesErr;

    try {
      _health = await repository.getHealth(verifySaia: verifySaia);
    } catch (e) {
      healthErr = e.toString().replaceFirst('Exception: ', '');
      debugPrint('Error al obtener salud del sistema: $e');
    }

    try {
      _courses = await repository.getCourses();
    } catch (e) {
      coursesErr = e.toString().replaceFirst('Exception: ', '');
      debugPrint('Error al obtener cursos: $e');
    }

    if (healthErr != null || coursesErr != null) {
      if (healthErr != null && coursesErr != null) {
        _errorMessage = 'Error de conexión: $healthErr';
      } else {
        _errorMessage = healthErr ?? coursesErr;
      }
    }

    _isLoading = false;
    notifyListeners();
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

  Future<String> triggerResearch(String assignmentId) async {
    _busyAssignments[assignmentId] = true;
    notifyListeners();
    try {
      final updated = await repository.executeResearch(assignmentId);
      _replaceAssignmentInMemory(updated);
      _health = await repository.getHealth();
      return 'Investigación de 4 Pilares completada exitosamente.';
    } catch (e) {
      final msg = e.toString().replaceFirst('Exception: ', '');
      return 'Fallo en investigación: $msg';
    } finally {
      _busyAssignments[assignmentId] = false;
      notifyListeners();
    }
  }

  Future<String> triggerResolution(String assignmentId) async {
    _busyAssignments[assignmentId] = true;
    notifyListeners();
    try {
      final updated = await repository.executeResolution(assignmentId);
      _replaceAssignmentInMemory(updated);
      _health = await repository.getHealth();
      return 'Resolución completada. Documento final generado.';
    } catch (e) {
      final msg = e.toString().replaceFirst('Exception: ', '');
      return 'Fallo en resolución: $msg';
    } finally {
      _busyAssignments[assignmentId] = false;
      notifyListeners();
    }
  }

  Future<String> addExternalTopic({
    required String title,
    required String descriptionText,
    required String categoryName,
    required String taskMode,
    List<String> filePaths = const [],
  }) async {
    _isLoading = true;
    notifyListeners();
    try {
      final newAssignment = await repository.createExternalAssignment(
        title: title,
        descriptionText: descriptionText,
        categoryName: categoryName,
        taskMode: taskMode,
        filePaths: filePaths,
      );

      _insertAssignmentInMemory(newAssignment);
      _health = await repository.getHealth();
      return 'Proyecto externo creado exitosamente.';
    } catch (e) {
      final msg = e.toString().replaceFirst('Exception: ', '');
      return 'Error al crear proyecto: $msg';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _replaceAssignmentInMemory(AssignmentModel updated) {
    _courses = _courses.map((c) {
      if (c.id == updated.courseId) {
        final acts = c.assignments
            .map((a) => a.id == updated.id ? updated : a)
            .toList();
        return CourseModel(
          id: c.id,
          name: c.name,
          totalGrade: c.totalGrade,
          isExternal: c.isExternal,
          assignments: acts,
        );
      }
      return c;
    }).toList();
    notifyListeners();
  }

  void _insertAssignmentInMemory(AssignmentModel newAssignment) {
    bool found = false;
    _courses = _courses.map((c) {
      if (c.id == newAssignment.courseId) {
        found = true;
        return CourseModel(
          id: c.id,
          name: c.name,
          totalGrade: c.totalGrade,
          isExternal: c.isExternal,
          assignments: [newAssignment, ...c.assignments],
        );
      }
      return c;
    }).toList();

    if (!found) {
      _courses = [
        CourseModel(
          id: newAssignment.courseId,
          name: newAssignment.courseName,
          totalGrade: '-',
          isExternal: newAssignment.isExternal,
          assignments: [newAssignment],
        ),
        ..._courses,
      ];
    }
    notifyListeners();
  }
}
