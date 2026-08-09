/**
 * ANNEX browser-extension shell.
 * The Manifest V3 packaging and content-script functionality are added in
 * the dedicated extension phase. This proves the workspace compiles today.
 */
export default function App() {
  return (
    <main style={{ padding: '1rem', width: 320, fontFamily: 'system-ui, sans-serif' }}>
      <h2>ANNEX</h2>
      <p>Learn Before You Believe.</p>
      <p style={{ color: '#6b7280' }}>Extension UI arrives in a later phase.</p>
    </main>
  );
}
