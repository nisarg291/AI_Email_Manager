import { motion } from 'framer-motion';

export function Scene3() {
  return (
    <motion.div 
      className="absolute inset-0 flex flex-col items-center justify-center p-[8vw]"
      initial={{ opacity: 0, y: '10vh' }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 1.1 }}
      transition={{ duration: 1 }}
    >
      <motion.div
        className="text-center mb-[6vw] w-full"
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.3 }}
      >
        <h2 className="text-[4vw] font-display font-bold">AI recommends labels for you</h2>
      </motion.div>

      <div className="flex w-full h-[60vh] gap-[4vw] items-center justify-center">
        {/* Profile Card */}
        <motion.div 
          className="w-[30vw] h-[40vw] max-h-[50vh] bg-slate-800/80 border border-slate-700 rounded-[2vw] p-[3vw] flex flex-col items-center backdrop-blur-md"
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 1, delay: 1, type: 'spring' }}
        >
          <div className="w-[8vw] h-[8vw] rounded-full bg-slate-700 mb-[2vw] overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-emerald-500 opacity-50" />
            <svg className="w-full h-full p-4 text-white/80" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div className="w-2/3 h-[2vw] bg-slate-700 rounded-full mb-[1vw]" />
          <div className="w-1/2 h-[1.5vw] bg-slate-700/50 rounded-full mb-[3vw]" />
          
          <div className="w-full flex-1 flex flex-col justify-end gap-[1vw]">
            <div className="w-full h-[6vw] bg-indigo-500/10 border border-indigo-500/30 rounded-[1vw] flex items-center justify-center relative overflow-hidden">
               <motion.div 
                  className="absolute inset-0 bg-indigo-500/20"
                  initial={{ x: '-100%' }}
                  animate={{ x: '100%' }}
                  transition={{ duration: 2, repeat: Infinity, delay: 2 }}
               />
               <span className="text-indigo-400 font-medium text-[1.2vw] relative z-10">Scanning Profile...</span>
            </div>
          </div>
        </motion.div>

        {/* Labels List */}
        <div className="flex flex-col gap-[1.5vw] w-[35vw]">
          {[
            { label: 'Critical Project Updates', tier: 'High Priority', color: 'border-red-500/50 bg-red-500/10 text-red-400' },
            { label: 'Design Assets', tier: 'Important', color: 'border-indigo-500/50 bg-indigo-500/10 text-indigo-400' },
            { label: 'Weekly Reports', tier: 'Normal', color: 'border-slate-600 bg-slate-800 text-slate-300' }
          ].map((item, i) => (
            <motion.div
              key={item.label}
              className={`w-full p-[2vw] border rounded-[1vw] flex justify-between items-center ${item.color}`}
              initial={{ x: 100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 2.5 + i * 0.8, type: 'spring' }}
            >
              <span className="text-[1.8vw] font-medium">{item.label}</span>
              <span className="text-[1.2vw] opacity-70 px-[1vw] py-[0.5vw] rounded-full bg-black/20">{item.tier}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
