import { motion } from 'framer-motion';

export function Scene1() {
  return (
    <motion.div 
      className="absolute inset-0 flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, filter: 'blur(20px)' }}
      transition={{ duration: 1 }}
    >
      <div className="absolute inset-0 overflow-hidden opacity-40">
        <video 
          src={`${import.meta.env.BASE_URL}videos/hero-bg.mp4`}
          className="w-full h-full object-cover"
          autoPlay muted loop playsInline
        />
      </div>

      <div className="relative z-10 flex flex-col items-center text-center">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          exit={{ scale: 2, opacity: 0 }}
          transition={{ type: 'spring', damping: 20, stiffness: 100, delay: 0.5 }}
          className="w-[12vw] h-[12vw] mb-8 relative"
        >
          <img src={`${import.meta.env.BASE_URL}images/email-icon.png`} className="w-full h-full object-contain drop-shadow-[0_0_30px_rgba(99,102,241,0.5)]" />
        </motion.div>

        <div className="overflow-hidden">
          <motion.h1 
            className="text-[6vw] font-display font-bold leading-tight"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '-100%', opacity: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 1 }}
          >
            Your inbox.
          </motion.h1>
        </div>
        <div className="overflow-hidden mt-2">
          <motion.h1 
            className="text-[6vw] font-display font-bold leading-tight text-indigo-500"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '-100%', opacity: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 1.2 }}
          >
            Finally under control.
          </motion.h1>
        </div>
      </div>

      {/* Floating envelopes */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-[4vw] h-[3vw] border border-white/20 rounded-md backdrop-blur-sm flex items-center justify-center bg-white/5"
          initial={{ 
            x: `${Math.random() * 100}vw`, 
            y: '120vh',
            rotate: Math.random() * 60 - 30,
            opacity: 0
          }}
          animate={{ 
            y: '-20vh',
            rotate: Math.random() * 100 - 50,
            opacity: [0, 0.8, 0]
          }}
          transition={{ 
            duration: 5 + Math.random() * 3, 
            delay: 1.5 + Math.random() * 2,
            repeat: Infinity,
            ease: "linear"
          }}
        >
          <svg className="w-1/2 h-1/2 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </motion.div>
      ))}
    </motion.div>
  );
}
