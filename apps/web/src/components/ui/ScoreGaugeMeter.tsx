import React from 'react';
import { motion } from 'framer-motion';

interface ScoreGaugeMeterProps {
  score: number; // 0 to 100
  title?: string;
  subtitle?: string;
  size?: number;
}

export const ScoreGaugeMeter: React.FC<ScoreGaugeMeterProps> = ({
  score,
  title = 'Composite Shadow Risk',
  subtitle = 'Organization Index Score',
  size = 200,
}) => {
  const strokeWidth = 16;
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius; // Semi-circle circumference
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size / 1.6 }}>
        <svg
          width={size}
          height={size / 1.5}
          viewBox={`0 0 ${size} ${size / 1.5}`}
          className="overflow-visible"
        >
          <defs>
            <linearGradient id="gaugeGradientBlue" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#93C5FD" />
              <stop offset="50%" stopColor="#38BDF8" />
              <stop offset="80%" stopColor="#2563EB" />
              <stop offset="100%" stopColor="#1D4ED8" />
            </linearGradient>
          </defs>

          {/* Background Arc Track */}
          <path
            d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
            fill="none"
            stroke="rgba(147, 197, 253, 0.2)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Animated Progress Arc */}
          <motion.path
            d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
            fill="none"
            stroke="url(#gaugeGradientBlue)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>

        {/* Center Readout */}
        <div className="absolute bottom-1 flex flex-col items-center text-center">
          <motion.span
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="text-4xl font-extrabold tracking-tight text-slate-800 dark:text-white"
          >
            {score}%
          </motion.span>
          <span className="text-xs font-semibold text-blue-600 dark:text-sky-400">
            {score > 70 ? 'Elevated Index' : 'Nominal Health'}
          </span>
        </div>
      </div>

      <div className="mt-3 text-center">
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">{title}</h4>
        <p className="text-xs text-slate-400">{subtitle}</p>
      </div>
    </div>
  );
};
