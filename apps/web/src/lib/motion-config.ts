import { Variants } from 'framer-motion';

export const springPresets = {
  gentle: { type: 'spring' as const, stiffness: 260, damping: 25 },
  responsive: { type: 'spring' as const, stiffness: 400, damping: 30 },
  bouncy: { type: 'spring' as const, stiffness: 500, damping: 22 },
  snappy: { type: 'spring' as const, stiffness: 600, damping: 35 },
};

export const cardHoverVariants: Variants = {
  initial: { y: 0, scale: 1 },
  hover: { 
    y: -4, 
    scale: 1.01,
    transition: springPresets.responsive 
  },
  tap: { 
    scale: 0.98,
    transition: { duration: 0.1 }
  }
};

export const pageFadeVariants: Variants = {
  initial: { opacity: 0, y: 12, scale: 0.99 },
  animate: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] } 
  },
  exit: { 
    opacity: 0, 
    y: -10, 
    scale: 0.99,
    transition: { duration: 0.2, ease: 'easeIn' } 
  }
};

export const listContainerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.05
    }
  }
};

export const listItemVariants: Variants = {
  hidden: { opacity: 0, y: 10, scale: 0.98 },
  show: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: springPresets.gentle 
  }
};

export const floatingToolbarVariants: Variants = {
  hidden: { opacity: 0, y: 15, scale: 0.92 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: springPresets.responsive
  },
  exit: { 
    opacity: 0, 
    y: 10, 
    scale: 0.95,
    transition: { duration: 0.15 } 
  }
};
