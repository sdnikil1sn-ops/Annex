import { Link, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'

function Shell() {
  const { user, signOut } = useAuth()
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b bg-white px-6 py-4">
        <Link to="/" className="text-lg font-semibold text-slate-900">
          ANNEX
        </Link>
        {user && (
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span>{user.displayName ?? user.email}</span>
            <button
              onClick={() => signOut()}
              className="rounded-md border border-slate-300 px-3 py-1 hover:bg-slate-100"
            >
              Sign out
            </button>
          </div>
        )}
      </header>
      <main className="mx-auto max-w-3xl px-6 py-8">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <p className="text-slate-600">Milestone 2 done — dashboard comes next.</p>
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  )
}
