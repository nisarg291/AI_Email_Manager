import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene5() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 500),
      setTimeout(() => setPhase(2), 1500),
      setTimeout(() => setPhase(3), 3000),
      setTimeout(() => setPhase(4), 9000),
    ];
    return () => timers.forEach(t => clearTimeout(t));
  }, []);

  return (
    <motion.div 
      className="absolute inset-0 z-20 flex items-center justify-center"
      initial={{ opacity: 0, rotateX: 90 }}
      animate={{ opacity: 1, rotateX: 0 }}
      exit={{ opacity: 0, x: '-100vw' }}
      transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
      style={{ perspective: 1200 }}
    >
      <div className="w-[80vw] flex items-center justify-between">
        <div className="w-[45vw]">
          <motion.h2 
            className="text-[4vw] font-display font-bold text-white mb-[1vw]"
            initial={{ opacity: 0, x: -30 }}
            animate={phase >= 1 ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
          >
            Live Mode
          </motion.h2>
          <motion.p 
            className="text-[1.8vw] text-white/60 mb-[3vw]"
            initial={{ opacity: 0 }}
            animate={phase >= 2 ? { opacity: 1 } : { opacity: 0 }}
          >
            Running in the background. Classifying every minute.
          </motion.p>
          
          <motion.div 
            className="flex items-center gap-[1vw] text-[1.2vw] font-mono text-accent"
            initial={{ opacity: 0 }}
            animate={phase >= 3 ? { opacity: 1 } : { opacity: 0 }}
          >
            <motion.div 
              className="w-[1vw] h-[1vw] bg-accent rounded-full"
              animate={{ opacity: [1, 0.2, 1], scale: [1, 1.5, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
            SYNCING
          </motion.div>
        </div>

        <div className="w-[30vw]">
          <motion.img 
            src={`${import.meta.env.BASE_URL}images/classification.png`} 
            alt="Classification abstract"
            className="w-full h-auto rounded-[2vw] border border-white/10"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={phase >= 1 ? { scale: 1, opacity: 1 } : { scale: 0.8, opacity: 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            style={{ filter: 'drop-shadow(0 20px 40px rgba(184,69,237,0.3))' }}
          />
        </div>
      </div>
    </motion.div>
  );
}
