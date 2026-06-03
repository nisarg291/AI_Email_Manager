import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene4() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 500),
      setTimeout(() => setPhase(2), 2000),
      setTimeout(() => setPhase(3), 4000),
      setTimeout(() => setPhase(4), 6000),
      setTimeout(() => setPhase(5), 9000),
    ];
    return () => timers.forEach(t => clearTimeout(t));
  }, []);

  const textToType = "Sure, I can meet on Thursday at 2 PM PST. Let me know if that works for you.";

  return (
    <motion.div 
      className="absolute inset-0 z-20 flex flex-col items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.2, filter: 'blur(10px)' }}
      transition={{ duration: 1 }}
    >
      <div className="w-[70vw] text-center mb-[4vw]">
        <motion.h2 
          className="text-[4vw] font-display font-bold text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Drafting replies, <span className="text-primary italic">done.</span>
        </motion.h2>
      </div>

      <motion.div 
        className="w-[60vw] bg-white/5 border border-white/10 rounded-[1vw] p-[2vw] backdrop-blur-lg relative"
        initial={{ y: 50, opacity: 0 }}
        animate={phase >= 1 ? { y: 0, opacity: 1 } : { y: 50, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      >
        <div className="flex items-center gap-[1vw] mb-[2vw] border-b border-white/10 pb-[1vw]">
          <div className="w-[3vw] h-[3vw] bg-accent/30 rounded-full flex items-center justify-center text-accent">AI</div>
          <div>
            <div className="text-[1vw] font-medium text-white/50">Auto-Drafting Reply</div>
          </div>
        </div>

        <div className="text-[1.5vw] text-white/90 min-h-[5vw] font-mono">
          {textToType.split('').map((char, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0 }}
              animate={phase >= 2 ? { opacity: 1 } : { opacity: 0 }}
              transition={{ delay: index * 0.05, duration: 0.1 }}
            >
              {char}
            </motion.span>
          ))}
          <motion.span 
            className="inline-block w-[0.8vw] h-[1.5vw] bg-primary ml-[0.5vw]"
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 0.8, repeat: Infinity }}
          />
        </div>

        <motion.div 
          className="mt-[2vw] inline-block px-[2vw] py-[1vw] bg-primary text-primary-foreground font-bold rounded-full text-[1vw]"
          initial={{ scale: 0, opacity: 0 }}
          animate={phase >= 4 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
          transition={{ type: 'spring', damping: 15, stiffness: 200 }}
        >
          Send
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
