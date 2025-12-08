import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

class UploadDialog extends StatefulWidget {
  const UploadDialog({super.key});

  @override
  State<UploadDialog> createState() => _UploadDialogState();
}

class _UploadDialogState extends State<UploadDialog> {
  List<PlatformFile> _selectedFiles = [];
  String _statementType = 'credit_card'; // Default to credit card

  Future<void> _pickFiles() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      allowMultiple: true,
    );

    if (result != null) {
      setState(() {
        _selectedFiles = result.files;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          const Icon(Icons.upload_file, color: Color(0xFF4CAF50)),
          const SizedBox(width: 12),
          const Text('Upload Bank Statements'),
        ],
      ),
      content: SizedBox(
        width: 500,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Selected files section
            if (_selectedFiles.isEmpty) ...[
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Center(
                  child: Column(
                    children: [
                      Icon(Icons.cloud_upload_outlined, size: 48, color: Colors.grey[400]),
                      const SizedBox(height: 8),
                      Text(
                        'No files selected',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
              ),
            ] else ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '📄 Selected Files: ${_selectedFiles.length} ${_selectedFiles.length == 1 ? 'file' : 'files'}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    ..._selectedFiles.map((file) => Padding(
                          padding: const EdgeInsets.only(left: 16, top: 4),
                          child: Text('• ${file.name}'),
                        )),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 16),

            // File picker button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _pickFiles,
                icon: const Icon(Icons.folder_open),
                label: Text(_selectedFiles.isEmpty ? 'Select Files' : 'Change Files'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Statement type selection
            const Text(
              'Statement Type:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),

            // Checkbox for checking account
            CheckboxListTile(
              title: const Text('This is a checking account statement'),
              subtitle: const Text('Leave unchecked for credit card statements'),
              value: _statementType == 'checking_account',
              onChanged: (bool? value) {
                setState(() {
                  _statementType = value == true ? 'checking_account' : 'credit_card';
                });
              },
              controlAffinity: ListTileControlAffinity.leading,
              contentPadding: EdgeInsets.zero,
            ),

            const SizedBox(height: 8),

            // Info message
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber[200]!),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, size: 20, color: Colors.amber[900]),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Selection applies to all uploaded files',
                      style: TextStyle(fontSize: 12, color: Colors.amber[900]),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _selectedFiles.isEmpty
              ? null
              : () {
                  Navigator.of(context).pop({
                    'files': _selectedFiles,
                    'statement_type': _statementType,
                  });
                },
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF4CAF50),
            foregroundColor: Colors.white,
            disabledBackgroundColor: Colors.grey[300],
          ),
          child: const Text('Upload'),
        ),
      ],
    );
  }
}
