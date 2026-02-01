//biography
import Link from 'next/link';

export default function BiographyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-800 to-slate-900">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-gray-600/30">
        <Link href="/" className="text-2xl font-bold text-white hover:text-gray-200 transition drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]">
          QuantumVault
        </Link>
        <Link 
          href="/"
          className="px-6 py-2 bg-gradient-to-r from-gray-600 to-slate-700 hover:from-gray-500 hover:to-slate-600 text-white rounded-lg transition font-medium shadow-lg shadow-white/20"
        >
          Back to Home
        </Link>
      </nav>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-20">
        <h1 className="text-5xl font-bold text-white text-center mb-12 drop-shadow-[0_0_20px_rgba(255,255,255,0.6)]">
          Meet the Creators
        </h1>

        {/* Hiro */}
        <div className="bg-gray-800/60 backdrop-blur-sm border border-gray-500/50 rounded-lg p-8 mb-8 shadow-2xl shadow-white/10">
          {/* Image */}
          <div className="flex justify-center mb-6">
            <img 
              src="/hiro.jpg" 
              alt="Hiro Okumura" 
              className="w-48 h-48 rounded-lg border-4 border-gray-400 object-cover shadow-lg shadow-white/30"
            />
          </div>
          
          <h2 className="text-3xl font-bold text-gray-200 mb-4 text-center">Hiro Okumura</h2>
          <div className="space-y-4 text-gray-300">
            <p>
              Freshman Computer Science student at Northeastern University, 
              specializing in post-quantum cryptography and biometric security systems.
            </p>
          </div>
          
          {/* Social Links */}
          <div className="flex justify-center gap-4 mt-6">
            <a 
              href="https://github.com/Hiro11411" 
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2 bg-gray-700/50 border border-gray-500 rounded-lg hover:border-gray-400 transition text-gray-200 hover:text-white"
            >
              GitHub
            </a>
            <a 
              href="https://linkedin.com/in/hiroaki-okumura" 
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2 bg-gray-700/50 border border-gray-500 rounded-lg hover:border-gray-400 transition text-gray-200 hover:text-white"
            >
              LinkedIn
            </a>
          </div>
        </div>

        {/* Sayer */}
        <div className="bg-gray-800/60 backdrop-blur-sm border border-gray-500/50 rounded-lg p-8 shadow-2xl shadow-white/10">
          {/* Image */}
          <div className="flex justify-center mb-6">
            <img 
              src="/sayer.jpg" 
              alt="Sayer" 
              className="w-48 h-48 rounded-lg border-4 border-gray-400 object-cover shadow-lg shadow-white/30"
            />
          </div>
          
          <h2 className="text-3xl font-bold text-gray-200 mb-4 text-center">Sayer Hashimoto</h2>
          <div className="space-y-4 text-gray-300">
            <p>
              Freshman Computer Science student at University of Michigan, specializing in Data Science/Analysis
            </p>
          </div>
          
          {/* Social Links */}
          <div className="flex justify-center gap-4 mt-6">
            <a 
              href="https://www.linkedin.com/in/sayer-hashimoto/" 
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2 bg-gray-700/50 border border-gray-500 rounded-lg hover:border-gray-400 transition text-gray-200 hover:text-white"
            >
              GitHub
            </a>
            <a 
              href="#" 
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2 bg-gray-700/50 border border-gray-500 rounded-lg hover:border-gray-400 transition text-gray-200 hover:text-white"
            >
              LinkedIn
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-600/30 py-8 text-center text-gray-400">
        <p>&copy; 2026 QuantumVault. Built for research purposes.</p>
      </footer>
    </div>
  );
}