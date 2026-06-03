import { motion, AnimatePresence } from 'framer-motion';
import { useVideoPlayer } from '@/lib/video';
import { Scene1 } from './video_scenes/Scene1';
import { Scene2 } from './video_scenes/Scene2';
import { Scene3 } from './video_scenes/Scene3';
import { Scene4 } from './video_scenes/Scene4';
import { Scene5 } from './video_scenes/Scene5';
import { Scene6 } from './video_scenes/Scene6';

const SCENE_DURATIONS = { 
  hero: 8000, 
  classification: 12000, 
  labels: 12000, 
  reply: 12000, 
  live: 12000,
  closing: 8000 
};

export default function VideoTemplate() {
  const { currentScene } = useVideoPlayer({ durations: SCENE_DURATIONS });

  return (
    <div className="relative w-full h-screen overflow-hidden bg-slate-900 text-white font-body">
      {/* Persistent Grid Background */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none" />

      {/* Persistent Background Glows */}
      <motion.div 
        className="absolute w-[40vw] h-[40vw] rounded-full blur-[10vw] opacity-20 pointer-events-none"
        style={{ background: '#6366f1' }}
        animate={{ 
          x: ['-10vw', '50vw', '20vw'], 
          y: ['-10vh', '30vh', '60vh'],
          scale: [1, 1.2, 0.8]
        }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />
      <motion.div 
        className="absolute w-[30vw] h-[30vw] rounded-full blur-[8vw] opacity-15 pointer-events-none"
        style={{ background: '#10b981' }}
        animate={{ 
          x: ['60vw', '10vw', '80vw'], 
          y: ['50vh', '-10vh', '20vh'],
          scale: [0.8, 1.5, 1]
        }}
        transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
      />

      <AnimatePresence mode="sync">
        {currentScene === 0 && <Scene1 key="hero" />}
        {currentScene === 1 && <Scene2 key="classification" />}
        {currentScene === 2 && <Scene3 key="labels" />}
        {currentScene === 3 && <Scene4 key="reply" />}
        {currentScene === 4 && <Scene5 key="live" />}
        {currentScene === 5 && <Scene6 key="closing" />}
      </AnimatePresence>
    </div>
  );
}
