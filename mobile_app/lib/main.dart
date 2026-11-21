import 'package:flutter/material.dart';
import 'data/repositories/academic_repository.dart';
import 'data/services/api_service.dart';
import 'ui/features/dashboard/view_models/dashboard_view_model.dart';
import 'ui/features/dashboard/views/assignment_card.dart';
import 'ui/features/external_topic/views/external_topic_screen.dart';
import 'ui/features/settings/views/settings_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final apiService =
      ApiService(baseUrl: 'https://viernes-academic-i7x3.onrender.com');
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

  void _handleBack() {
    setState(() {
      if (_selectedCourseId != null) {
        _selectedCourseId = null;
      } else if (_activeScreen != 'home') {
        _activeScreen = 'home';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: widget.viewModel,
      builder: (context, _) {
        final vm = widget.viewModel;
        final health = vm.health;
        final bool isRootLevel =
            _activeScreen == 'home' && _selectedCourseId == null;

        return PopScope(
          canPop: isRootLevel,
          onPopInvokedWithResult: (didPop, result) {
            if (didPop) return;
            _handleBack();
          },
          child: Scaffold(
            appBar: AppBar(
              leading: (!isRootLevel)
                  ? IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new, size: 18),
                      onPressed: _handleBack,
                    )
                  : null,
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _activeScreen == 'psm'
                        ? (_selectedCourseId != null
                            ? 'V.I.E.R.N.E.S. · MATERIA'
                            : 'V.I.E.R.N.E.S. · SAIA PSM')
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
                    vm.isLoading
                        ? 'Conectando al servidor...'
                        : '${health?.aiMode ?? "Desconectado"} · ${health?.totalTokensUsed ?? 0} tokens',
                    style: TextStyle(
                      fontSize: 11,
                      color: vm.isLoading
                          ? Colors.amberAccent
                          : (health != null
                              ? const Color(0xFF4CAF50)
                              : const Color(0xFF8E8E98)),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
              actions: [
                if (vm.isLoading)
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 12),
                    child: Center(
                      child: SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white70),
                        ),
                      ),
                    ),
                  )
                else ...[
                  if (_activeScreen == 'psm')
                    IconButton(
                      tooltip: 'Sincronizar SAIA en vivo',
                      onPressed: vm.isSyncing ? null : () => vm.syncSaiaLive(),
                      icon: vm.isSyncing
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.sync, size: 18),
                    ),
                  IconButton(
                    tooltip: 'Actualizar datos',
                    onPressed: () => vm.refreshAll(),
                    icon: const Icon(Icons.refresh, size: 18),
                  ),
                ],
                IconButton(
                  tooltip: 'Ajustes',
                  onPressed: () => setState(() => _activeScreen = 'settings'),
                  icon: const Icon(Icons.settings_outlined, size: 18),
                ),
              ],
            ),
            body: _buildActiveBody(context, vm),
          ),
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

    return RefreshIndicator(
      onRefresh: () => vm.refreshAll(),
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        children: [
          // Banner de error si falla la conexión
          if (vm.errorMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF2E1515),
                borderRadius: BorderRadius.circular(10),
                border:
                    Border.all(color: const Color(0xFFE53935).withOpacity(0.6)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.wifi_off,
                      color: Color(0xFFE53935), size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      vm.errorMessage!,
                      style: const TextStyle(
                          fontSize: 12, color: Color(0xFFFFCDD2)),
                    ),
                  ),
                  TextButton(
                    onPressed: () => vm.refreshAll(),
                    child: const Text('Reintentar',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
          ],

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
          if (visibleCourses.isEmpty && !vm.isLoading) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 20),
              child: Center(
                child: Text(
                  vm.errorMessage != null
                      ? 'No se pudieron cargar las materias. Revisa tu conexión.'
                      : 'No hay materias registradas aún.',
                  style:
                      const TextStyle(fontSize: 13, color: Color(0xFF71717A)),
                ),
              ),
            ),
          ],
          ...visibleCourses.map((course) {
            final activeActs =
                course.assignments.where((a) => !a.isOverdue).toList();
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
                        .map(
                            (a) => AssignmentCard(assignment: a, viewModel: vm))
                        .toList(),
              ),
            );
          }),
        ],
      ),
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

    return RefreshIndicator(
      onRefresh: () => vm.refreshAll(),
      child: Column(
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
                      onSelected: (_) =>
                          setState(() => _selectedCourseId = c.id),
                    ),
                  );
                }),
              ],
            ),
          ),
          Expanded(
            child: assignments.isEmpty
                ? const Center(
                    child: Text(
                      'No hay actividades para mostrar.',
                      style: TextStyle(fontSize: 13, color: Color(0xFF71717A)),
                    ),
                  )
                : ListView.builder(
                    physics: const AlwaysScrollableScrollPhysics(),
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
      ),
    );
  }
}
