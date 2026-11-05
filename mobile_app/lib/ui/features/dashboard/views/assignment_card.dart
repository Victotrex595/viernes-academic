import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../data/models/academic_models.dart';
import '../view_models/dashboard_view_model.dart';

class AssignmentCard extends StatelessWidget {
  final AssignmentModel assignment;
  final DashboardViewModel viewModel;

  const AssignmentCard({
    super.key,
    required this.assignment,
    required this.viewModel,
  });

  Future<void> _openUrlOrLocalFile(
    BuildContext context,
    String url,
    String localPath,
  ) async {
    String target = url;
    if (target.isEmpty || target.startsWith('local://')) {
      final rawPath = localPath.isNotEmpty
          ? localPath
          : target.replaceFirst('local://', '');
      target = viewModel.repository.apiService.buildDownloadUrl(rawPath);
    }
    final uri = Uri.parse(target);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ruta del archivo: $localPath')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final busy = viewModel.isAssignmentBusy(assignment.id);

    Color statusColor = Colors.amber.shade700;
    if (assignment.isCompleted) {
      statusColor = Colors.green.shade600;
    } else if (assignment.isOverdue) {
      statusColor = Colors.redAccent;
    }

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header: Course badge + Delivery status
            Row(
              children: [
                Expanded(
                  child: Text(
                    assignment.courseName,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: statusColor.withValues(alpha: 0.5)),
                  ),
                  child: Text(
                    assignment.isCompleted
                        ? 'Entregada'
                        : (assignment.isOverdue ? 'Retrasada' : 'Pendiente'),
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: statusColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Title
            Text(
              assignment.title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),

            // Dates & Time Remaining
            Wrap(
              spacing: 12,
              runSpacing: 4,
              children: [
                if (assignment.dueDate.isNotEmpty)
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.event, size: 15),
                      const SizedBox(width: 4),
                      Text(
                        assignment.dueDate,
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.schedule, size: 15),
                    const SizedBox(width: 4),
                    Text(
                      assignment.timeRemaining,
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
                if (assignment.tokensUsed > 0)
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.bolt, size: 15, color: Colors.amber),
                      Text(
                        '${assignment.tokensUsed} tokens',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
              ],
            ),

            if (assignment.descriptionText.isNotEmpty) ...[
              const SizedBox(height: 10),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest.withValues(
                    alpha: 0.5,
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  assignment.descriptionText,
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.bodySmall,
                ),
              ),
            ],

            const Divider(height: 24),

            // Mode Selector: Digital | Manuscrito | Video
            Text(
              'Modalidad de Asistencia / Entrega:',
              style: theme.textTheme.labelMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 6),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'digital',
                  icon: Icon(Icons.description_outlined, size: 16),
                  label: Text('Digital', style: TextStyle(fontSize: 12)),
                ),
                ButtonSegment(
                  value: 'manuscrito',
                  icon: Icon(Icons.draw_outlined, size: 16),
                  label: Text('A Mano', style: TextStyle(fontSize: 12)),
                ),
                ButtonSegment(
                  value: 'video',
                  icon: Icon(Icons.videocam_outlined, size: 16),
                  label: Text('Video', style: TextStyle(fontSize: 12)),
                ),
              ],
              selected: {assignment.taskMode},
              onSelectionChanged: busy
                  ? null
                  : (selection) {
                      viewModel.changeTaskMode(assignment.id, selection.first);
                    },
            ),

            const SizedBox(height: 12),

            // Token Safety Switch
            Container(
              decoration: BoxDecoration(
                color: assignment.allowTokenSpend
                    ? theme.colorScheme.primaryContainer.withValues(alpha: 0.35)
                    : theme.colorScheme.surfaceContainerHighest.withValues(
                        alpha: 0.35,
                      ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: SwitchListTile(
                dense: true,
                title: const Text(
                  'Consumir Tokens de Resolución',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
                subtitle: Text(
                  assignment.allowTokenSpend
                      ? 'Autorizado: El consorcio IA puede resolver esta actividad.'
                      : 'Protegido: Activa este switch solo si deseas que la IA resuelva la tarea.',
                  style: const TextStyle(fontSize: 11),
                ),
                value: assignment.allowTokenSpend,
                onChanged: busy
                    ? null
                    : (val) => viewModel.toggleTokenSwitch(assignment.id, val),
              ),
            ),

            const SizedBox(height: 12),

            // Two Main Action Buttons
            if (busy)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Center(
                  child: Column(
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 8),
                      Text(
                        'Ejecutando Consorcio IA (DeepSeek-R1 + Gemini)...',
                        style: TextStyle(fontSize: 12),
                      ),
                    ],
                  ),
                ),
              )
            else
              Row(
                children: [
                  Expanded(
                    child: FilledButton.tonalIcon(
                      onPressed: () async {
                        try {
                          await viewModel.runResearch(assignment.id);
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                  '4 Pilares para NotebookLM generados con éxito.',
                                ),
                              ),
                            );
                          }
                        } catch (e) {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Error: $e')),
                            );
                          }
                        }
                      },
                      icon: const Icon(Icons.auto_stories_outlined, size: 18),
                      label: const Text(
                        'Investigar Tema\n(4 Pilares)',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 12),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: assignment.allowTokenSpend
                          ? () async {
                              try {
                                await viewModel.runResolution(assignment.id);
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text(
                                        'Borrador editable generado por Consenso IA (No subido a SAIA).',
                                      ),
                                    ),
                                  );
                                }
                              } catch (e) {
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text('Error: $e')),
                                  );
                                }
                              }
                            }
                          : null,
                      icon: Icon(
                        assignment.allowTokenSpend
                            ? Icons.psychology_outlined
                            : Icons.lock_outline,
                        size: 18,
                      ),
                      label: const Text(
                        'Resolver Tarea\n(Consenso IA)',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 12),
                      ),
                    ),
                  ),
                ],
              ),

            // Results Section: 4 Pillars for NotebookLM
            if (assignment.researchFiles.isNotEmpty) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.secondaryContainer.withValues(
                    alpha: 0.35,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.folder_special_outlined, size: 18),
                        SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Material NotebookLM (4 Pilares Listos)',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ],
                    ),
                    if (assignment.researchSummary.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        assignment.researchSummary,
                        style: const TextStyle(fontSize: 11.5),
                      ),
                    ],
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: assignment.researchFiles.map((file) {
                        return ActionChip(
                          avatar: const Icon(Icons.description, size: 15),
                          label: Text(
                            file.name,
                            style: const TextStyle(fontSize: 11),
                          ),
                          onPressed: () => _openUrlOrLocalFile(
                            context,
                            file.url,
                            file.localPath,
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ],

            // Results Section: Resolution Draft
            if (assignment.resolutionStatus != 'idle' &&
                (assignment.resolutionLocalPath.isNotEmpty ||
                    assignment.resolutionDriveUrl.isNotEmpty)) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.tertiaryContainer.withValues(
                    alpha: 0.35,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.verified_outlined, size: 18),
                        SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Resolución por Consenso IA (Revisión Manual)',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ],
                    ),
                    if (assignment.consensusReport.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        assignment.consensusReport,
                        maxLines: 6,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 11.5),
                      ),
                    ],
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () => _openUrlOrLocalFile(
                          context,
                          assignment.resolutionDriveUrl,
                          assignment.resolutionLocalPath,
                        ),
                        icon: const Icon(Icons.edit_document, size: 18),
                        label: const Text(
                          'Abrir Documento Editable (.docx / Google Docs)',
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
