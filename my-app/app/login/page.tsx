'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('username', username);
    localStorage.setItem('email', email);
    setSubmitted(true);
    console.log('username', username);
    console.log('email', email);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-teal-950 via-emerald-950 to-black">
      <div className="max-w-md w-full bg-teal-950/80 backdrop-blur-sm rounded-lg shadow-2xl shadow-teal-500/30 border border-teal-700/50 p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-teal-400 drop-shadow-[0_0_15px_rgba(20,184,166,0.8)]">
          Login
        </h2>
        
        {submitted && (
          <div className="mb-4 p-3 bg-teal-900/50 border border-teal-500 text-teal-300 rounded-lg shadow-[0_0_10px_rgba(20,184,166,0.3)]">
            Welcome, {username}! 🌊
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-teal-300 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 bg-teal-950/70 border border-teal-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-400 text-teal-100 placeholder-teal-800 transition shadow-inner"
              placeholder="Enter your name"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-teal-300 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 bg-teal-950/70 border border-teal-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-400 text-teal-100 placeholder-teal-800 transition shadow-inner"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-teal-300 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-teal-950/70 border border-teal-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-400 text-teal-100 placeholder-teal-800 transition shadow-inner"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-teal-600 to-emerald-600 text-white py-2.5 px-4 rounded-lg hover:from-teal-500 hover:to-emerald-500 transition font-medium shadow-lg shadow-teal-500/40"
          >
            Sign In
          </button>
        </form>

        <p className="text-center text-sm text-teal-400 mt-6">
          Don't have an account?{' '}
          <Link href="/signup" className="text-teal-300 hover:text-teal-200 hover:underline font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}