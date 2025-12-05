import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export const PremiumBackground = () => {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            // Throttle or use requestAnimationFrame for performance if needed, 
            // but for simple parallax, direct state update is usually fine on modern devices.
            // Using a dampening factor (20) to keep movement subtle.
            setMousePosition({
                x: (e.clientX / window.innerWidth) * 20,
                y: (e.clientY / window.innerHeight) * 20,
            });
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none bg-slate-50 dark:bg-slate-950 transition-colors duration-500">
            {/* Soft Gradient Layers - "Bloom" effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/80 via-white/50 to-purple-50/80 dark:from-slate-950 dark:via-slate-900/80 dark:to-slate-950 opacity-80" />

            <div className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] rounded-full bg-blue-200/20 dark:bg-blue-900/10 blur-[120px] animate-pulse-glow" />
            <div className="absolute top-[40%] -right-[10%] w-[50%] h-[50%] rounded-full bg-purple-200/20 dark:bg-purple-900/10 blur-[120px] animate-pulse-glow delay-2000" />
            <div className="absolute -bottom-[10%] left-[20%] w-[40%] h-[40%] rounded-full bg-teal-200/20 dark:bg-teal-900/10 blur-[100px] animate-pulse-glow delay-1000" />

            {/* Floating 3D Elements (CSS-based Parallax) */}

            {/* Element 1: Open Book */}
            <motion.div
                className="absolute top-20 left-[10%] opacity-30 dark:opacity-20 text-blue-300 dark:text-blue-800"
                animate={{
                    y: [0, -25, 0],
                    rotate: [0, 5, 0],
                    scale: [1, 1.05, 1]
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                style={{ x: mousePosition.x * -1.5, y: mousePosition.y * -1.5 }}
            >
                <svg width="140" height="140" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                    <path d="M6.5 2v15" />
                    <path d="M10 6h6" opacity="0.5" />
                    <path d="M10 10h6" opacity="0.5" />
                    <path d="M10 14h4" opacity="0.5" />
                </svg>
            </motion.div>

            {/* Element 2: Graduation Cap / Knowledge Symbol */}
            <motion.div
                className="absolute bottom-32 right-[15%] opacity-20 dark:opacity-10 text-purple-400 dark:text-purple-700"
                animate={{
                    y: [0, 35, 0],
                    rotate: [0, -8, 0],
                    scale: [1, 1.1, 1]
                }}
                transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                style={{ x: mousePosition.x * 2, y: mousePosition.y * 2 }}
            >
                <svg width="180" height="180" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="0.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                    <path d="M6 12v5c3 3 9 3 12 0v-5" />
                </svg>
            </motion.div>

            {/* Element 3: Abstract Paper / Document */}
            <motion.div
                className="absolute top-1/3 left-1/2 opacity-10 dark:opacity-5 text-teal-400 dark:text-teal-700"
                animate={{
                    y: [0, -40, 0],
                    rotate: [12, 15, 12],
                    scale: [1, 1.05, 1]
                }}
                transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                style={{ x: mousePosition.x * 0.8, y: mousePosition.y * 0.8 }}
            >
                <svg width="200" height="240" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="0.5">
                    <rect x="4" y="2" width="16" height="20" rx="2" />
                    <path d="M8 6h8" />
                    <path d="M8 10h8" />
                    <path d="M8 14h8" />
                    <path d="M8 18h5" />
                </svg>
            </motion.div>

            {/* Element 4: Floating Pencil/Pen */}
            <motion.div
                className="absolute bottom-10 left-[5%] opacity-20 dark:opacity-10 text-orange-300 dark:text-orange-800"
                animate={{
                    y: [0, -15, 0],
                    rotate: [-45, -40, -45],
                }}
                transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
                style={{ x: mousePosition.x * 1.2, y: mousePosition.y * 1.2 }}
            >
                <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                </svg>
            </motion.div>
        </div>
    );
};
