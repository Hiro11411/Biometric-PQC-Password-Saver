'use client';

import { useState, useRef } from 'react';

export default function VaultPage() {
  const [passwords, setPasswords] = useState([
    { id: 1, website: 'github.com', username: 'hiro', password: 'secretpass123', visible: false },
    { id: 2, website: 'google.com', username: 'hiro@email.com', password: 'mypass456', visible: false },
  ]);

  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const [newPassword, setNewPassword] = useState({
    website: '',
    username: '',
    password: ''
  });

  // Music metadata
  const currentSong = {
    title: "Angelicide",
    artist: "Your Artist Name",
    album: "Album Name",
    coverImage: "/music/angelicide.jpg" // Add your album cover image
  };

  const toggleMusic = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const togglePasswordVisibility = (id: number) => {
    setPasswords(passwords.map(p => 
      p.id === id ? { ...p, visible: !p.visible } : p
    ));
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      setPasswords(passwords.map(p => 
        p.id === editingId ? { ...p, ...newPassword } : p
      ));
      setEditingId(null);
    } else {
      setPasswords([...passwords, { id: Date.now(), ...newPassword, visible: false }]);
    }
    setNewPassword({ website: '', username: '', password: '' });
    setShowAddForm(false);
  };

  const handleEdit = (item: any) => {
    setNewPassword({ website: item.website, username: item.username, password: item.password });
    setEditingId(item.id);
    setShowAddForm(true);
  };

  const handleDelete = (id: number) => {
    setPasswords(passwords.filter(p => p.id !== id));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAdd(e);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-300 via-rose-200 to-pink-100 pb-24">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b-2 border-pink-400 bg-white/70 backdrop-blur-md shadow-lg shadow-pink-300/30">
        <h1 className="text-2xl font-bold text-pink-600 drop-shadow-[0_0_15px_rgba(236,72,153,0.6)]">
          Enigma 
        </h1>
        <div className="flex gap-4">
          <a href="/" className="px-4 py-2 bg-white border-2 border-pink-400 rounded-lg text-pink-700 hover:bg-pink-50 hover:border-rose-500 transition font-medium">
            Home
          </a>
          <button className="px-4 py-2 bg-gradient-to-r from-pink-500 via-rose-500 to-red-500 hover:from-pink-400 hover:via-rose-400 hover:to-red-400 text-white rounded-lg transition shadow-lg shadow-rose-400/50 font-medium">
            Logout
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-4xl font-bold text-pink-600 drop-shadow-[0_0_10px_rgba(236,72,153,0.4)]">Your Passwords</h2>
          <button
            onClick={() => {
              setShowAddForm(!showAddForm);
              if (showAddForm) {
                setEditingId(null);
                setNewPassword({ website: '', username: '', password: '' });
              }
            }}
            className="px-6 py-2.5 bg-gradient-to-r from-pink-500 via-rose-500 to-red-500 text-white rounded-lg hover:from-pink-400 hover:via-rose-400 hover:to-red-400 transition font-medium shadow-xl shadow-rose-400/50"
          >
            {showAddForm ? 'Cancel' : '+ Add Password'}
          </button>
        </div>

        {/* Add/Edit Password Form */}
        {showAddForm && (
          <div className="bg-white/90 backdrop-blur-md border-2 border-rose-400 rounded-lg p-6 mb-8 shadow-2xl shadow-rose-300/60">
            <h3 className="text-xl font-bold text-rose-600 mb-4">
              {editingId ? 'Edit Password' : 'Add New Password'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-pink-700 mb-1">
                  Website
                </label>
                <input
                  type="text"
                  required
                  value={newPassword.website}
                  onChange={(e) => setNewPassword({...newPassword, website: e.target.value})}
                  className="w-full px-4 py-2.5 bg-white border-2 border-pink-300 rounded-lg focus:ring-2 focus:ring-rose-500 focus:border-rose-500 outline-none text-pink-900 placeholder-pink-400"
                  placeholder="github.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-pink-700 mb-1">
                  Username/Email
                </label>
                <input
                  type="text"
                  required
                  value={newPassword.username}
                  onChange={(e) => setNewPassword({...newPassword, username: e.target.value})}
                  className="w-full px-4 py-2.5 bg-white border-2 border-pink-300 rounded-lg focus:ring-2 focus:ring-rose-500 focus:border-rose-500 outline-none text-pink-900 placeholder-pink-400"
                  placeholder="username@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-pink-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={newPassword.password}
                  onChange={(e) => setNewPassword({...newPassword, password: e.target.value})}
                  className="w-full px-4 py-2.5 bg-white border-2 border-pink-300 rounded-lg focus:ring-2 focus:ring-rose-500 focus:border-rose-500 outline-none text-pink-900 placeholder-pink-400"
                  placeholder="••••••••"
                />
              </div>
              <button
                onClick={handleSubmit}
                className="w-full bg-gradient-to-r from-pink-500 via-rose-500 to-red-600 text-white py-2.5 rounded-lg hover:from-pink-400 hover:via-rose-400 hover:to-red-500 transition font-medium shadow-xl shadow-rose-500/60"
              >
                {editingId ? 'Update Password' : 'Save Password'}
              </button>
            </div>
          </div>
        )}

        {/* Password List */}
        <div className="space-y-4">
          {passwords.length === 0 ? (
            <div className="text-center py-12 text-pink-600 font-medium">
              No passwords saved yet. Click "Add Password" to get started.
            </div>
          ) : (
            passwords.map((item) => (
              <div
                key={item.id}
                className="bg-white/90 backdrop-blur-md border-2 border-pink-400 rounded-lg p-6 hover:border-rose-500 hover:shadow-2xl hover:shadow-rose-300/60 transition shadow-xl shadow-pink-300/50"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-bold text-pink-600">{item.website}</h3>
                      <span className="px-3 py-1 bg-gradient-to-r from-pink-500 via-rose-500 to-red-500 text-white text-xs rounded-full font-bold shadow-md shadow-rose-400/50">
                        Quantum-Secure
                      </span>
                    </div>
                    <p className="text-pink-700 text-sm mb-2 font-medium">
                      Username: <span className="text-pink-600">{item.username}</span>
                    </p>
                    <div className="flex items-center gap-2">
                      <p className="text-pink-700 text-sm font-medium">
                        Password: <span className="text-pink-600">{item.visible ? item.password : '••••••••'}</span>
                      </p>
                      <button
                        onClick={() => togglePasswordVisibility(item.id)}
                        className="text-rose-500 hover:text-rose-600 transition"
                      >
                        {item.visible ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => navigator.clipboard.writeText(item.password)}
                      className="px-3 py-1.5 bg-pink-500 hover:bg-pink-600 text-white rounded transition text-sm font-medium shadow-md shadow-pink-400/40"
                    >
                      Copy
                    </button>
                    <button
                      onClick={() => handleEdit(item)}
                      className="px-3 py-1.5 bg-rose-500 hover:bg-rose-600 text-white rounded transition text-sm font-medium shadow-md shadow-rose-400/40"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded transition text-sm font-medium shadow-md shadow-red-500/40"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Spotify-Style Music Player - Bottom */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-pink-600 via-rose-600 to-red-600 border-t-2 border-pink-400 shadow-2xl shadow-pink-500/50">
        <audio ref={audioRef} loop>
          <source src="/music/angelicide.mp3" type="audio/mpeg" />
        </audio>
        
        <div className="max-w-screen-2xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            {/* Left: Album Art + Song Info */}
            <div className="flex items-center gap-4 flex-1 min-w-0">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-300 to-rose-400 rounded-md shadow-lg flex-shrink-0 overflow-hidden flex items-center justify-center">
                <span className="text-white text-2xl">🎵</span>
              </div>
              <div className="min-w-0">
                <p className="text-white font-semibold text-sm truncate">{currentSong.title}</p>
                <p className="text-pink-200 text-xs truncate">{currentSong.artist}</p>
              </div>
            </div>

            {/* Center: Playback Controls */}
            <div className="flex items-center gap-4">
              <button
                onClick={toggleMusic}
                className="w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? (
                  <svg className="w-5 h-5 text-pink-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-pink-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            </div>

            {/* Right: Additional Info */}
            <div className="flex items-center gap-2 flex-1 justify-end">
              <span className="text-pink-200 text-xs hidden sm:block">The Theme is inspired by this song</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}