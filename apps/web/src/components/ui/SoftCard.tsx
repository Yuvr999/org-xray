import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cardHoverVariants } from '@/lib/motion-config';

interface SoftCardProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

export const SoftCard: React.FC<SoftCardProps> = ({
  children,
  className = '',
  hoverEffect = true,
  ...props
}) => {
  return (
    <motion.div
      variants={hoverEffect ? cardHoverVariants : undefined}
      initial="initial"
      whileHover={hoverEffect ? 'hover' : undefined}
      whileTap={hoverEffect ? 'tap' : undefined}
      className={`glass-card rounded-2xl p-5 transition-colors duration-200 ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};
