'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';

interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: Record<string, string>) => Promise<void>;
  signup: (userData: Record<string, string>) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Load persisted authentication details on startup
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
        }
      } catch (err) {
        console.error('Failed to initialize auth state from storage', err);
      } finally {
        setLoading(false);
      }
    };
    initializeAuth();
  }, []);

  // Handle Login
  const login = async (credentials: Record<string, string>) => {
    setLoading(true);
    try {
      // In FastAPI OAuth2 Password Bearer, login uses urlencoded payload or JSON.
      // We will send standard JSON, or adapt as needed.
      const response = await api.post('/auth/login', credentials);
      const { access_token, user: userData } = response.data;

      // Update state
      setToken(access_token);
      setUser(userData);

      // Persist locally
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      router.push('/dashboard');
    } catch (err: any) {
      setLoading(false);
      throw err.response?.data?.detail || 'Login failed. Please check your credentials.';
    } finally {
      setLoading(false);
    }
  };

  // Handle Signup
  const signup = async (userData: Record<string, string>) => {
    setLoading(true);
    try {
      const response = await api.post('/auth/signup', userData);
      const { access_token, user: newUserData } = response.data;

      // Auto-login upon successful registration
      setToken(access_token);
      setUser(newUserData);

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(newUserData));

      router.push('/dashboard');
    } catch (err: any) {
      setLoading(false);
      throw err.response?.data?.detail || 'Signup failed. Please try again.';
    } finally {
      setLoading(false);
    }
  };

  // Handle Logout
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        loading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
