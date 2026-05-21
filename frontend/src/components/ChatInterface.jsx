import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, Sparkles, ChevronDown, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

export default function ChatInterface({ user }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Hello! I am SynapseAI. Upload a document using the sidebar, and I'll help you understand it, create summaries, and answer your questions."
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!user) return;
    const fetchHistory = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/chat/history?session_id=default', {
          headers: { 'X-User-Id': user.id }
        });
        if (res.data && res.data.length > 0) {
          const loadedMessages = [
            {
              id: 1,
              role: 'assistant',
              content: "Hello! I am SynapseAI. Upload a document using the sidebar, and I'll help you understand it, create summaries, and answer your questions."
            }
          ];
          res.data.forEach(item => {
            loadedMessages.push({
              id: `${item.id}_user`,
              role: 'user',
              content: item.message
            });
            loadedMessages.push({
              id: `${item.id}_assistant`,
              role: 'assistant',
              content: item.response
            });
          });
          setMessages(loadedMessages);
        } else {
          setMessages([
            {
              id: 1,
              role: 'assistant',
              content: "Hello! I am SynapseAI. Upload a document using the sidebar, and I'll help you understand it, create summaries, and answer your questions."
            }
          ]);
        }
      } catch (err) {
        console.error("Failed to load chat history:", err);
      }
    };
    fetchHistory();
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/api/chat', {
        query: userMessage.content,
        session_id: 'default'
      }, {
        headers: { 'X-User-Id': user?.id }
      });

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: "Sorry, I encountered an error communicating with the backend. Please check if the server is running."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 relative">
      {/* Background Decor */}
      <div className="absolute top-0 inset-x-0 h-64 bg-gradient-to-b from-blue-900/10 to-transparent pointer-events-none" />
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 z-0">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div 
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex max-w-4xl mx-auto gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
                ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gradient-to-br from-indigo-500 to-purple-600'}`}
              >
                {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Sparkles className="w-4 h-4 text-white" />}
              </div>
              
              <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
                <div className={`px-5 py-3.5 rounded-2xl leading-relaxed text-[15px] shadow-sm
                  ${msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-tr-none' 
                    : 'bg-slate-800 text-slate-200 border border-slate-700/50 rounded-tl-none'}`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>

                {/* Sources Section */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 w-full">
                    <details className="group">
                      <summary className="flex items-center gap-1.5 text-xs font-medium text-slate-400 cursor-pointer hover:text-slate-300 transition-colors list-none">
                        <BookOpen className="w-3.5 h-3.5" />
                        View Sources ({msg.sources.length})
                        <ChevronDown className="w-3.5 h-3.5 group-open:rotate-180 transition-transform" />
                      </summary>
                      <div className="mt-2 space-y-2 pl-2 border-l-2 border-slate-700">
                        {msg.sources.map((src, i) => (
                          <div key={i} className="bg-slate-800/50 p-2.5 rounded-lg text-xs text-slate-400">
                            {src.substring(0, 150)}...
                          </div>
                        ))}
                      </div>
                    </details>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex max-w-4xl mx-auto gap-4 flex-row"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="px-5 py-4 rounded-2xl bg-slate-800 border border-slate-700/50 rounded-tl-none flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                <span className="text-sm text-slate-400 animate-pulse">Researching...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} className="h-4" />
      </div>

      {/* Input Form */}
      <div className="p-4 sm:p-6 bg-slate-900 border-t border-slate-800 z-10 relative">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="w-full bg-slate-800 border-2 border-slate-700 rounded-2xl py-4 pl-6 pr-14 
                     text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-slate-800/80
                     transition-all shadow-sm group-hover:border-slate-600"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2.5 top-2.5 bottom-2.5 px-3 bg-blue-600 hover:bg-blue-500 
                     disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-xl 
                     transition-colors flex items-center justify-center shadow-sm"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
        <p className="text-center text-xs text-slate-500 mt-3 font-medium">
          SynapseAI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
