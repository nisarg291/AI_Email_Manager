import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene6() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 800),
      setTimeout(() => setPhase(2), 2500),
      setTimeout(() => setPhase(3), 4000),
      setTimeout(() => setPhase(4), 11000),
    ];
    return () => timers.forEach(t => clearTimeout(t));
  }, []);

  return (
    <motion.div 
      className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-background"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.5 }}
    >
      <motion.div 
        className="absolute inset-0 bg-primary/10"
        initial={{ scale: 0, borderRadius: '100%' }}
        animate={{ scale: 2, borderRadius: '0%' }}
        transition={{ duration: 2, ease: [0.16, 1, 0.3, 1] }}
      />
      
      <div className="relative z-10 text-center flex flex-col items-center">
        <motion.div
          className="mb-[3vw]"
          initial={{ scale: 0, rotate: -180 }}
          animate={phase >= 1 ? { scale: 1, rotate: 0 } : { scale: 0, rotate: -180 }}
          transition={{ type: 'spring', damping: 20, stiffness: 100 }}
        >
          <img 
            src={`${import.meta.env.BASE_URL}images/gmail_abstract.png`} 
            alt="Gmail Logo Abstract" 
            className="w-[10vw] h-[10vw] rounded-[2vw] border border-white/20"
          />
        </motion.div>

        <motion.h1 
          className="text-[6vw] font-display font-black tracking-tighter"
          initial={{ opacity: 0, y: 30 }}
          animate={phase >= 2 ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.8 }}
        >
          AI Email Manager
        </motion.h1>

        <motion.p
          className="text-[2vw] text-primary mt-[1vw] font-mono"
          initial={{ opacity: 0 }}
          animate={phase >= 3 ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 1 }}
        >
          github.com/yourusername/ai-email-manager
        </motion.p>
      </div>
    </motion.div>
  );
}
