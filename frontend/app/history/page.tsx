'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { predictionService, HistoryRecord } from '@/services/prediction.service';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { 
  History, 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  BrainCircuit, 
  AlertTriangle, 
  CheckCircle2,
  Trash2
} from 'lucide-react';

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [filteredRecords, setFilteredRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Search & Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [contractFilter, setContractFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');

  // Pagination States
  const [currentPage, setCurrentPage] = useState(1);
  const recordsPerPage = 5;

  useEffect(() => {
    const fetchHistoryData = async () => {
      try {
        const historyData = await predictionService.getHistory();
        
        // If history database is empty, load a mock professional history database
        // so the user can immediately experience search, filtering, and pagination.
        if (historyData.length === 0) {
          const mockHistory: HistoryRecord[] = [
            { id: '1', timestamp: new Date(Date.now() - 3600000 * 2).toISOString(), tenure: 5, MonthlyCharges: 85.3, TotalCharges: 426.5, gender: 'Female', Contract: 'Month-to-month', churn_prediction: 1 },
            { id: '2', timestamp: new Date(Date.now() - 3600000 * 5).toISOString(), tenure: 62, MonthlyCharges: 25.1, TotalCharges: 1556.2, gender: 'Male', Contract: 'Two year', churn_prediction: 0 },
            { id: '3', timestamp: new Date(Date.now() - 3600000 * 24).toISOString(), tenure: 14, MonthlyCharges: 70.2, TotalCharges: 982.8, gender: 'Female', Contract: 'Month-to-month', churn_prediction: 0 },
            { id: '4', timestamp: new Date(Date.now() - 3600000 * 28).toISOString(), tenure: 1, MonthlyCharges: 104.9, TotalCharges: 104.9, gender: 'Male', Contract: 'Month-to-month', churn_prediction: 1 },
            { id: '5', timestamp: new Date(Date.now() - 3600000 * 48).toISOString(), tenure: 36, MonthlyCharges: 95.6, TotalCharges: 3441.6, gender: 'Female', Contract: 'One year', churn_prediction: 0 },
            { id: '6', timestamp: new Date(Date.now() - 3600000 * 72).toISOString(), tenure: 45, MonthlyCharges: 80.4, TotalCharges: 3618.0, gender: 'Male', Contract: 'One year', churn_prediction: 0 },
            { id: '7', timestamp: new Date(Date.now() - 3600000 * 96).toISOString(), tenure: 8, MonthlyCharges: 110.2, TotalCharges: 881.6, gender: 'Female', Contract: 'Month-to-month', churn_prediction: 1 },
          ];
          setRecords(mockHistory);
          setFilteredRecords(mockHistory);
        } else {
          setRecords(historyData);
          setFilteredRecords(historyData);
        }
      } catch (err) {
        console.error('Failed to fetch history list', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistoryData();
  }, []);

  // Handle Search & Filter logic
  useEffect(() => {
    let result = records;

    // Search query: filters by Monthly or Total Charges matching value
    if (searchQuery) {
      result = result.filter(rec => 
        rec.MonthlyCharges.toString().includes(searchQuery) ||
        rec.TotalCharges.toString().includes(searchQuery) ||
        rec.Contract.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by Contract Type
    if (contractFilter !== 'All') {
      result = result.filter(rec => rec.Contract === contractFilter);
    }

    // Filter by Churn Risk
    if (riskFilter !== 'All') {
      const targetPrediction = riskFilter === 'High' ? 1 : 0;
      result = result.filter(rec => rec.churn_prediction === targetPrediction);
    }

    setFilteredRecords(result);
    setCurrentPage(1); // Reset page on filter changes
  }, [searchQuery, contractFilter, riskFilter, records]);

  // Pagination calculation
  const indexOfLastRecord = currentPage * recordsPerPage;
  const indexOfFirstRecord = indexOfLastRecord - recordsPerPage;
  const currentRecords = filteredRecords.slice(indexOfFirstRecord, indexOfLastRecord);
  const totalPages = Math.ceil(filteredRecords.length / recordsPerPage);

  const formatDate = (isoStr: string) => {
    const d = new Date(isoStr);
    return d.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded bg-slate-800"></div>
        <Card className="border-slate-800 bg-slate-900/30 p-6 animate-pulse">
          <div className="h-10 w-full rounded bg-slate-850 mb-4"></div>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 w-full rounded bg-slate-900"></div>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Prediction History</h1>
          <p className="text-slate-400 mt-1">Audit log of all processed churn assessments</p>
        </div>
        {records.length > 0 && (
          <button 
            onClick={() => {
              setRecords([]);
              setFilteredRecords([]);
            }}
            className="flex items-center justify-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-2.5 text-sm font-semibold text-red-400 hover:bg-red-500/10 transition-all"
          >
            <Trash2 className="h-4.5 w-4.5" />
            Clear Log
          </button>
        )}
      </div>

      {records.length === 0 ? (
        <Card className="border-slate-850 bg-slate-900/10 p-12 border-dashed flex flex-col items-center justify-center text-center shadow-xl">
          <History className="h-12 w-12 text-slate-800 mb-4 animate-pulse" />
          <h3 className="text-lg font-bold text-slate-300">No predictions logged yet</h3>
          <p className="text-sm text-slate-500 max-w-sm mt-1.5">
            Run your first churn model assessment to view your logged predictions history database.
          </p>
          <Link href="/prediction" className="mt-6">
            <button className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 transition-all">
              <BrainCircuit className="h-4.5 w-4.5" />
              Assess Customer Now
            </button>
          </Link>
        </Card>
      ) : (
        <Card className="border-slate-800 bg-slate-900/30 shadow-xl backdrop-blur-sm">
          <CardHeader className="border-b border-slate-850 pb-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle className="text-slate-100 flex items-center gap-2">
                  <History className="h-5 w-5 text-indigo-400" />
                  Audit Trail
                </CardTitle>
                <CardDescription className="text-slate-400 mt-1">
                  Showing {filteredRecords.length} records in database
                </CardDescription>
              </div>
              
              {/* Search & Filters */}
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1 min-w-[200px]">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-600" />
                  <Input 
                    placeholder="Search charges/contract..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 border-slate-800 bg-slate-950 text-white placeholder:text-slate-600 focus-visible:ring-indigo-500"
                  />
                </div>

                <div className="flex gap-2">
                  {/* Contract filter */}
                  <select
                    value={contractFilter}
                    onChange={(e) => setContractFilter(e.target.value)}
                    className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="All">All Contracts</option>
                    <option value="Month-to-month">Month-to-month</option>
                    <option value="One year">One year</option>
                    <option value="Two year">Two year</option>
                  </select>

                  {/* Churn Risk filter */}
                  <select
                    value={riskFilter}
                    onChange={(e) => setRiskFilter(e.target.value)}
                    className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="All">All Risks</option>
                    <option value="High">High Risk</option>
                    <option value="Low">Low Risk</option>
                  </select>
                </div>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-850 text-slate-500 text-xs uppercase tracking-wider bg-slate-900/10">
                    <th className="px-6 py-4 font-semibold">Date Assessed</th>
                    <th className="px-6 py-4 font-semibold">Contract</th>
                    <th className="px-6 py-4 font-semibold text-center">Tenure</th>
                    <th className="px-6 py-4 font-semibold text-right">Monthly Bill</th>
                    <th className="px-6 py-4 font-semibold text-right">Total Billing</th>
                    <th className="px-6 py-4 font-semibold text-center">Churn Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850 text-slate-350 text-sm">
                  {currentRecords.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                        No records matched your search parameters.
                      </td>
                    </tr>
                  ) : (
                    currentRecords.map((record) => (
                      <tr key={record.id} className="hover:bg-slate-800/10 transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-300 whitespace-nowrap">
                          {formatDate(record.timestamp)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">{record.Contract}</td>
                        <td className="px-6 py-4 text-center">{record.tenure}m</td>
                        <td className="px-6 py-4 text-right">${record.MonthlyCharges.toFixed(2)}</td>
                        <td className="px-6 py-4 text-right">${record.TotalCharges.toFixed(2)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex justify-center">
                            {record.churn_prediction === 1 ? (
                              <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/20 bg-red-500/5 px-2.5 py-0.5 text-xs font-semibold text-red-400">
                                <AlertTriangle className="h-3 w-3" />
                                High (1)
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 px-2.5 py-0.5 text-xs font-semibold text-emerald-400">
                                <CheckCircle2 className="h-3 w-3" />
                                Low (0)
                              </span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-slate-850 px-6 py-4">
                <span className="text-xs text-slate-500">
                  Showing page <b>{currentPage}</b> of <b>{totalPages}</b>
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="flex items-center justify-center h-8 w-8 rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:bg-slate-800/40 hover:text-white disabled:opacity-40 disabled:hover:bg-slate-950"
                  >
                    <ChevronLeft className="h-4.5 w-4.5" />
                  </button>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="flex items-center justify-center h-8 w-8 rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:bg-slate-800/40 hover:text-white disabled:opacity-40 disabled:hover:bg-slate-950"
                  >
                    <ChevronRight className="h-4.5 w-4.5" />
                  </button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
