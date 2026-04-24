import React, { createContext, useContext, useState } from 'react';
import { CURRENT_USER, Player } from '@/data/players';

interface AuthContextType {
  user: Player | null;
  isLoggedIn: boolean;
  login: () => void;
  logout: () => void;
  updateProfile: (updates: Partial<Player>) => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoggedIn: false,
  login: () => {},
  logout: () => {},
  updateProfile: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Player | null>(CURRENT_USER);
  const [isLoggedIn, setIsLoggedIn] = useState(true);

  const login = () => {
    setUser(CURRENT_USER);
    setIsLoggedIn(true);
  };

  const logout = () => {
    setUser(null);
    setIsLoggedIn(false);
  };

  const updateProfile = (updates: Partial<Player>) => {
    setUser(prev => prev ? { ...prev, ...updates } : prev);
  };

  return (
    <AuthContext.Provider value={{ user, isLoggedIn, login, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
