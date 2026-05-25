'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { api } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { KeyRound, ArrowLeft, Copy, Check } from 'lucide-react';

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<{ message: string; email_sent?: boolean; reset_link?: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = async (values: ForgotPasswordFormValues) => {
    setLoading(true);
    setErrorMsg(null);
    setSuccessData(null);
    try {
      const response = await api.post('/auth/forgot-password', {
        email: values.email,
      });
      setSuccessData(response.data);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to request password reset. Please try again.';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (successData?.reset_link) {
      navigator.clipboard.writeText(successData.reset_link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (successData) {
    return (
      <div className="space-y-6 animate-fadeIn">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-md">
          <KeyRound className="h-6 w-6" />
        </div>
        
        <div className="flex flex-col space-y-1.5">
          <h3 className="text-xl font-bold text-slate-100">Password Reset Request</h3>
          <p className="text-sm text-slate-400">
            {successData.email_sent 
              ? "We've sent a password reset link to your email address. Please follow the instructions to set your new password."
              : "A password reset link has been successfully generated."}
          </p>
        </div>

        {/* Show reset link in sandbox mode (when email_sent is false) */}
        {!successData.email_sent && successData.reset_link && (
          <div className="space-y-3">
            <Label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Reset Link (Sandbox Mode)</Label>
            <div className="flex items-center justify-between gap-3 bg-slate-950 border border-slate-800 rounded-xl p-3.5 pl-4 text-white font-mono text-xs shadow-inner group">
              <span className="select-all tracking-wide truncate max-w-[280px]">{successData.reset_link}</span>
              <button
                type="button"
                onClick={copyToClipboard}
                className="flex items-center justify-center h-8 w-8 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 active:scale-95 transition-all"
                title="Copy to clipboard"
              >
                {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
              </button>
            </div>
            
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-xs text-amber-300/80 leading-relaxed">
              <strong>Sandbox Notice:</strong> SMTP email servers are not fully configured. Copy the reset link above and open it in a new tab to change your password directly.
            </div>
          </div>
        )}

        {successData.email_sent && (
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-xs text-emerald-400 leading-relaxed">
            <strong>Check your inbox:</strong> The reset link was sent to your email. Click it to set your new password. Please check your spam folder if it doesn't arrive within 2 minutes.
          </div>
        )}

        <Link href="/login" className="block pt-2">
          <Button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-semibold flex items-center justify-center gap-2 rounded-xl transition-all">
            <ArrowLeft className="h-4 w-4" />
            Back to Sign In
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-1.5">
        <h3 className="text-xl font-semibold text-slate-100">Reset Password</h3>
        <p className="text-sm text-slate-400">Enter your email address to retrieve temporary access</p>
      </div>

      {errorMsg && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-400 animate-fadeIn">
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className="text-slate-300">Email Address</Label>
          <Input
            id="email"
            type="email"
            placeholder="name@company.com"
            disabled={loading}
            className="border-slate-800 bg-slate-950 text-white placeholder:text-slate-600 focus-visible:ring-indigo-500"
            {...register('email')}
          />
          {errors.email && (
            <p className="text-xs text-red-400">{errors.email.message}</p>
          )}
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 font-semibold text-white hover:from-indigo-500 hover:to-purple-500 transition-all shadow-lg shadow-indigo-600/20"
        >
          {loading ? 'Processing reset...' : 'Reset Password'}
        </Button>
      </form>

      <div className="text-center text-sm text-slate-400 pt-2">
        Remembered your credentials?{' '}
        <Link
          href="/login"
          className="font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          Sign in
        </Link>
      </div>
    </div>
  );
}
