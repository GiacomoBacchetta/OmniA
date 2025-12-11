import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import ArchivePage from './pages/ArchivePage'
import AgentPage from './pages/AgentPage'
import MapPage from './pages/MapPage'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/archive" replace />} />
          <Route path="archive" element={<ArchivePage />} />
          <Route path="agent" element={<AgentPage />} />
          <Route path="map" element={<MapPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
