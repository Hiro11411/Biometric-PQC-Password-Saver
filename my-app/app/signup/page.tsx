//signup
'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function SignupPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    dateOfBirth: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const allowed_CHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    
    for (let char of formData.password) {
        if (!allowed_CHAR.includes(char)) {
            alert("Password can only contain letters and numbers")
            return;
        }
    }
    console.log(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-950 via-violet-950 to-black py-12 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-purple-400 drop-shadow-[0_0_15px_rgba(192,132,252,0.8)]">Create Account</h1>
          <p className="text-purple-300 mt-2">Biometric Encryption System</p>
        </div>

        <div className="bg-purple-950/80 backdrop-blur-sm rounded-lg shadow-2xl shadow-purple-500/30 border border-purple-700/50 p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-purple-300 mb-1">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-purple-950/70 border border-purple-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-400 outline-none transition text-purple-100 placeholder-purple-800"
                placeholder="Zuick"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-purple-300 mb-1">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-purple-950/70 border border-purple-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-400 outline-none transition text-purple-100 placeholder-purple-800"
                placeholder="you@example.com"
              />
            </div>

            {/* Date of Birth */}
            <div>
              <label htmlFor="dateOfBirth" className="block text-sm font-medium text-purple-300 mb-1">
                Date of Birth
              </label>
              <input
                id="dateOfBirth"
                name="dateOfBirth"
                type="date"
                required
                value={formData.dateOfBirth}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-purple-950/70 border border-purple-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-400 outline-none transition text-purple-100"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-purple-300 mb-1">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-purple-950/70 border border-purple-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-400 outline-none transition text-purple-100 placeholder-purple-800"
                placeholder="••••••••"
              />
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-purple-300 mb-1">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-purple-950/70 border border-purple-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-400 outline-none transition text-purple-100 placeholder-purple-800"
                placeholder="••••••••"
              />
            </div>

            {/* CAPTCHA */} {/*Incomplete Finish Captcha Later*/}
            <div className="flex items-center">
              <input
                id="captcha"
                type="checkbox"
                required
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-purple-700 rounded"
              />
              <label htmlFor="captcha" className="ml-2 block text-sm text-purple-300">
                I'm not a robot
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-violet-600 text-white py-2.5 px-4 rounded-lg hover:from-purple-500 hover:to-violet-500 transition font-medium shadow-lg shadow-purple-500/40"
            >
              Create Account
            </button>
          </form>

          {/* Login Link */}
          <p className="text-center text-sm text-purple-400 mt-6">
            Already have an account?{' '}
            <Link href="/login" className="text-purple-300 hover:text-purple-200 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}