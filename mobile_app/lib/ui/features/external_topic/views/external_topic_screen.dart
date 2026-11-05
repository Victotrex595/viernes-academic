import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../../dashboard/view_models/dashboard_view_model.dart';
import '../../dashboard/views/assignment_card.dart';

class ExternalTopicScreen extends StatefulWidget {
  final DashboardViewModel viewModel;

  const ExternalTopicScreen({super.key, required this.viewModel});

  @override
  State<ExternalTopicScreen> createState() => _ExternalTopicScreenState();
}

class _ExternalTopicScreenState extends State<ExternalTopicScreen> {
  final _titleController = TextEditingController();
  final _categoryController = TextEditingController(
    text: 'Proyectos Libres / Fuera de PSM',
  );
  final _descriptionController = TextEditingController();
  String _selectedMode = 'digital';
  final List<String> _pickedFilePaths = [];
  bool _submitting = false;

  @override
  void dispose() {
    _titleController.dispose();
    _categoryController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickFiles() async {
    final result = await FilePicker.platform.pickFiles(allowMultiple: true);
    if (result != null) {
      setState(() {
        for (final f in result.files) {
          if (f.path != null && !_pickedFilePaths.contains(f.path!)) {
            _pickedFilePaths.add(f.path!);
          }
        }
      });
    }
  }

  Future<void> _submitExternalTopic({required bool runResearchImmediately}) async {
    final title = _titleController.text.trim();
    if (title.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Escribe el título del tema o evaluación externa.'),
        ),
      );
      return;
    }

    setState(() => _submitting = true);
    try {
      final created = await widget.viewModel.addExternalTopic(
        title: title,
        descriptionText: _descriptionController.text.trim(),
        categoryName: _categoryController.text.trim(),
        taskMode: _selectedMode,
        filePaths: _pickedFilePaths,
      );

      if (runResearchImmediately) {
        await widget.viewModel.runResearch(created.id);
      }

      _titleController.clear();
      _descriptionController.clear();
      setState(() => _pickedFilePaths.clear());

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              runResearchImmediately
                  ? 'Tema creado y 4 Pilares de NotebookLM generados.'
                  : 'Tema libre registrado. Puedes investigarlo o resolverlo abajo.',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final externalCourses = widget.viewModel.courses
        .where((c) => c.isExternal)
        .toList();
    final externalAssignments = externalCourses
        .expand((c) => c.assignments)
        .toList();

    return ListView(
      padding: const EdgeInsets.only(bottom: 32),
      children: [
        Card(
          margin: const EdgeInsets.all(14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Nuevo Tema o Evaluación Fuera de PSM',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Ingresa cualquier tema para generar su carpeta de 4 Pilares para NotebookLM, o describe una evaluación externa con sus archivos adjuntos para resolverla en consenso.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: _titleController,
                  decoration: const InputDecoration(
                    labelText: 'Tema o Título de la Evaluación *',
                    hintText: 'Ej. Redes Neuronales / Examen Certificación AWS',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.topic_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _categoryController,
                  decoration: const InputDecoration(
                    labelText: 'Carpeta / Categoría en Google Drive',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.create_new_folder_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _descriptionController,
                  maxLines: 4,
                  decoration: const InputDecoration(
                    labelText: 'Lineamientos, Enunciado o Puntos a Investigar',
                    hintText:
                        'Pega aquí las instrucciones, preguntas o aspectos específicos que quieres cubrir...',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(
                      value: 'digital',
                      icon: Icon(Icons.description_outlined, size: 16),
                      label: Text('Digital'),
                    ),
                    ButtonSegment(
                      value: 'manuscrito',
                      icon: Icon(Icons.draw_outlined, size: 16),
                      label: Text('A Mano'),
                    ),
                    ButtonSegment(
                      value: 'video',
                      icon: Icon(Icons.videocam_outlined, size: 16),
                      label: Text('Video'),
                    ),
                  ],
                  selected: {_selectedMode},
                  onSelectionChanged: (s) =>
                      setState(() => _selectedMode = s.first),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: _pickFiles,
                  icon: const Icon(Icons.attach_file),
                  label: Text(
                    _pickedFilePaths.isEmpty
                        ? 'Adjuntar PDF, Word o Foto de Enunciado'
                        : '${_pickedFilePaths.length} archivo(s) adjunto(s)',
                  ),
                ),
                if (_pickedFilePaths.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    children: _pickedFilePaths.map((p) {
                      final name = p.split(RegExp(r'[/\\]')).last;
                      return InputChip(
                        label: Text(name, style: const TextStyle(fontSize: 11)),
                        onDeleted: () =>
                            setState(() => _pickedFilePaths.remove(p)),
                      );
                    }).toList(),
                  ),
                ],
                const SizedBox(height: 16),
                if (_submitting)
                  const Center(child: CircularProgressIndicator())
                else
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.tonalIcon(
                          onPressed: () => _submitExternalTopic(
                            runResearchImmediately: false,
                          ),
                          icon: const Icon(Icons.add_task),
                          label: const Text('Guardar en Lista'),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () => _submitExternalTopic(
                            runResearchImmediately: true,
                          ),
                          icon: const Icon(Icons.auto_stories_outlined),
                          label: const Text('Crear + 4 Pilares'),
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
        if (externalAssignments.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
            child: Text(
              'Mis Temas y Evaluaciones Libres (${externalAssignments.length})',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ),
          ...externalAssignments.map(
            (a) => AssignmentCard(assignment: a, viewModel: widget.viewModel),
          ),
        ],
      ],
    );
  }
}
