import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene1() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 500),
      setTimeout(() => setPhase(2), 2000),
      setTimeout(() => setPhase(3), 3500),
      setTimeout(() => setPhase(4), 7000),
    ];
    return () => timers.forEach(t => clearTimeout(t));
  }, []);

  return (
    <motion.div 
      className="absolute inset-0 z-20 flex flex-col items-center justify-center"
      initial={{ opacity: 0, scale: 1.1 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, filter: 'blur(20px)', scale: 0.9 }}
      transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="relative w-full max-w-[80vw] text-center">
        {/* Animated abstract shape */}
        <motion.div 
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[30vw] h-[30vw] border border-primary/20 rounded-full"
          animate={{ rotate: 360, scale: [1, 1.2, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />
        
        <div className="relative z-10">
          <motion.div className="overflow-hidden mb-[2vw]">
            <motion.h1 
              className="text-[6vw] font-display font-bold leading-tight"
              initial={{ y: '100%' }}
              animate={phase >= 1 ? { y: 0 } : { y: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
              Your Inbox.
            </motion.h1>
          </motion.div>
          
          <motion.div className="overflow-hidden">
            <motion.h1 
              className="text-[6vw] font-display font-bold leading-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent"
              initial={{ y: '100%' }}
              animate={phase >= 2 ? { y: 0 } : { y: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
              Finally under control.
            </motion.h1>
          </motion.div>

          <motion.p 
            className="mt-[3vw] text-[1.8vw] text-white/60 font-body max-w-[40vw] mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={phase >= 3 ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 1, ease: 'easeOut' }}
          >
            Powered by Django & GPT-4o-mini
          </motion.p>
        </div>
      </div>
    </motion.div>
  );
}
