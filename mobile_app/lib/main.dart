import 'package:flutter/material.dart';
import 'data/repositories/academic_repository.dart';
import 'data/services/api_service.dart';
import 'ui/features/dashboard/view_models/dashboard_view_model.dart';
import 'ui/features/dashboard/views/assignment_card.dart';
import 'ui/features/external_topic/views/external_topic_screen.dart';
import 'ui/features/settings/views/settings_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final apiService = ApiService(baseUrl: 'https://viernes-academic.onrender.com');
  final repository = AcademicRepository(apiService: apiService);
  final viewModel = DashboardViewModel(repository: repository)..initialize();
  runApp(PsmConsortiumApp(viewModel: viewModel));
}

class PsmConsortiumApp extends StatelessWidget {
  final DashboardViewModel viewModel;

  const PsmConsortiumApp({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    const bgBase = Color(0xFF0D0D0F);
    const bgSurface = Color(0xFF141417);
    const borderSubtle = Color(0xFF26262C);

    return MaterialApp(
      title: 'V.I.E.R.N.E.S.',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.dark,
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: bgBase,
        colorScheme: const ColorScheme.dark(
          surface: bgSurface,
          primary: Color(0xFFF4F4F6),
          onPrimary: Color(0xFF0D0D0F),
          secondary: Color(0xFFA1A1AA),
          outline: borderSubtle,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: bgBase,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
        ),
        cardTheme: CardThemeData(
          color: bgSurface,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: borderSubtle, width: 1),
          ),
        ),
      ),
      home: LaunchWorkspaceShell(viewModel: viewModel),
    );
  }
}

class LaunchWorkspaceShell extends StatefulWidget {
  final DashboardViewModel viewModel;

  const LaunchWorkspaceShell({super.key, required this.viewModel});

  @override
  State<LaunchWorkspaceShell> createState() => _LaunchWorkspaceShellState();
}

