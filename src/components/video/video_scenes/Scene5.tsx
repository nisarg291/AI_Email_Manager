import { motion } from 'framer-motion';

export function Scene5() {
  return (
    <motion.div 
      className="absolute inset-0 flex flex-col items-center justify-center p-[8vw]"
      initial={{ opacity: 0, rotateX: -20, y: '20vh' }}
      animate={{ opacity: 1, rotateX: 0, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 1 }}
      style={{ perspective: 1000 }}
    >
      <div className="text-center mb-[8vw]">
        <motion.h2 
          className="text-[4.5vw] font-display font-bold"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          Classifies new emails every minute
        </motion.h2>
      </div>

      {/* Live Pulse UI */}
      <motion.div 
        className="w-[60vw] h-[30vh] bg-[#1e293b] border border-slate-700 rounded-[2vw] relative overflow-hidden flex flex-col items-center justify-center shadow-[0_0_50px_rgba(0,0,0,0.5)]"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, delay: 1, type: 'spring' }}
      >
        {/* Pulse rings */}
        <motion.div 
          className="absolute w-[20vw] h-[20vw] rounded-full border border-indigo-500/50"
          animate={{ scale: [1, 3], opacity: [0.8, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeOut" }}
        />
        <motion.div 
          className="absolute w-[20vw] h-[20vw] rounded-full border border-indigo-500/30"
          animate={{ scale: [1, 3], opacity: [0.8, 0] }}
          transition={{ duration: 3, delay: 1.5, repeat: Infinity, ease: "easeOut" }}
        />

        <div className="relative z-10 flex flex-col items-center">
          <div className="text-[2vw] text-indigo-400 font-medium mb-[2vw] flex items-center gap-[1vw]">
            <span className="w-[1vw] h-[1vw] rounded-full bg-indigo-500 animate-pulse" />
            Live Processing Active
          </div>
          
          {/* Progress Bar */}
          <div className="w-[40vw] h-[1vw] bg-slate-800 rounded-full overflow-hidden mb-[3vw] relative">
            <motion.div 
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-indigo-500 to-emerald-500"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
            />
          </div>

          <div className="px-[3vw] py-[1vw] border border-red-500/30 bg-red-500/10 text-red-400 rounded-full text-[1.5vw] font-medium backdrop-blur-sm">
            Stop Classification
          </div>
        </div>
      </motion.div>

      {/* Privacy Callout */}
      <motion.div
        className="mt-[6vw] text-center w-[50vw]"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 2.5 }}
      >
        <div className="inline-flex items-center justify-center p-[2vw] bg-slate-800/50 border border-slate-700 rounded-[1.5vw] backdrop-blur-md">
          <svg className="w-[3vw] h-[3vw] text-emerald-400 mr-[1.5vw]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <p className="text-[1.6vw] text-slate-300 leading-snug">
            <strong className="text-emerald-400">Privacy First.</strong> Only sender + subject sent to AI.<br/>Never your full email.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
