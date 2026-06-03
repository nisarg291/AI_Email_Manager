import { motion, AnimatePresence } from 'framer-motion';
import { useVideoPlayer } from '@/lib/video';
import { Scene1 } from './video_scenes/Scene1';
import { Scene2 } from './video_scenes/Scene2';
import { Scene3 } from './video_scenes/Scene3';
import { Scene4 } from './video_scenes/Scene4';
import { Scene5 } from './video_scenes/Scene5';
import { Scene6 } from './video_scenes/Scene6';

const SCENE_DURATIONS = {
  opener: 8000,
  classification: 10000,
  labels: 10000,
  reply: 10000,
  live: 10000,
  closing: 12000
};

export default function VideoTemplate() {
  const { currentScene } = useVideoPlayer({ durations: SCENE_DURATIONS });

  return (
    <div className="relative w-full h-screen overflow-hidden bg-background">
      {/* Background layer - persistent across scenes */}
      <div className="absolute inset-0 z-0">
        <video 
          src={`${import.meta.env.BASE_URL}videos/hero_bg.mp4`}
          className="w-full h-full object-cover opacity-30 mix-blend-screen"
          autoPlay loop muted playsInline
        />
        
        {/* Animated gradient overlay */}
        <motion.div 
          className="absolute inset-0 opacity-40 mix-blend-overlay"
          animate={{
            background: [
              'radial-gradient(circle at 0% 0%, #15B8F5 0%, transparent 50%)',
              'radial-gradient(circle at 100% 100%, #B845ED 0%, transparent 50%)',
              'radial-gradient(circle at 50% 50%, #15B8F5 0%, transparent 50%)',
              'radial-gradient(circle at 0% 100%, #B845ED 0%, transparent 50%)',
              'radial-gradient(circle at 100% 0%, #15B8F5 0%, transparent 50%)'
            ]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />
        
        {/* Noise texture */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-overlay" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }}></div>
      </div>

      {/* Persistent UI frame */}
      <div className="absolute top-0 left-0 w-full h-full z-10 pointer-events-none p-[4vw]">
        <div className="absolute top-[3vw] left-[3vw] flex items-center gap-[1vw]">
          <div className="w-[1.5vw] h-[1.5vw] rounded-sm bg-primary" />
          <span className="text-[1.2vw] font-display font-bold tracking-widest text-primary uppercase">AI Email Manager</span>
        </div>
        <div className="absolute top-[3vw] right-[3vw] flex gap-[0.5vw]">
          <motion.div 
            className="w-[0.5vw] h-[0.5vw] rounded-full bg-primary"
            animate={{ opacity: [1, 0.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <span className="text-[1vw] font-mono text-primary/70">SYS.ACTIVE</span>
        </div>
        <div className="absolute bottom-[3vw] right-[3vw]">
          <span className="text-[1vw] font-mono text-white/30">00:0{currentScene + 1} // 00:06</span>
        </div>
      </div>

      {/* Main Content */}
      <AnimatePresence mode="popLayout">
        {currentScene === 0 && <Scene1 key="s1" />}
        {currentScene === 1 && <Scene2 key="s2" />}
        {currentScene === 2 && <Scene3 key="s3" />}
        {currentScene === 3 && <Scene4 key="s4" />}
        {currentScene === 4 && <Scene5 key="s5" />}
        {currentScene === 5 && <Scene6 key="s6" />}
      </AnimatePresence>
    </div>
  );
}