class _LaunchWorkspaceShellState extends State<LaunchWorkspaceShell> {
  String _activeScreen = 'home'; // 'home' | 'psm' | 'external' | 'settings'
  String? _selectedCourseId;

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: widget.viewModel,
      builder: (context, _) {
        final vm = widget.viewModel;
        final health = vm.health;

        return Scaffold(
          appBar: AppBar(
            leading: _activeScreen != 'home'
                ? IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new, size: 18),
                    onPressed: () => setState(() => _activeScreen = 'home'),
                  )
                : null,
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _activeScreen == 'psm'
                      ? 'V.I.E.R.N.E.S. · SAIA PSM'
                      : _activeScreen == 'external'
                          ? 'V.I.E.R.N.E.S. · TEMA LIBRE'
                          : _activeScreen == 'settings'
                              ? 'V.I.E.R.N.E.S. · SISTEMA'
                              : 'V.I.E.R.N.E.S.',
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    letterSpacing: 1.2,
                  ),
                ),
                Text(
                  '${health?.aiMode ?? "Inicializando..."} · ${health?.totalTokensUsed ?? 0} tokens',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF8E8E98),
                    fontFamily: 'monospace',
                  ),
                ),
              ],
            ),
            actions: [
              if (_activeScreen == 'psm')
                IconButton(
                  tooltip: 'Sincronizar SAIA',
                  onPressed: vm.isSyncing ? null : () => vm.syncSaiaLive(),
                  icon: const Icon(Icons.sync, size: 18),
                ),
              IconButton(
                tooltip: 'Ajustes',
                onPressed: () => setState(() => _activeScreen = 'settings'),
                icon: const Icon(Icons.settings_outlined, size: 18),
              ),
            ],
          ),
          body: _buildActiveBody(context, vm),
        );
      },
    );
  }

  Widget _buildActiveBody(BuildContext context, DashboardViewModel vm) {
    switch (_activeScreen) {
      case 'psm':
        return _buildPsmDashboard(context, vm);
      case 'external':
        return ExternalTopicScreen(viewModel: vm);
      case 'settings':
        return SettingsScreen(viewModel: vm);
      default:
        return _buildExecutiveHome(context, vm);
    }
  }

  Widget _buildExecutiveHome(BuildContext context, DashboardViewModel vm) {
    final psmCourses = vm.courses.where((c) => !c.isExternal).toList();
    final psmActs = psmCourses
        .expand((c) => c.assignments)
        .where((a) => !a.isOverdue)
        .toList();
    final extActs = vm.courses
        .where((c) => c.isExternal)
        .expand((c) => c.assignments)
        .where((a) => !a.isOverdue)
        .toList();
    final visibleCourses = vm.courses
        .where((c) => !c.isExternal || c.assignments.isNotEmpty)
        .toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text(
          'ESPACIOS DE TRABAJO',
          style: TextStyle(
            fontSize: 11,
            fontFamily: 'monospace',
            color: Color(0xFF71717A),
            letterSpacing: 0.8,
          ),
        ),
        const SizedBox(height: 10),

        // Main Button 1: Tareas del PSM
        Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => setState(() => _activeScreen = 'psm'),
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Asignaciones PSM (SAIA)',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Gestiona tus materias inscritas, inspecciona lineamientos del docente, genera los 4 pilares para NotebookLM o resuelve tareas por consenso.',
                          style: TextStyle(
                            fontSize: 12,
                            color: Color(0xFF90909C),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${psmCourses.length} materias · ${psmActs.where((a) => !a.isCompleted).length} activas',
                          style: const TextStyle(
                            fontSize: 11,
                            fontFamily: 'monospace',
                            color: Color(0xFFA1A1AA),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Icon(Icons.chevron_right, color: Color(0xFFA1A1AA)),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Main Button 2: Tema Libre
        Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => setState(() => _activeScreen = 'external'),
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Tema Libre y Evaluación Externa',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Investiga cualquier tema fuera de la universidad bajo los 4 pilares o adjunta una evaluación externa para su resolución.',
                          style: TextStyle(
                            fontSize: 12,
                            color: Color(0xFF90909C),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${extActs.length} proyectos registrados',
                          style: const TextStyle(
                            fontSize: 11,
                            fontFamily: 'monospace',
                            color: Color(0xFFA1A1AA),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Icon(Icons.chevron_right, color: Color(0xFFA1A1AA)),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 24),
        const Text(
          'DOCUMENTACIÓN POR MATERIA',
          style: TextStyle(
            fontSize: 11,
            fontFamily: 'monospace',
            color: Color(0xFF71717A),
            letterSpacing: 0.8,
          ),
        ),
        const SizedBox(height: 10),
        ...visibleCourses.map((course) {
          final activeActs = course.assignments
              .where((a) => !a.isOverdue)
              .toList();
          return Card(
            margin: const EdgeInsets.only(bottom: 10),
            child: ExpansionTile(
              title: Text(
                course.name,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
              subtitle: Text(
                '${activeActs.length} actividad(es) activa(s)',
                style: const TextStyle(
                  fontSize: 11,
                  fontFamily: 'monospace',
                  color: Color(0xFF8E8E98),
                ),
              ),
              children: activeActs.isEmpty
                  ? [
                      const Padding(
                        padding: EdgeInsets.all(14),
                        child: Text(
                          'Sin actividades activas en esta materia.',
                          style: TextStyle(
                            fontSize: 12,
                            color: Color(0xFF71717A),
                          ),
                        ),
                      ),
                    ]
                  : activeActs
                      .map((a) => AssignmentCard(assignment: a, viewModel: vm))
                      .toList(),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildPsmDashboard(BuildContext context, DashboardViewModel vm) {
    final psmCourses = vm.courses.where((c) => !c.isExternal).toList();
    final filteredCourses = _selectedCourseId == null
        ? psmCourses
        : psmCourses.where((c) => c.id == _selectedCourseId).toList();

    final assignments = filteredCourses
        .expand((c) => c.assignments)
        .where((a) => !vm.onlyPending || !a.isCompleted)
        .toList();

    return Column(
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          child: Row(
            children: [
              FilterChip(
                label: const Text('Pendientes'),
                selected: vm.onlyPending,
                onSelected: (val) => vm.toggleOnlyPending(val),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: const Text('Todas'),
                selected: _selectedCourseId == null,
                onSelected: (_) => setState(() => _selectedCourseId = null),
              ),
              const SizedBox(width: 6),
              ...psmCourses.map((c) {
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(
                      c.name.length > 22
                          ? '${c.name.substring(0, 22)}…'
                          : c.name,
                    ),
                    selected: _selectedCourseId == c.id,
                    onSelected: (_) => setState(() => _selectedCourseId = c.id),
                  ),
                );
              }),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.only(bottom: 24),
            itemCount: assignments.length,
            itemBuilder: (context, idx) {
              return AssignmentCard(
                assignment: assignments[idx],
                viewModel: vm,
              );
            },
          ),
        ),
      ],
    );
  }
}
