import React, { useState } from 'react';
import axios from 'axios';

export default function AuthPage({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Username and password are required');
      return;
    }

    setIsLoading(true);

    try {
      if (isRegister) {
        const registerRes = await axios.post('http://localhost:8000/api/register', {
          username,
          password,
          email,
        });
        onLoginSuccess({
          id: registerRes.data.user_id,
          username: registerRes.data.username,
        });
      } else {
        const res = await axios.post('http://localhost:8000/api/login', {
          username,
          password,
        });
        onLoginSuccess({
          id: res.data.user_id,
          username: res.data.username,
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">SynapseAI</h1>
          <p className="text-slate-400 mt-2">{isRegister ? 'Create your account' : 'Sign in to continue'}</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-2">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 focus:border-blue-500 focus:outline-none"
              placeholder="Enter your username"
            />
          </div>

          {isRegister && (
            <div>
              <label className="block text-sm text-slate-400 mb-2">Email</label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 focus:border-blue-500 focus:outline-none"
                placeholder="Enter your email (optional)"
              />
            </div>
          )}

          <div>
            <label className="block text-sm text-slate-400 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 focus:border-blue-500 focus:outline-none"
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="text-sm text-red-400">{error}</div>}

          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full rounded-2xl bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? 'Processing...' : isRegister ? 'Create account' : 'Sign in'}
          </button>

          <div className="text-center text-sm text-slate-400">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
              className="font-semibold text-blue-400 hover:text-blue-300"
            >
              {isRegister ? 'Sign in' : 'Register'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
