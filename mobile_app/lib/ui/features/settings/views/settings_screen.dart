import 'package:flutter/material.dart';
import '../../dashboard/view_models/dashboard_view_model.dart';

class SettingsScreen extends StatefulWidget {
  final DashboardViewModel viewModel;

  const SettingsScreen({super.key, required this.viewModel});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlController;
  final _cookieController = TextEditingController();
  bool _savingCookie = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(
      text: widget.viewModel.repository.apiService.baseUrl,
    );
  }

  @override
  void dispose() {
    _urlController.dispose();
    _cookieController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final health = widget.viewModel.health;

    return ListView(
      padding: const EdgeInsets.all(14),
      children: [
        // 1. Backend / Tunnel Connection
        Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.dns_outlined),
                    SizedBox(width: 8),
                    Text(
                      'Conexión al Servidor (PC Local / Túnel)',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Usa http://10.0.2.2:8000 en emulador Android, la IP local de tu PC en Wi-Fi, o tu enlace HTTPS de Cloudflare Tunnel / Tailscale desde cualquier lugar.',
                  style: TextStyle(fontSize: 12),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _urlController,
                  decoration: const InputDecoration(
                    labelText: 'URL del Backend FastAPI',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.tonalIcon(
                    onPressed: () async {
                      await widget.viewModel.updateBackendUrl(
                        _urlController.text,
                      );
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('URL actualizada y verificada.'),
                          ),
                        );
                      }
                    },
                    icon: const Icon(Icons.sync),
                    label: const Text('Guardar y Probar Conexión'),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // 2. SAIA Cookie Renewal
        Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.school_outlined),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'Sesión SAIA PSM (MoodleSession)',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                    ),
                    Chip(
                      label: Text(
                        health?.saiaActive == true
                            ? 'Activa'
                            : (health?.saiaConfigured == true
                                  ? 'Configurada'
                                  : 'Sin Cookie'),
                        style: const TextStyle(fontSize: 11),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _cookieController,
                  decoration: const InputDecoration(
                    labelText: 'Pegar nueva cookie MoodleSession',
                    hintText: 'Ej. 8aumev6pno5o099bk1v6bpfruf',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.key),
                  ),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: _savingCookie
                        ? null
                        : () async {
                            final c = _cookieController.text.trim();
                            if (c.isEmpty) return;
                            setState(() => _savingCookie = true);
                            try {
                              final active = await widget.viewModel.repository
                                  .updateCookie(c);
                              await widget.viewModel.refreshAll(
                                verifySaia: true,
                              );
                              _cookieController.clear();
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      active
                                          ? 'Sesión SAIA activa y verificada en /my/.'
                                          : 'Cookie guardada, pero SAIA indica sesión expirada.',
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
                            } finally {
                              if (mounted) {
                                setState(() => _savingCookie = false);
                              }
                            }
                          },
                    icon: const Icon(Icons.verified_user_outlined),
                    label: const Text('Actualizar y Verificar en SAIA'),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // 3. AI Consortium & Google Drive Status
        Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.hub_outlined),
                    SizedBox(width: 8),
                    Text(
                      'Estado del Consorcio IA y Google Drive',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(
                    health?.geminiConfigured == true
                        ? Icons.check_circle
                        : Icons.science_outlined,
                    color: health?.geminiConfigured == true
                        ? Colors.green
                        : Colors.amber,
                  ),
                  title: Text('Gemini (${health?.geminiModel ?? "gemini-3.8-flash"})'),
                  subtitle: Text(
                    health?.geminiConfigured == true
                        ? 'API Key activa en .env'
                        : 'En espera de API Key (Modo Simulación 0 Tokens)',
                  ),
                ),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(
                    health?.deepseekConfigured == true
                        ? Icons.check_circle
                        : Icons.science_outlined,
                    color: health?.deepseekConfigured == true
                        ? Colors.green
                        : Colors.amber,
                  ),
                  title: Text('DeepSeek (${health?.deepseekModel ?? "deepseek-reasoner"})'),
                  subtitle: Text(
                    health?.deepseekConfigured == true
                        ? 'API Key activa en .env'
                        : 'En espera de API Key (Modo Simulación 0 Tokens)',
                  ),
                ),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(
                    health?.driveConnected == true
                        ? Icons.cloud_done
                        : Icons.folder_copy_outlined,
                    color: health?.driveConnected == true
                        ? Colors.green
                        : Colors.blueAccent,
                  ),
                  title: const Text('Google Drive & NotebookLM'),
                  subtitle: Text(
                    health?.driveConnected == true
                        ? 'Conectado vía OAuth2 a tu Google Drive'
                        : 'Espejo local activo en Moodle_PSM_Estudio/',
                  ),
                  trailing: OutlinedButton(
                    onPressed: () async {
                      try {
                        final res = await widget.viewModel.repository.apiService
                            .triggerDriveOAuth();
                        await widget.viewModel.refreshAll();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(res['message']?.toString() ?? 'OK'),
                            ),
                          );
                        }
                      } catch (e) {
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Aviso: $e')),
                          );
                        }
                      }
                    },
                    child: const Text('Conectar OAuth'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
