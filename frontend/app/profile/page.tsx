'use client';

import React from 'react';
import { useAuth } from '@/context/auth-context';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { 
  UserCircle, 
  Mail, 
  Shield, 
  CreditCard, 
  Calendar, 
  LogOut,
  Settings,
  Database
} from 'lucide-react';

export default function ProfilePage() {
  const { user, logout } = useAuth();

  // Handle fallback values if auth context has empty values in local dev sandbox
  const currentUser = user || {
    name: 'Administrator',
    email: 'admin@churnpredict.ai',
    role: 'ML Architect'
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">User Profile</h1>
        <p className="text-slate-400 mt-1">Manage your platform account credentials and subscriptions</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* User Card */}
        <Card className="md:col-span-1 border-slate-800 bg-slate-900/30 shadow-xl backdrop-blur-sm flex flex-col items-center p-6 text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-4">
            <UserCircle className="h-12 w-12" />
          </div>
          <h2 className="text-xl font-bold text-white">{currentUser.name}</h2>
          <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20 mt-2">
            <Shield className="h-3 w-3" />
            {currentUser.role || 'Data Scientist'}
          </span>

          <div className="w-full border-t border-slate-850 mt-6 pt-6 space-y-4 text-left">
            <div className="flex items-center gap-3 text-sm text-slate-400">
              <Mail className="h-4.5 w-4.5 text-slate-500" />
              <span className="truncate">{currentUser.email}</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-slate-400">
              <Calendar className="h-4.5 w-4.5 text-slate-500" />
              <span>Joined May 2026</span>
            </div>
          </div>

          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-red-600 hover:bg-red-500 px-4 py-2.5 text-sm font-semibold text-white transition-all shadow-lg shadow-red-600/10 mt-8"
          >
            <LogOut className="h-4.5 w-4.5" />
            Sign Out Account
          </button>
        </Card>

        {/* Subscription & Account limits card */}
        <div className="md:col-span-2 space-y-6">
          <Card className="border-slate-800 bg-slate-900/30 shadow-xl backdrop-blur-sm">
            <CardHeader className="border-b border-slate-850 pb-4">
              <CardTitle className="text-slate-100 flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-indigo-400" />
                Subscription Plan
              </CardTitle>
              <CardDescription className="text-slate-400">
                Billing cycles and prediction volume tracking
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              <div className="flex justify-between items-center bg-slate-950 p-4 rounded-xl border border-slate-850">
                <div>
                  <h3 className="text-sm font-bold text-white">Enterprise Tier (Unlimited)</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Renews automatically on June 23, 2026</p>
                </div>
                <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 rounded-full uppercase tracking-wider">
                  Active
                </span>
              </div>

              {/* Progress limit */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-semibold text-slate-400">
                  <span>Prediction Quota Usage</span>
                  <span>148 / 10,000 evaluations</span>
                </div>
                <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-850">
                  <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full" style={{ width: '1.48%' }} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Platform Settings details */}
          <Card className="border-slate-800 bg-slate-900/30 shadow-xl backdrop-blur-sm">
            <CardHeader className="border-b border-slate-850 pb-4">
              <CardTitle className="text-slate-100 flex items-center gap-2">
                <Settings className="h-5 w-5 text-indigo-400" />
                ML Platform Configurations
              </CardTitle>
              <CardDescription className="text-slate-400">
                System environments and database configurations
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="flex items-center gap-3 text-sm text-slate-400">
                <Database className="h-4.5 w-4.5 text-slate-500" />
                <div>
                  <p className="text-slate-200 font-semibold">PostgreSQL Database Connection</p>
                  <p className="text-xs text-slate-500 mt-0.5">Connected (SSL Active) &bull; Host: localhost:5432</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
