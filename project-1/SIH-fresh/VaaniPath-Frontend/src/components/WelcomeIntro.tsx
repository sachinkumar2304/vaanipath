import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface WelcomeIntroProps {
    onComplete: () => void;
}

export const WelcomeIntro = ({ onComplete }: WelcomeIntroProps) => {
    const [step, setStep] = useState(0);

    const greetings = [
        { text: "Welcome", lang: "English" },
        { text: "नमस्ते", lang: "Hindi" },
        { text: "வணக்கம்", lang: "Tamil" },
        { text: "സ്വാഗതം", lang: "Malayalam" },
        { text: "স্বাগতম", lang: "Bengali" },
        { text: "સ્વાગત છે", lang: "Gujarati" },
        { text: "ਸੁਆਗਤ ਹੈ", lang: "Punjabi" },
        { text: "ಸುಸ್ವಾಗತ", lang: "Kannada" },
        { text: "स्वागत आहे", lang: "Marathi" },
        { text: "VaaniPath", lang: "Universal" }
    ];

    useEffect(() => {
        const timer = setInterval(() => {
            setStep((prev) => {
                if (prev >= greetings.length - 1) {
                    clearInterval(timer);
                    setTimeout(onComplete, 1000); // Wait 1s after last greeting before closing
                    return prev;
                }
                return prev + 1;
            });
        }, 750); // 0.75 seconds per language

        return () => clearInterval(timer);
    }, [onComplete]);

    return (
        <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black overflow-hidden"
            exit={{ opacity: 0, transition: { duration: 0.8 } }}
        >
            {/* Cosmos Background */}
            <div className="absolute inset-0 z-0">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900 via-[#00091d] to-black"></div>
                {[...Array(50)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute bg-white rounded-full"
                        initial={{
                            x: Math.random() * window.innerWidth,
                            y: Math.random() * window.innerHeight,
                            scale: Math.random() * 0.5 + 0.5,
                            opacity: Math.random() * 0.5 + 0.2,
                        }}
                        animate={{
                            opacity: [0.2, 1, 0.2],
                            scale: [0.5, 1, 0.5],
                        }}
                        transition={{
                            duration: Math.random() * 3 + 2,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                        style={{
                            width: Math.random() * 3 + 1 + "px",
                            height: Math.random() * 3 + 1 + "px",
                        }}
                    />
                ))}
            </div>

            <div className="relative z-10 flex flex-col items-center justify-center">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={step}
                        initial={{ opacity: 0, scale: 0.8, filter: "blur(10px)" }}
                        animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                        exit={{ opacity: 0, scale: 1.1, filter: "blur(10px)" }}
                        transition={{ duration: 0.4 }}
                        className="text-center"
                    >
                        <h1 className="text-5xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 drop-shadow-[0_0_15px_rgba(168,85,247,0.3)] flex items-center justify-center gap-6">
                            {greetings[step].text}
                        </h1>
                        <p className="mt-6 text-slate-400 text-xl md:text-2xl font-bold tracking-[0.5em] uppercase drop-shadow-md">
                            {greetings[step].lang}
                        </p>
                    </motion.div>
                </AnimatePresence>
            </div>
        </motion.div>
    );
};
