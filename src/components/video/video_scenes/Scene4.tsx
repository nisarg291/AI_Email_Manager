import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene4() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 1000), // Open email
      setTimeout(() => setPhase(2), 3000), // AI typing
      setTimeout(() => setPhase(3), 7000), // AI done
      setTimeout(() => setPhase(4), 8500), // Send click
      setTimeout(() => setPhase(5), 9500), // Sent state
    ];
    return () => timers.forEach(t => clearTimeout(t));
  }, []);

  return (
    <motion.div 
      className="absolute inset-0 flex flex-col items-center justify-center p-[6vw]"
      initial={{ opacity: 0, scale: 1.1 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, rotateX: 20, y: '-20vh' }}
      transition={{ duration: 1 }}
      style={{ perspective: 1000 }}
    >
      <motion.div
        className="text-center mb-[4vw]"
        initial={{ y: -30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <h2 className="text-[4vw] font-display font-bold">Draft professional replies in seconds</h2>
      </motion.div>

      {/* Mock Email Interface */}
      <motion.div 
        className="w-[70vw] h-[55vh] bg-[#1e293b] border border-slate-700 rounded-[1.5vw] shadow-2xl overflow-hidden flex flex-col"
        initial={{ rotateX: 45, y: '20vh', opacity: 0 }}
        animate={{ rotateX: 0, y: 0, opacity: 1 }}
        transition={{ duration: 1.5, type: 'spring', bounce: 0.3, delay: 0.5 }}
      >
        {/* Header */}
        <div className="h-[4vh] bg-slate-800 border-b border-slate-700 flex items-center px-[2vw] gap-[0.5vw]">
          <div className="w-[1vw] h-[1vw] rounded-full bg-red-500/80" />
          <div className="w-[1vw] h-[1vw] rounded-full bg-yellow-500/80" />
          <div className="w-[1vw] h-[1vw] rounded-full bg-emerald-500/80" />
        </div>

        {/* Content */}
        <div className="p-[3vw] flex-1 flex flex-col gap-[2vw]">
          <div className="flex gap-[1vw] items-center text-[1.5vw]">
            <span className="text-slate-400">To:</span>
            <span className="bg-slate-700 px-[1vw] py-[0.5vw] rounded-full text-slate-200">client@acme.com</span>
          </div>
          
          {/* Reply Body */}
          <div className="flex-1 bg-slate-900/50 rounded-[1vw] p-[2vw] border border-slate-700 relative overflow-hidden text-[1.8vw] leading-relaxed text-slate-300">
            {phase >= 2 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 3 }}
                  style={{ display: 'inline-block', clipPath: phase >= 3 ? 'inset(0 100% 0 0)' : 'inset(0 0 0 0)' }}
                  className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-emerald-400"
                >
                  <TypewriterText text="Hi Sarah, Thanks for reaching out. I've reviewed the proposal and it looks great. Let's proceed with the next steps." trigger={phase >= 2} />
                </motion.span>
                {phase >= 3 && (
                   <span className="text-slate-200">Hi Sarah, Thanks for reaching out. I've reviewed the proposal and it looks great. Let's proceed with the next steps.</span>
                )}
              </motion.div>
            )}
            
            {phase >= 1 && phase < 2 && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm z-10">
                <motion.div 
                  className="flex items-center gap-[1vw] text-indigo-400 text-[1.5vw] bg-indigo-500/20 px-[2vw] py-[1vw] rounded-full border border-indigo-500/50"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 1.2, opacity: 0 }}
                >
                  <svg className="w-[2vw] h-[2vw] animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" strokeDasharray="32" strokeDashoffset="16"></circle></svg>
                  AI Generating Reply...
                </motion.div>
              </div>
            )}
          </div>

          {/* Bottom Bar */}
          <div className="flex justify-between items-center h-[5vh]">
            <div className="flex gap-[1vw]">
               <div className="w-[3vw] h-[3vw] rounded bg-slate-700" />
               <div className="w-[3vw] h-[3vw] rounded bg-slate-700" />
            </div>
            
            <motion.div
              className={`px-[3vw] py-[1vw] rounded-[0.5vw] font-medium text-[1.5vw] flex items-center gap-[1vw] ${phase >= 5 ? 'bg-emerald-500 text-white' : 'bg-indigo-600 text-white'}`}
              animate={{
                scale: phase === 4 ? 0.95 : 1,
              }}
            >
              {phase >= 5 ? (
                <>
                  <svg className="w-[1.5vw] h-[1.5vw]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Sent
                </>
              ) : (
                'Send'
              )}
            </motion.div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function TypewriterText({ text, trigger }: { text: string, trigger: boolean }) {
  const [displayed, setDisplayed] = useState('');
  
  useEffect(() => {
    if (!trigger) return;
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i));
      i++;
      if (i > text.length) clearInterval(interval);
    }, 30);
    return () => clearInterval(interval);
  }, [text, trigger]);
  
  return <span>{displayed}</span>;
}
