'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { predictionService, ChurnStats } from '@/services/prediction.service';
import { 
  Users, 
  AlertTriangle, 
  DollarSign, 
  Percent, 
  TrendingUp, 
  PlusCircle, 
  FileText, 
  Activity 
} from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState<ChurnStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const dashboardStats = await predictionService.getStats();
        setStats(dashboardStats);
      } catch (err) {
        console.error('Failed to load dashboard metrics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded bg-slate-800"></div>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-slate-900 border border-slate-800"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 h-96 animate-pulse rounded-2xl bg-slate-900 border border-slate-800"></div>
          <div className="h-96 animate-pulse rounded-2xl bg-slate-900 border border-slate-800"></div>
        </div>
      </div>
    );
  }

  // Fallback default statistics if database returns empty
  const activeStats = stats || {
    total_predictions: 0,
    high_risk_count: 0,
    average_monthly_charges: 0.0,
    churn_rate_percentage: 0.0,
    history: []
  };

  const kpis = [
    {
      name: 'Total Assessments',
      value: activeStats.total_predictions.toLocaleString(),
      icon: Users,
      color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
      description: 'Total customer records evaluated',
    },
    {
      name: 'High Churn Risks',
      value: activeStats.high_risk_count.toLocaleString(),
      icon: AlertTriangle,
      color: 'text-red-400 bg-red-500/10 border-red-500/20',
      description: 'Immediate action required',
    },
    {
      name: 'Avg Monthly Charge',
      value: `$${activeStats.average_monthly_charges.toFixed(2)}`,
      icon: DollarSign,
      color: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
      description: 'Average billing of assessed accounts',
    },
    {
      name: 'Aggregated Churn Rate',
      value: `${activeStats.churn_rate_percentage.toFixed(1)}%`,
      icon: Percent,
      color: 'text-pink-400 bg-pink-500/10 border-pink-500/20',
      description: 'Ratio of positive churn outcomes',
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">SaaS Analytics</h1>
          <p className="text-slate-400 mt-1">Real-time churn warnings, customer metrics, and ML monitoring</p>
        </div>
        <div>
          <Link href="/prediction">
            <button className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-indigo-500 transition-all">
              <PlusCircle className="h-4.5 w-4.5" />
              Assess Customer
            </button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div 
              key={kpi.name} 
              className="relative overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/30 p-6 shadow-xl backdrop-blur-sm hover:border-slate-700/80 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-400">{kpi.name}</span>
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl border ${kpi.color} transition-transform group-hover:scale-110 duration-300`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-3xl font-bold tracking-tight text-white">{kpi.value}</span>
                <p className="text-xs text-slate-500 mt-1.5">{kpi.description}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Dashboard Analytics & Distribution charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Churn Risk by contract card */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800/80 bg-slate-900/30 p-6 shadow-xl backdrop-blur-sm space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="text-indigo-400 h-5 w-5" />
              <h2 className="text-lg font-bold text-white">Segment Risk Breakdown</h2>
            </div>
            <span className="text-xs font-semibold text-slate-500">Based on model attributes</span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-slate-300">Month-to-month Contract</span>
                <span className="text-slate-400 font-medium">42.7% Churn rate</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-red-400 rounded-full" style={{ width: '42.7%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-slate-300">Fiber Optic Service</span>
                <span className="text-slate-400 font-medium">41.9% Churn rate</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-red-400 rounded-full" style={{ width: '41.9%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-slate-300">Electronic Check Payments</span>
                <span className="text-slate-400 font-medium">45.3% Churn rate</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-red-400 rounded-full" style={{ width: '45.3%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-slate-300">One Year Contract</span>
                <span className="text-slate-400 font-medium">11.3% Churn rate</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-amber-400 rounded-full" style={{ width: '11.3%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-slate-300">DSL Internet Service</span>
                <span className="text-slate-400 font-medium">19.0% Churn rate</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-400 rounded-full" style={{ width: '19%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* System & Model status info */}
        <div className="rounded-2xl border border-slate-800/80 bg-slate-900/30 p-6 shadow-xl backdrop-blur-sm flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800/80 pb-4">
              <Activity className="text-emerald-400 h-5 w-5" />
              <h2 className="text-lg font-bold text-white">Classifier Health</h2>
            </div>

            <div className="space-y-4 pt-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Deployed Model</span>
                <span className="text-slate-100 font-semibold bg-slate-800 px-2.5 py-0.5 rounded-lg border border-slate-700">Random Forest</span>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">ML Validation Accuracy</span>
                <span className="text-emerald-400 font-semibold">78.9%</span>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">F1 Weighted Score</span>
                <span className="text-indigo-400 font-semibold">77.6%</span>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Tracking Framework</span>
                <span className="text-slate-100 font-semibold bg-slate-800 px-2.5 py-0.5 rounded-lg border border-slate-700">MLflow v3.12</span>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-800/80 mt-6 text-center">
            <span className="text-xs text-slate-500">Pipeline logs successfully recorded under <b>logs/</b></span>
          </div>
        </div>
      </div>

      {/* Action Plan banner */}
      <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-6 shadow-xl flex items-center justify-between gap-4 flex-col sm:flex-row">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Did you check the exploratory insights?</h3>
            <p className="text-sm text-slate-400 mt-0.5">We mapped critical contract and payment method churn patterns. Open the EDA notebook to view findings.</p>
          </div>
        </div>
        <a 
          href="https://github.com/IBM/telco-customer-churn-on-icp4d" 
          target="_blank" 
          rel="noreferrer" 
          className="shrink-0 text-sm font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          View Dataset Source &rarr;
        </a>
      </div>
    </div>
  );
}
