import React, { useEffect, useState } from 'react';
import { Upload, MessageSquare, BookOpen, BrainCircuit } from 'lucide-react';
import UploadModal from './components/UploadModal';
import ChatInterface from './components/ChatInterface';
import AuthPage from './components/AuthPage';

function App() {
  const [user, setUser] = useState(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [documents, setDocuments] = useState([]);

  const fetchDocuments = async (userId) => {
    try {
      const res = await fetch('http://localhost:8000/api/documents', {
        headers: {
          'X-User-Id': userId
        }
      });
      const docs = await res.json();
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setDocuments([]);
    }
  };

  useEffect(() => {
    const savedUser = window.localStorage.getItem('synapse_user');
    if (savedUser) {
      const parsed = JSON.parse(savedUser);
      setUser(parsed);
      fetchDocuments(parsed.id);
    }
  }, []);

  useEffect(() => {
    if (user) {
      window.localStorage.setItem('synapse_user', JSON.stringify(user));
      fetchDocuments(user.id);
    } else {
      window.localStorage.removeItem('synapse_user');
      setDocuments([]);
    }
  }, [user]);

  const handleLogout = () => {
    setUser(null);
    setIsUploadOpen(false);
  };

  if (!user) {
    return <AuthPage onLoginSuccess={setUser} />;
  }

  return (
    <div className="min-h-screen flex bg-slate-900 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-6 flex items-center gap-3">
          <BrainCircuit className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="font-bold text-xl tracking-tight text-white">SynapseAI</h1>
            <p className="text-sm text-slate-400">Logged in as {user.username}</p>
          </div>
        </div>
        
        <nav className="flex-1 px-4 py-2 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600/10 text-blue-400 rounded-xl font-medium transition-colors">
            <MessageSquare className="w-5 h-5" />
            Research Chat
          </button>
          <button 
            onClick={() => setIsUploadOpen(true)}
            className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-xl font-medium transition-colors"
          >
            <Upload className="w-5 h-5" />
            Upload Document
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-xl font-medium transition-colors"
          >
            Logout
          </button>
        </nav>
        
        <div className="p-4 m-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-slate-800 p-2 rounded-lg">
              <BookOpen className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-300">Knowledge Base</p>
              <p className="text-xs text-slate-500">{documents.length} Documents</p>
            </div>
          </div>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {documents.length === 0 ? (
              <p className="text-xs text-slate-500">No PDFs uploaded yet.</p>
            ) : (
              documents.map((doc) => (
                <div key={doc.id} className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200">
                  <div className="font-medium truncate">{doc.filename}</div>
                  <div className="text-xs text-slate-500">{new Date(doc.upload_date).toLocaleString()}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative">
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md flex items-center px-6 sticky top-0 z-10 md:hidden">
          <BrainCircuit className="w-6 h-6 text-blue-500 mr-3" />
          <div>
            <h1 className="font-bold text-lg">SynapseAI</h1>
            <p className="text-xs text-slate-400">Logged in as {user.username}</p>
          </div>
        </header>

        <div className="flex-1 overflow-hidden relative">
          <ChatInterface user={user} />
        </div>
      </main>

      {isUploadOpen && (
        <UploadModal 
          onClose={() => setIsUploadOpen(false)} 
          onSuccess={() => fetchDocuments(user.id)} 
          userId={user.id}
        />
      )}
    </div>
  );
}

export default App;
