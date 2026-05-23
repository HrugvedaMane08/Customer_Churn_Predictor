'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/auth-context';
import { ProtectedRoute } from '@/components/shared/protected-route';
import { 
  LayoutDashboard, 
  BrainCircuit, 
  History, 
  UserCircle, 
  LogOut, 
  Menu, 
  X, 
  Bell, 
  Sun, 
  Moon 
} from 'lucide-react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Navigation tabs config
  const navItems = [
    { name: 'Analytics Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Churn Assessment', href: '/prediction', icon: BrainCircuit },
    { name: 'Prediction History', href: '/history', icon: History },
    { name: 'User Profile', href: '/profile', icon: UserCircle },
  ];

  return (
    <ProtectedRoute>
      <div className={`flex min-h-screen ${theme === 'dark' ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-950'} transition-colors duration-300`}>
        {/* ================================================== */}
        {/* DESKTOP SIDEBAR */}
        {/* ================================================== */}
        <aside className="hidden w-64 border-r border-slate-800 bg-slate-900/50 backdrop-blur-md md:flex md:flex-col md:fixed md:inset-y-0">
          <div className="flex h-16 items-center gap-2 px-6 border-b border-slate-850">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
              <BrainCircuit className="h-5.5 w-5.5" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              ChurnPredict AI
            </span>
          </div>

          <nav className="flex-1 space-y-1 px-4 py-6">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/10'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                  }`}
                >
                  <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-white'}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User Info footer */}
          <div className="p-4 border-t border-slate-850">
            <div className="flex items-center gap-3 px-2 py-3 rounded-xl bg-slate-800/30">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-500 text-white font-bold text-sm">
                {user?.name ? user.name[0].toUpperCase() : 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold truncate text-white">{user?.name || 'User'}</p>
                <p className="text-[10px] text-slate-500 truncate">{user?.email || 'user@example.com'}</p>
              </div>
              <button 
                onClick={logout}
                className="text-slate-400 hover:text-red-400 transition-colors p-1"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </aside>

        {/* ================================================== */}
        {/* MOBILE SIDEBAR DRAWER */}
        {/* ================================================== */}
        {mobileMenuOpen && (
          <div className="relative z-50 md:hidden">
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
            <div className="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-slate-900 p-6 shadow-2xl">
              <div className="flex items-center justify-between pb-6 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="h-6 w-6 text-indigo-400" />
                  <span className="text-lg font-bold text-white">ChurnPredict AI</span>
                </div>
                <button onClick={() => setMobileMenuOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="h-6 w-6" />
                </button>
              </div>
              <nav className="flex-1 space-y-2 py-6">
                {navItems.map((item) => {
                  const isActive = pathname === item.href;
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center px-4 py-3 text-sm font-medium rounded-xl ${
                        isActive ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                      }`}
                    >
                      <Icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
              <div className="border-t border-slate-850 pt-4">
                <button
                  onClick={logout}
                  className="flex w-full items-center px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 rounded-xl"
                >
                  <LogOut className="mr-3 h-5 w-5" />
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ================================================== */}
        {/* MAIN BODY AND TOP BAR */}
        {/* ================================================== */}
        <div className="flex flex-1 flex-col md:pl-64">
          <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="text-slate-400 hover:text-white md:hidden"
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="hidden sm:block">
              <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full uppercase tracking-wider">
                Production-Grade System
              </span>
            </div>

            <div className="flex items-center gap-4">
              {/* Theme toggle */}
              <button 
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800/40"
              >
                {theme === 'dark' ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
              </button>

              <button className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800/40 relative">
                <Bell className="h-4.5 w-4.5" />
                <span className="absolute top-1 right-1 h-1.5 w-1.5 rounded-full bg-indigo-500 animate-ping" />
              </button>
            </div>
          </header>

          <main className="flex-1 p-6 md:p-8">
            <div className="mx-auto max-w-5xl space-y-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
};
