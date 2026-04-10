import React, { useState, useEffect } from 'react';
import { analyzeSentiment, healthCheck } from './services/api';
import { 
  Send, Trash2, History, Sparkles, Smile, Frown, Meh, 
  Loader2, Activity, Zap, Compass, Wind
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast, { Toaster } from 'react-hot-toast';

function App() {
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [recentReviews, setRecentReviews] = useState([]);
  const [health, setHealth] = useState({ status: 'connecting', latency: 0 });

  // Real-time Health Polling
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await healthCheck();
        if (data) setHealth({ status: 'online', ...data });
      } catch {
        setHealth({ status: 'offline', latency: 0 });
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Hydrate from Local Storage
  useEffect(() => {
    const savedReviews = localStorage.getItem('recentReviews');
    if (savedReviews) setRecentReviews(JSON.parse(savedReviews));
  }, []);

  const handleAnalyze = async () => {
    if (!reviewText.trim()) {
      toast.error('Please enter a review');
      return;
    }
    setLoading(true);
    setResult(null); 
    
    try {
      const analysis = await analyzeSentiment(reviewText);
      setResult(analysis);
      const newReview = { 
        id: Date.now(), 
        text: reviewText, 
        ...analysis, 
        timestamp: new Date().toISOString() 
      };
      const updated = [newReview, ...recentReviews].slice(0, 6);
      setRecentReviews(updated);
      localStorage.setItem('recentReviews', JSON.stringify(updated));
    } catch (err) {
      toast.error('Network interference');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setRecentReviews([]);
    localStorage.removeItem('recentReviews');
    toast.success('History cleared');
  };

  const themes = {
    positive: { text: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100', accent: 'bg-emerald-400' },
    negative: { text: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-100', accent: 'bg-rose-400' },
    neutral: { text: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-100', accent: 'bg-slate-400' },
    none: { text: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-100', accent: 'bg-indigo-400' }
  };

  const current = themes[result?.sentiment || 'none'];

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 font-sans selection:bg-indigo-100 selection:text-indigo-700">
      <Toaster position="top-center" />

      {/* Subtle Background Aura */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <motion.div 
          animate={{ 
            x: [0, 50, 0], 
            y: [0, 30, 0],
            backgroundColor: result?.sentiment === 'positive' ? '#D1FAE5' : result?.sentiment === 'negative' ? '#FFE4E6' : '#EEF2FF'
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] rounded-full blur-[120px] opacity-40 transition-colors duration-1000"
        />
      </div>

      <nav className="sticky top-6 z-50 container mx-auto px-6 max-w-4xl">
        <div className="bg-white/70 backdrop-blur-xl border border-white/40 shadow-sm rounded-2xl px-6 py-3 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-slate-900 rounded-lg shadow-lg shadow-slate-200">
              <Wind className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-bold tracking-tight text-slate-900">Sentience.<span className="font-normal text-slate-400">io</span></span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`px-3 py-1 rounded-full border ${health.status === 'online' ? 'bg-emerald-50 border-emerald-100' : 'bg-rose-50 border-rose-100'} flex items-center gap-2`}>
              <div className={`w-1.5 h-1.5 rounded-full ${health.status === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-tighter">System {health.status}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-12 max-w-4xl relative z-10">
        <header className="text-center mb-16 space-y-4">
          <motion.h1 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight"
          >
            Sentiment <span className="text-indigo-600">Reflection</span>
          </motion.h1>
          <p className="text-slate-500 text-lg max-w-lg mx-auto leading-relaxed">
            Uncover the emotional nuances within your text with our refined neural interpreter.
          </p>
        </header>

        {/* Input Section */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-[32px] border border-slate-100 shadow-[0_20px_50px_rgba(0,0,0,0.04)] p-2 mb-12"
        >
          <div className="relative">
            <textarea
              className="w-full bg-transparent p-8 text-xl outline-none resize-none min-h-[200px] placeholder:text-slate-300 text-slate-700 leading-relaxed transition-all"
              placeholder="What are you thinking about?"
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
            />
            
            <AnimatePresence>
              {loading && (
                <motion.div 
                  initial={{ left: "-100%" }}
                  animate={{ left: "100%" }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-y-0 w-32 bg-gradient-to-r from-transparent via-white/80 to-transparent pointer-events-none z-10"
                />
              )}
            </AnimatePresence>
          </div>

          <div className="p-4 flex justify-between items-center bg-slate-50/50 rounded-[24px]">
            <button 
              onClick={() => {setReviewText(''); setResult(null);}}
              className="px-6 py-2 text-slate-400 hover:text-slate-600 font-medium transition-colors text-sm"
            >
              Clear
            </button>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="group relative flex items-center gap-2 px-8 py-3.5 bg-slate-900 hover:bg-indigo-600 text-white rounded-xl font-bold transition-all hover:shadow-xl shadow-slate-200 active:scale-95 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {loading ? "Interpreting..." : "Reveal Sentiment"}
            </button>
          </div>
        </motion.div>

        {/* Results */}
        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`p-10 rounded-[32px] border ${current.border} ${current.bg} shadow-sm mb-12`}
            >
              <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-6">
                  <div className={`p-5 rounded-2xl bg-white shadow-sm ${current.text}`}>
                    {result.sentiment === 'positive' ? <Smile size={40} strokeWidth={1.5} /> : result.sentiment === 'negative' ? <Frown size={40} strokeWidth={1.5} /> : <Meh size={40} strokeWidth={1.5} />}
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1 block">Analysis</span>
                    <h3 className={`text-4xl font-extrabold capitalize ${current.text}`}>{result.sentiment}</h3>
                  </div>
                </div>

                <div className="w-full md:w-64 space-y-3">
                  <div className="flex justify-between text-xs font-bold text-slate-500 uppercase tracking-tighter">
                    <span>Certainty Factor</span>
                    <span className={current.text}>{(result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-white rounded-full overflow-hidden p-0.5">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${result.confidence * 100}%` }}
                      className={`h-full rounded-full ${current.accent}`}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Recent Activity Grid */}
        <div className="space-y-6">
          <div className="flex justify-between items-center px-2">
            <div className="flex items-center gap-3">
              <Compass className="w-5 h-5 text-slate-300" />
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Recent Logs</h3>
            </div>
            
            {recentReviews.length > 0 && (
              <button 
                onClick={clearHistory}
                className="flex items-center gap-1.5 text-[10px] font-bold text-rose-400 hover:text-rose-600 uppercase tracking-widest transition-colors group"
              >
                <Trash2 size={12} className="group-hover:rotate-12 transition-transform" />
                Clear History
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AnimatePresence mode="popLayout">
              {recentReviews.length > 0 ? (
                recentReviews.map((rev) => (
                  <motion.div 
                    key={rev.id}
                    layout
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                    className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow group"
                  >
                    <div className="flex justify-between items-center mb-3">
                      <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-md ${themes[rev.sentiment].bg} ${themes[rev.sentiment].text}`}>
                        {rev.sentiment}
                      </span>
                      <span className="text-[10px] text-slate-300 font-medium uppercase tracking-tighter">
                        {new Date(rev.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 line-clamp-1 italic group-hover:text-slate-900 transition-colors">
                      "{rev.text}"
                    </p>
                  </motion.div>
                ))
              ) : (
                <motion.div 
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }} 
                  className="col-span-full py-12 text-center border-2 border-dashed border-slate-200 rounded-[32px] bg-slate-50/50"
                >
                  <p className="text-slate-400 text-sm font-medium italic">No recent activity discovered</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      <footer className="py-16 text-center">
        <div className="inline-flex items-center gap-2 opacity-30 grayscale hover:grayscale-0 transition-all cursor-default">
           <Activity size={14} className="text-slate-400" />
           <span className="text-[10px] font-bold text-slate-500 tracking-[0.3em] uppercase underline underline-offset-8">Designed and Developed By ❤️ Pranav Jha</span>
        </div>
      </footer>
    </div>
  );
}

export default App;