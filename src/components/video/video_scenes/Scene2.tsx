import { motion } from 'framer-motion';

const CATEGORIES = [
  { label: 'Job Offers', color: 'border-emerald-500 text-emerald-400 bg-emerald-500/10' },
  { label: 'Invoices', color: 'border-indigo-500 text-indigo-400 bg-indigo-500/10' },
  { label: 'Meetings', color: 'border-blue-500 text-blue-400 bg-blue-500/10' },
  { label: 'Newsletters', color: 'border-slate-500 text-slate-400 bg-slate-500/10' },
  { label: 'Spam', color: 'border-red-500 text-red-400 bg-red-500/10' }
];

export function Scene2() {
  return (
    <motion.div 
      className="absolute inset-0 flex flex-col items-center justify-center p-[8vw]"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, y: '-10vh' }}
      transition={{ duration: 1 }}
    >
      <motion.div
        className="text-center mb-[8vw]"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5 }}
      >
        <h2 className="text-[4.5vw] font-display font-bold">165 Smart Categories</h2>
        <p className="text-[2vw] text-slate-400 mt-4">Emails sorted instantly.</p>
      </motion.div>

      <div className="relative w-full h-[40vh]">
        {/* Central brain/AI hub */}
        <motion.div 
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[15vw] h-[15vw] rounded-full border border-indigo-500/30 flex items-center justify-center overflow-hidden"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1, delay: 1, type: 'spring' }}
        >
          <img src={`${import.meta.env.BASE_URL}images/neural-net.png`} className="w-full h-full object-cover opacity-60 mix-blend-screen" />
          <div className="absolute inset-0 bg-indigo-500/10 animate-pulse" />
        </motion.div>

        {/* Chips */}
        {CATEGORIES.map((cat, i) => {
          const angle = (i / CATEGORIES.length) * Math.PI * 2 - Math.PI / 2;
          const radiusX = 35; // vw
          const radiusY = 20; // vh
          const destX = `calc(50vw + ${Math.cos(angle) * radiusX}vw - 50%)`;
          const destY = `calc(50vh + ${Math.sin(angle) * radiusY}vh - 50%)`;

          return (
            <motion.div
              key={cat.label}
              className={`absolute top-0 left-0 px-[2vw] py-[1vw] rounded-full border ${cat.color} text-[1.5vw] font-medium whitespace-nowrap`}
              initial={{ 
                x: '50vw', 
                y: '50vh',
                scale: 0,
                opacity: 0,
                translateX: '-50%',
                translateY: '-50%'
              }}
              animate={{ 
                x: destX,
                y: destY,
                scale: 1,
                opacity: 1
              }}
              transition={{ 
                duration: 1.5, 
                delay: 2 + i * 0.4,
                type: 'spring',
                bounce: 0.4
              }}
            >
              {cat.label}
            </motion.div>
          );
        })}

        {/* Floating emails moving to chips */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={`email-${i}`}
            className="absolute top-0 left-0 w-[2vw] h-[1.5vw] bg-white/20 rounded-sm"
            initial={{ 
              x: '50vw', 
              y: '50vh',
              scale: 0,
              opacity: 0,
              translateX: '-50%',
              translateY: '-50%'
            }}
            animate={{ 
              x: `calc(50vw + ${Math.cos((i % 5) / 5 * Math.PI * 2 - Math.PI/2) * 35}vw - 50%)`,
              y: `calc(50vh + ${Math.sin((i % 5) / 5 * Math.PI * 2 - Math.PI/2) * 20}vh - 50%)`,
              scale: 0.5,
              opacity: [0, 1, 0]
            }}
            transition={{ 
              duration: 1.5, 
              delay: 3 + i * 0.5,
              ease: "circOut"
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}
