import React, { useState } from 'react';
import { Upload, MessageSquare, BookOpen, BrainCircuit } from 'lucide-react';
import UploadModal from './components/UploadModal';
import ChatInterface from './components/ChatInterface';

function App() {
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [pdfsUploaded, setPdfsUploaded] = useState(0);

  return (
    <div className="min-h-screen flex bg-slate-900 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-6 flex items-center gap-3">
          <BrainCircuit className="w-8 h-8 text-blue-500" />
          <h1 className="font-bold text-xl tracking-tight text-white">SynapseAI</h1>
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
        </nav>
        
        <div className="p-4 m-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
          <div className="bg-slate-800 p-2 rounded-lg">
            <BookOpen className="w-5 h-5 text-slate-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-300">Knowledge Base</p>
            <p className="text-xs text-slate-500">{pdfsUploaded} Documents</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative">
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md flex items-center px-6 sticky top-0 z-10 md:hidden">
          <BrainCircuit className="w-6 h-6 text-blue-500 mr-3" />
          <h1 className="font-bold text-lg">SynapseAI</h1>
        </header>

        <div className="flex-1 overflow-hidden relative">
          <ChatInterface />
        </div>
      </main>

      {isUploadOpen && (
        <UploadModal 
          onClose={() => setIsUploadOpen(false)} 
          onSuccess={() => setPdfsUploaded(prev => prev + 1)} 
        />
      )}
    </div>
  );
}

export default App;
