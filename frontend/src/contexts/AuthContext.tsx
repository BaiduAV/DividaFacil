import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Spinner } from '../components/ui/spinner';
import api, { User, SessionResponse } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window !== 'undefined') {
      try {
        const raw = sessionStorage.getItem('session_user');
        if (raw) return JSON.parse(raw) as User;
      } catch {
        // ignore parse errors
      }
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const session: SessionResponse = await api.getSession();
      if (session.authenticated && session.user) {
        setUser(session.user);
      } else setUser(null);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      await api.login(email, password);
      await checkAuth(); // Refresh user data after login
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      await api.signup({ name, email, password });
      await checkAuth(); // Auto-login after signup is handled by backend
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await api.logout();
      setUser(null);
    } catch (error) {
      // Even if logout fails, clear local state
      setUser(null);
      throw error;
    }
  };

  useEffect(() => {
    checkAuth();

    // Listen for global unauthorized events to clear session state and optionally trigger re-auth UI
    const handleUnauthorized = () => {
      setUser(null);
      // Avoid forcing isLoading=false if we're in the middle of a refresh cycle
      if (!isLoading) {
        setIsLoading(false);
      }
    };
    window.addEventListener('api:unauthorized', handleUnauthorized as EventListener);
    return () => window.removeEventListener('api:unauthorized', handleUnauthorized as EventListener);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    signup,
    logout,
    checkAuth,
  };

  // Simple lightweight skeleton while loading auth state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner label="Loading session" />
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};