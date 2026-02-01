//Introduction Page
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-black">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-red-900/30">
        <h1 className="text-2xl font-bold text-red-500">QuantumVault</h1>
        <Link 
          href="/login"
          className="px-6 py-2 bg-red-700 hover:bg-red-800 text-white rounded-lg transition font-medium"
        >
          Free Trial
        </Link>
      </nav>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-6xl font-bold text-red-500 mb-6 drop-shadow-[0_0_20px_rgba(220,38,38,0.5)]">
            QuantumVault
          </h2>
          <p className="text-3xl text-red-300 mb-4">
            Post-Quantum Password Manager
          </p>
          <p className="text-xl text-red-400 max-w-3xl mx-auto mb-8">
            The world's first password manager secured with quantum-resistant cryptography and biometric authentication
          </p>
          <Link 
            href="/login"
            className="inline-block px-8 py-4 bg-gradient-to-r from-red-700 to-red-900 text-white text-lg rounded-lg hover:from-red-800 hover:to-red-950 transition font-medium shadow-lg shadow-red-900/50"
          >
            Start Free Trial
          </Link>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <div className="bg-black/60 backdrop-blur-sm border border-red-900/50 rounded-lg p-6">
            <h3 className="text-xl font-bold text-red-400 mb-3">🔐 Quantum-Resistant</h3>
            <p className="text-red-300">
              Protected with Kyber-1024 lattice-based encryption that remains secure against quantum computers
            </p>
          </div>
          <div className="bg-black/60 backdrop-blur-sm border border-red-900/50 rounded-lg p-6">
            <h3 className="text-xl font-bold text-red-400 mb-3">👤 Biometric Auth</h3>
            <p className="text-red-300">
              Multi-factor authentication with face recognition and emotional analysis
            </p>
          </div>
          <div className="bg-black/60 backdrop-blur-sm border border-red-900/50 rounded-lg p-6">
            <h3 className="text-xl font-bold text-red-400 mb-3">🛡️ Zero-Knowledge</h3>
            <p className="text-red-300">
              Your passwords are encrypted locally. We never see your data.
            </p>
          </div>
        </div>

        {/* Creator Section */}
        <div className="bg-black/80 backdrop-blur-sm border border-red-900/50 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-red-500 mb-4">Created by Hiro and Sayer</h3>
          <p className="text-red-300 mb-6">
            Click the link to learn more about the creators of this website.
          </p>
  
          {/* Biography Link */}
          <Link 
            href="/biography"
            className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-red-700 to-red-900 border border-red-800 rounded-lg hover:from-red-800 hover:to-red-950 transition text-white font-medium shadow-lg shadow-red-900/50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Meet the Creators
          </Link>
        </div>
      </div> {/* ← Added this closing div for max-w-6xl */}

      {/* Footer */}
      <footer className="border-t border-red-900/30 py-8 text-center text-red-400">
        <p>&copy; 2026 QuantumVault. Built for research purposes.</p>
      </footer>
    </div>
  );
}