import 'package:flutter/material.dart';

/// Time period selector widget for monthly trends chart
/// 
/// Provides three period options: 2 Months, 6 Months, YTD
/// Uses segmented button design for clean UI
class TimePeriodSelector extends StatelessWidget {
  final String selectedPeriod;
  final Function(String) onPeriodChanged;

  const TimePeriodSelector({
    super.key,
    required this.selectedPeriod,
    required this.onPeriodChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            'Time Period: ',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(width: 12),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(
                value: '2m',
                label: Text('2 Months'),
              ),
              ButtonSegment(
                value: '6m',
                label: Text('6 Months'),
              ),
              ButtonSegment(
                value: 'ytd',
                label: Text('YTD'),
              ),
            ],
            selected: {selectedPeriod},
            onSelectionChanged: (Set<String> selection) {
              onPeriodChanged(selection.first);
            },
            style: ButtonStyle(
              backgroundColor: WidgetStateProperty.resolveWith<Color>(
                (Set<WidgetState> states) {
                  if (states.contains(WidgetState.selected)) {
                    return theme.colorScheme.primaryContainer;
                  }
                  return theme.colorScheme.surface;
                },
              ),
              foregroundColor: WidgetStateProperty.resolveWith<Color>(
                (Set<WidgetState> states) {
                  if (states.contains(WidgetState.selected)) {
                    return theme.colorScheme.onPrimaryContainer;
                  }
                  return theme.colorScheme.onSurface;
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
