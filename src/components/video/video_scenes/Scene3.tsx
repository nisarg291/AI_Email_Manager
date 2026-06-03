import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene3() {
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
      className="absolute inset-0 z-20 flex flex-col items-center justify-center"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.1, filter: 'blur(20px)' }}
      transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
    >
      <motion.div 
        className="w-[80vw] h-[60vh] bg-secondary/40 backdrop-blur-xl border border-white/10 rounded-[2vw] overflow-hidden flex"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <div className="w-1/2 p-[4vw] flex flex-col justify-center border-r border-white/10">
          <motion.h2 
            className="text-[3.5vw] font-display font-bold leading-tight"
            initial={{ opacity: 0, x: -20 }}
            animate={phase >= 1 ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
            transition={{ duration: 0.8 }}
          >
            Zero-Touch <br/> <span className="text-accent">Label Automation</span>
          </motion.h2>
          <motion.p 
            className="mt-[2vw] text-[1.2vw] text-white/60"
            initial={{ opacity: 0 }}
            animate={phase >= 2 ? { opacity: 1 } : { opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            Emails are automatically moved to the right folders. Your inbox stays at zero without lifting a finger.
          </motion.p>
        </div>
        
        <div className="w-1/2 relative flex items-center justify-center p-[4vw]">
          <motion.div 
            className="absolute right-0 top-0 w-[30vw] h-[30vw] bg-primary/20 blur-[100px] rounded-full"
            animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 5, repeat: Infinity }}
          />
          
          <div className="relative z-10 w-full">
            <motion.div 
              className="bg-background border border-primary/30 rounded-[1vw] p-[2vw]"
              initial={{ rotateY: 90, opacity: 0 }}
              animate={phase >= 3 ? { rotateY: 0, opacity: 1 } : { rotateY: 90, opacity: 0 }}
              transition={{ type: 'spring', damping: 20, stiffness: 100 }}
              style={{ perspective: 1000 }}
            >
              <div className="flex flex-col gap-[1vw]">
                {['Important', 'Newsletters', 'Receipts'].map((label, idx) => (
                  <div key={idx} className="flex items-center gap-[1vw] p-[1vw] bg-white/5 rounded-[0.5vw]">
                    <div className={`w-[1vw] h-[1vw] rounded-full ${idx === 0 ? 'bg-red-500' : idx === 1 ? 'bg-blue-500' : 'bg-green-500'}`} />
                    <span className="text-[1.2vw]">{label}</span>
                    <motion.div 
                      className="ml-auto text-[1vw] text-white/50"
                      initial={{ opacity: 0 }}
                      animate={phase >= 3 ? { opacity: 1 } : { opacity: 0 }}
                      transition={{ delay: 1 + (idx * 0.2) }}
                    >
                      + {Math.floor(Math.random() * 10) + 1} msgs
                    </motion.div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
