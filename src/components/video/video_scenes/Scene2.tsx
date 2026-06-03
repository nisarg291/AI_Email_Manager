import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function Scene2() {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 800),
      setTimeout(() => setPhase(2), 2000),
      setTimeout(() => setPhase(3), 3500),
      setTimeout(() => setPhase(4), 5000),
      setTimeout(() => setPhase(5), 9000),
    ];
    return () => timers.forEach(t => clearTimeout(t));
  }, []);

  const emails = [
    { title: "Invoice from Stripe", type: "Billing", color: "text-blue-400" },
    { title: "Urgent: Project Update", type: "Work", color: "text-red-400" },
    { title: "Weekly Newsletter", type: "Read Later", color: "text-green-400" }
  ];

  return (
    <motion.div 
      className="absolute inset-0 z-20 flex items-center justify-center"
      initial={{ opacity: 0, x: '10vw' }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: '-10vw', filter: 'blur(10px)' }}
      transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="w-[85vw] flex items-center justify-between">
        <div className="w-[45vw]">
          <motion.h2 
            className="text-[4.5vw] font-display font-bold leading-tight mb-[2vw]"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            AI Email <br />
            <span className="text-primary">Classification</span>
          </motion.h2>
          <motion.p 
            className="text-[1.5vw] text-white/70"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            GPT-4o-mini instantly categorizes incoming mail with superhuman accuracy.
          </motion.p>
        </div>

        <div className="w-[35vw] relative">
          <motion.div 
            className="absolute inset-0 bg-accent/20 blur-[80px] rounded-full"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 4, repeat: Infinity }}
          />
          
          <div className="relative z-10 flex flex-col gap-[1.5vw]">
            {emails.map((email, i) => (
              <motion.div 
                key={i}
                className="bg-secondary/80 backdrop-blur-md border border-white/10 p-[1.5vw] rounded-[1vw] flex justify-between items-center"
                initial={{ opacity: 0, x: 50 }}
                animate={phase >= i + 1 ? { opacity: 1, x: 0 } : { opacity: 0, x: 50 }}
                transition={{ type: 'spring', damping: 20, stiffness: 100 }}
              >
                <div className="text-[1.2vw] font-medium">{email.title}</div>
                <motion.div 
                  className={`text-[1vw] font-mono border border-white/20 px-[1vw] py-[0.5vw] rounded-full ${email.color}`}
                  initial={{ scale: 0 }}
                  animate={phase >= i + 2 ? { scale: 1 } : { scale: 0 }}
                  transition={{ type: 'spring', damping: 15, stiffness: 200 }}
                >
                  {email.type}
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
