class StudyFileItem {
  final String name;
  final String localPath;
  final String url;

  const StudyFileItem({
    required this.name,
    required this.localPath,
    required this.url,
  });

  factory StudyFileItem.fromJson(Map<String, dynamic> json) {
    return StudyFileItem(
      name: (json['name'] ?? '') as String,
      localPath: (json['local_path'] ?? '') as String,
      url: (json['url'] ?? '') as String,
    );
  }
}

class AssignmentModel {
  final String id;
  final String courseId;
  final String courseName;
  final String title;
  final String type;
  final String link;
  final String dueDate;
  final String timeRemaining;
  final String status;
  final bool isCompleted;
  final bool isOverdue;
  final String descriptionText;
  final String taskMode; // 'digital' | 'manuscrito' | 'video'
  final bool allowTokenSpend;
  final String researchStatus;
  final String researchDriveFolderUrl;
  final List<StudyFileItem> researchFiles;
  final String researchSummary;
  final String resolutionStatus;
  final String resolutionDriveUrl;
  final String resolutionLocalPath;
  final String consensusReport;
  final int tokensUsed;
  final bool isExternal;

  const AssignmentModel({
    required this.id,
    required this.courseId,
    required this.courseName,
    required this.title,
    required this.type,
    required this.link,
    required this.dueDate,
    required this.timeRemaining,
    required this.status,
    required this.isCompleted,
    required this.isOverdue,
    required this.descriptionText,
    required this.taskMode,
    required this.allowTokenSpend,
    required this.researchStatus,
    required this.researchDriveFolderUrl,
    required this.researchFiles,
    required this.researchSummary,
    required this.resolutionStatus,
    required this.resolutionDriveUrl,
    required this.resolutionLocalPath,
    required this.consensusReport,
    required this.tokensUsed,
    required this.isExternal,
  });

  factory AssignmentModel.fromJson(
    Map<String, dynamic> json, {
    String fallbackCourseName = '',
  }) {
    final rawFiles = (json['research_files'] as List<dynamic>? ?? []);
    return AssignmentModel(
      id: (json['id'] ?? '') as String,
      courseId: (json['course_id'] ?? '') as String,
      courseName: (json['course_name'] ?? fallbackCourseName) as String,
      title: (json['title'] ?? '') as String,
      type: (json['type'] ?? 'Tarea') as String,
      link: (json['link'] ?? '') as String,
      dueDate: (json['due_date'] ?? '') as String,
      timeRemaining: (json['time_remaining'] ?? '-') as String,
      status: (json['status'] ?? 'Pendiente') as String,
      isCompleted: json['is_completed'] == true,
      isOverdue: json['is_overdue'] == true,
      descriptionText: (json['description_text'] ?? '') as String,
      taskMode: (json['task_mode'] ?? 'digital') as String,
      allowTokenSpend: json['allow_token_spend'] == true,
      researchStatus: (json['research_status'] ?? 'idle') as String,
      researchDriveFolderUrl:
          (json['research_drive_folder_url'] ?? '') as String,
      researchFiles: rawFiles
          .map((e) => StudyFileItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      researchSummary: (json['research_summary'] ?? '') as String,
      resolutionStatus: (json['resolution_status'] ?? 'idle') as String,
      resolutionDriveUrl: (json['resolution_drive_url'] ?? '') as String,
      resolutionLocalPath: (json['resolution_local_path'] ?? '') as String,
      consensusReport: (json['consensus_report'] ?? '') as String,
      tokensUsed: (json['tokens_used'] ?? 0) as int,
      isExternal: json['is_external'] == true,
    );
  }
}

class CourseModel {
  final String id;
  final String name;
  final String totalGrade;
  final bool isExternal;
  final List<AssignmentModel> assignments;

  const CourseModel({
    required this.id,
    required this.name,
    required this.totalGrade,
    required this.isExternal,
    required this.assignments,
  });

  factory CourseModel.fromJson(Map<String, dynamic> json) {
    final cname = (json['name'] ?? '') as String;
    final rawActs = (json['assignments'] as List<dynamic>? ?? []);
    return CourseModel(
      id: (json['id'] ?? '') as String,
      name: cname,
      totalGrade: (json['total_grade'] ?? 'Sin calificar') as String,
      isExternal: json['is_external'] == true,
      assignments: rawActs
          .map(
            (a) => AssignmentModel.fromJson(
              a as Map<String, dynamic>,
              fallbackCourseName: cname,
            ),
          )
          .toList(),
    );
  }
}

class SystemHealthStatus {
  final bool saiaConfigured;
  final bool? saiaActive;
  final String saiaUser;
  final bool geminiConfigured;
  final bool deepseekConfigured;
  final String aiMode;
  final bool driveConnected;
  final String driveMirrorPath;
  final String geminiModel;
  final String geminiArbiterModel;
  final String deepseekModel;
  final int totalTokensUsed;

  const SystemHealthStatus({
    required this.saiaConfigured,
    this.saiaActive,
    required this.saiaUser,
    required this.geminiConfigured,
    required this.deepseekConfigured,
    required this.aiMode,
    required this.driveConnected,
    required this.driveMirrorPath,
    required this.geminiModel,
    required this.geminiArbiterModel,
    required this.deepseekModel,
    required this.totalTokensUsed,
  });

  factory SystemHealthStatus.fromJson(Map<String, dynamic> json) {
    final saia = (json['saia'] as Map<String, dynamic>? ?? {});
    final aiKeys = (json['ai_keys'] as Map<String, dynamic>? ?? {});
    final drive = (json['drive'] as Map<String, dynamic>? ?? {});
    final models = (json['models'] as Map<String, dynamic>? ?? {});
    return SystemHealthStatus(
      saiaConfigured: saia['configured'] == true,
      saiaActive: saia['active'] as bool?,
      saiaUser: (saia['user'] ?? 'Estudiante PSM') as String,
      geminiConfigured: aiKeys['gemini_configured'] == true,
      deepseekConfigured: aiKeys['deepseek_configured'] == true,
      aiMode: (aiKeys['mode'] ?? 'Modo Simulación') as String,
      driveConnected: drive['connected'] == true,
      driveMirrorPath: (drive['local_mirror_path'] ?? '') as String,
      geminiModel: (models['gemini_model'] ?? 'gemini-3.8-flash') as String,
      geminiArbiterModel:
          (models['gemini_arbiter_model'] ?? 'gemini-4-argon') as String,
      deepseekModel:
          (models['deepseek_model'] ?? 'deepseek-reasoner') as String,
      totalTokensUsed: (json['total_tokens_used'] ?? 0) as int,
    );
  }
}
