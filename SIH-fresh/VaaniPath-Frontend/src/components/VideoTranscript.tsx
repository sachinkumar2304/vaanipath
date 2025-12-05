import { useState, useEffect, useRef } from 'react';
import { Search, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { TranscriptEntry } from '@/types/video';
import { motion, AnimatePresence } from 'framer-motion';

interface VideoTranscriptProps {
    transcript: TranscriptEntry[];
    currentTime: number;
    onTimestampClick: (time: number) => void;
    className?: string;
}

export const VideoTranscript = ({
    transcript,
    currentTime,
    onTimestampClick,
    className = ''
}: VideoTranscriptProps) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [copied, setCopied] = useState(false);
    const activeEntryRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to active entry
    useEffect(() => {
        if (activeEntryRef.current && isExpanded) {
            activeEntryRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    }, [currentTime, isExpanded]);

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const filteredTranscript = transcript.filter(entry =>
        entry.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.speaker?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const currentEntryIndex = transcript.findIndex(
        entry => currentTime >= entry.startTime && currentTime < entry.endTime
    );

    const copyTranscript = () => {
        const text = transcript
            .map(entry => `[${formatTime(entry.startTime)}] ${entry.speaker ? `${entry.speaker}: ` : ''}${entry.text}`)
            .join('\n\n');
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className={`glass-card border-white/20 dark:border-white/10 rounded-2xl shadow-xl overflow-hidden ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border/50 bg-background/30">
                <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold text-foreground">Transcript</h3>
                    <span className="text-xs text-muted-foreground bg-muted/50 px-2 py-1 rounded-full">
                        {transcript.length} entries
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={copyTranscript}
                        className="h-8 px-3"
                        aria-label="Copy transcript"
                    >
                        {copied ? (
                            <Check className="h-4 w-4 text-green-600" />
                        ) : (
                            <Copy className="h-4 w-4" />
                        )}
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="h-8 px-3"
                        aria-label={isExpanded ? 'Collapse transcript' : 'Expand transcript'}
                    >
                        {isExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                        ) : (
                            <ChevronDown className="h-4 w-4" />
                        )}
                    </Button>
                </div>
            </div>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: 'easeInOut' }}
                    >
                        {/* Search Bar */}
                        <div className="p-4 border-b border-border/50 bg-background/20">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search transcript..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10 h-10 bg-background/50 border-input focus:ring-primary"
                                />
                            </div>
                        </div>

                        {/* Transcript Entries */}
                        <div className="max-h-96 overflow-y-auto p-4 space-y-3">
                            {filteredTranscript.length > 0 ? (
                                filteredTranscript.map((entry, index) => {
                                    const isActive = currentTime >= entry.startTime && currentTime < entry.endTime;
                                    const globalIndex = transcript.indexOf(entry);

                                    return (
                                        <div
                                            key={index}
                                            ref={isActive ? activeEntryRef : null}
                                            onClick={() => onTimestampClick(entry.startTime)}
                                            className={`
                        group cursor-pointer p-3 rounded-xl transition-all duration-200
                        ${isActive
                                                    ? 'bg-primary/10 border-l-4 border-primary shadow-sm'
                                                    : 'hover:bg-muted/50 border-l-4 border-transparent'
                                                }
                      `}
                                            role="button"
                                            tabIndex={0}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' || e.key === ' ') {
                                                    e.preventDefault();
                                                    onTimestampClick(entry.startTime);
                                                }
                                            }}
                                            aria-label={`Jump to ${formatTime(entry.startTime)}`}
                                        >
                                            <div className="flex items-start gap-3">
                                                <span className={`
                          text-xs font-mono font-medium px-2 py-1 rounded-md flex-shrink-0
                          ${isActive
                                                        ? 'bg-primary text-primary-foreground'
                                                        : 'bg-muted text-muted-foreground group-hover:bg-primary/20 group-hover:text-primary'
                                                    }
                        `}>
                                                    {formatTime(entry.startTime)}
                                                </span>
                                                <div className="flex-1 min-w-0">
                                                    {entry.speaker && (
                                                        <p className="text-xs font-semibold text-primary mb-1">
                                                            {entry.speaker}
                                                        </p>
                                                    )}
                                                    <p className={`
                            text-sm leading-relaxed
                            ${isActive ? 'text-foreground font-medium' : 'text-muted-foreground'}
                          `}>
                                                        {entry.text}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })
                            ) : (
                                <div className="text-center py-8">
                                    <p className="text-muted-foreground">No transcript entries found</p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
