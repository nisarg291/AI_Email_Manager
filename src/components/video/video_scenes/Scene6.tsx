import { motion } from 'framer-motion';

export function Scene6() {
  return (
    <motion.div 
      className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.5 }}
    >
      <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />
      
      <motion.div
        className="flex flex-col items-center"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1], delay: 0.5 }}
      >
        <div className="w-[15vw] h-[15vw] relative mb-[4vw]">
          <img src={`${import.meta.env.BASE_URL}images/email-icon.png`} className="w-full h-full object-contain filter drop-shadow-[0_0_40px_rgba(99,102,241,0.6)]" />
        </div>
        
        <h1 className="text-[6vw] font-display font-bold text-white mb-[2vw] tracking-tight">
          AI Email Manager
        </h1>
        
        <p className="text-[2.5vw] text-indigo-400 font-medium">
          Less inbox. More focus.
        </p>
      </motion.div>

      {/* Decorative lines */}
      <motion.div 
        className="absolute bottom-[15vh] w-[1px] bg-gradient-to-t from-indigo-500 to-transparent"
        initial={{ height: 0 }}
        animate={{ height: '20vh' }}
        transition={{ duration: 1.5, delay: 2, ease: "easeOut" }}
      />
    </motion.div>
  );
}
