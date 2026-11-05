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
      name: (json['name'] ?? '').toString(),
      localPath: (json['local_path'] ?? '').toString(),
      url: (json['url'] ?? '').toString(),
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
      id: (json['id'] ?? '').toString(),
      courseId: (json['course_id'] ?? '').toString(),
      courseName: (json['course_name'] ?? fallbackCourseName).toString(),
      title: (json['title'] ?? '').toString(),
      type: (json['type'] ?? 'Tarea').toString(),
      link: (json['link'] ?? '').toString(),
      dueDate: (json['due_date'] ?? '').toString(),
      timeRemaining: (json['time_remaining'] ?? '-').toString(),
      status: (json['status'] ?? 'Pendiente').toString(),
      isCompleted: json['is_completed'] == true || json['is_completed'] == 1,
      isOverdue: json['is_overdue'] == true || json['is_overdue'] == 1,
      descriptionText: (json['description_text'] ?? '').toString(),
      taskMode: (json['task_mode'] ?? 'digital').toString(),
      allowTokenSpend:
          json['allow_token_spend'] == true || json['allow_token_spend'] == 1,
      researchStatus: (json['research_status'] ?? 'idle').toString(),
      researchDriveFolderUrl:
          (json['research_drive_folder_url'] ?? '').toString(),
      researchFiles: rawFiles
          .whereType<Map<String, dynamic>>()
          .map((e) => StudyFileItem.fromJson(e))
          .toList(),
      researchSummary: (json['research_summary'] ?? '').toString(),
      resolutionStatus: (json['resolution_status'] ?? 'idle').toString(),
      resolutionDriveUrl: (json['resolution_drive_url'] ?? '').toString(),
      resolutionLocalPath: (json['resolution_local_path'] ?? '').toString(),
      consensusReport: (json['consensus_report'] ?? '').toString(),
      tokensUsed: (json['tokens_used'] as num?)?.toInt() ?? 0,
      isExternal: json['is_external'] == true || json['is_external'] == 1,
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
    final cname = (json['name'] ?? '').toString();
    final rawActs = (json['assignments'] as List<dynamic>? ?? []);
    return CourseModel(
      id: (json['id'] ?? '').toString(),
      name: cname,
      totalGrade: (json['total_grade'] ?? 'Sin calificar').toString(),
      isExternal: json['is_external'] == true || json['is_external'] == 1,
      assignments: rawActs
          .whereType<Map<String, dynamic>>()
          .map(
            (a) => AssignmentModel.fromJson(
              a,
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
      saiaActive: saia['active'] == true
          ? true
          : (saia['active'] == false ? false : null),
      saiaUser: (saia['user'] ?? 'Estudiante PSM').toString(),
      geminiConfigured: aiKeys['gemini_configured'] == true,
      deepseekConfigured: aiKeys['deepseek_configured'] == true,
      aiMode: (aiKeys['mode'] ?? 'Modo Simulación').toString(),
      driveConnected: drive['connected'] == true,
      driveMirrorPath: (drive['local_mirror_path'] ?? '').toString(),
      geminiModel: (models['gemini_model'] ?? 'gemini-3.8-flash').toString(),
      geminiArbiterModel:
          (models['gemini_arbiter_model'] ?? 'gemini-4-argon').toString(),
      deepseekModel:
          (models['deepseek_model'] ?? 'deepseek-reasoner').toString(),
      totalTokensUsed: (json['total_tokens_used'] as num?)?.toInt() ?? 0,
    );
  }
}
