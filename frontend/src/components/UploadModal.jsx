import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, UploadCloud, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function UploadModal({ onClose, onSuccess, userId }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [errorMsg, setErrorMsg] = useState('');

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'X-User-Id': userId
        }
      });
      if (res.data.error) {
        throw new Error(res.data.error);
      }
      setStatus('success');
      onSuccess();
      setTimeout(onClose, 1500);
    } catch (err) {
      setStatus('error');
      setErrorMsg(err.message || "Failed to upload file");
    }
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm"
      >
        <motion.div 
          initial={{ scale: 0.95, y: 20 }} 
          animate={{ scale: 1, y: 0 }} 
          exit={{ scale: 0.95, y: 20 }}
          className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl"
        >
          <div className="flex justify-between items-center p-6 border-b border-slate-800">
            <h2 className="text-xl font-semibold text-slate-100">Upload Document</h2>
            <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6">
            {status === 'idle' || status === 'error' ? (
              <div 
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors
                  ${file ? 'border-blue-500 bg-blue-500/5' : 'border-slate-700 hover:border-slate-500 bg-slate-900'}`}
              >
                <input 
                  type="file" 
                  accept=".pdf"
                  id="file-upload" 
                  className="hidden"
                  onChange={(e) => setFile(e.target.files[0])}
                />
                <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                  <div className={`p-4 rounded-full mb-4 ${file ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-400'}`}>
                    {file ? <FileText className="w-8 h-8" /> : <UploadCloud className="w-8 h-8" />}
                  </div>
                  <h3 className="text-lg font-medium text-slate-200 mb-1">
                    {file ? file.name : "Click or drag file to upload"}
                  </h3>
                  <p className="text-sm text-slate-500">
                    {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "PDF documents up to 50MB"}
                  </p>
                </label>
              </div>
            ) : status === 'uploading' ? (
              <div className="py-12 flex flex-col items-center justify-center">
                <Loader2 className="w-10 h-10 text-blue-500 animate-spin mb-4" />
                <h3 className="text-lg font-medium text-slate-200">Processing Document...</h3>
                <p className="text-sm text-slate-500 text-center mt-2">
                  Extracting text, generating embeddings, <br/>and saving to vector database.
                </p>
              </div>
            ) : (
              <div className="py-12 flex flex-col items-center justify-center">
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="text-green-500 mb-4">
                  <CheckCircle2 className="w-12 h-12" />
                </motion.div>
                <h3 className="text-lg font-medium text-slate-200">Upload Complete!</h3>
                <p className="text-sm text-slate-500 mt-2">Knowledge base updated.</p>
              </div>
            )}

            {status === 'error' && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm text-center">
                {errorMsg}
              </div>
            )}

            {file && (status === 'idle' || status === 'error') && (
              <button 
                onClick={handleUpload}
                className="w-full mt-6 py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-colors"
              >
                Upload & Process
              </button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
