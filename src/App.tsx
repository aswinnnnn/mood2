import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import JournalPage from './pages/JournalPage';
import NavBar from './components/NavBar';
import { useAuth } from './context/AuthContext';
import PreferencesPage from './pages/PreferencesPage';

// Protected Route wrapper component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/" />;
}

// Layout component that includes NavBar
function Layout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return (
    <>
      {isAuthenticated && <NavBar />}
      <div className={`${isAuthenticated ? 'pt-16' : ''}`}>
        {children}
      </div>
    </>
  );
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();
  
  return (
    <Layout>
      <Routes>
        <Route path="/" element={isAuthenticated ? <Navigate to="/journal" /> : <LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/journal"
          element={
            <ProtectedRoute>
              <JournalPage />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/preferences" 
          element={
            <ProtectedRoute>
              <PreferencesPage />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Layout>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}