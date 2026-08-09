import 'package:flutter_test/flutter_test.dart';

import 'package:annex_mobile/main.dart';

void main() {
  testWidgets('renders the ANNEX tagline', (WidgetTester tester) async {
    await tester.pumpWidget(const AnnexApp());

    expect(find.text('ANNEX'), findsWidgets);
    expect(find.text('Learn Before You Believe'), findsOneWidget);
  });
}
