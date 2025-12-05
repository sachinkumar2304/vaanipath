import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, CheckCircle, Clock, Music, Headphones, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getVideoDetails, type Video } from '@/services/videos';
import {
    getDubbedContent,
    checkDubbingStatus,
    getAvailableLanguages,
    updateProgress as updateProgressService,
    getProgress,
    getVideoQuiz,
    submitQuiz,
    cancelDubbing,
    type LanguageAvailability,
    type DubbingStatusResponse
} from '@/services/processing';

const CourseDetail = () => {
    const { videoId } = useParams<{ videoId: string }>();
    const navigate = useNavigate();
    const { isTeacher } = useAuth();
    const { toast } = useToast();
    const videoRef = useRef<HTMLVideoElement>(null);

    const [video, setVideo] = useState<Video | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedLanguage, setSelectedLanguage] = useState('');
    const [contentUrl, setContentUrl] = useState('');
    const [dubbingStatus, setDubbingStatus] = useState<'loading' | 'processing' | 'ready' | 'error'>('loading');
    const [availableLanguages, setAvailableLanguages] = useState<LanguageAvailability[]>([]);
    const [progress, setProgress] = useState(0);
    const [showQuiz, setShowQuiz] = useState(false);
    const [quiz, setQuiz] = useState<any>(null);
    const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
    const [dubbingProgress, setDubbingProgress] = useState(0);

    useEffect(() => {
        if (videoId) {
            fetchVideo();
            fetchProgress();
            fetchAvailableLanguages();
        }
        return () => {
            // Cleanup: Clear polling interval on unmount
            if (pollingInterval) {
                clearInterval(pollingInterval);
                setPollingInterval(null);
            }
        };
    }, [videoId]);

    const fetchVideo = async () => {
        try {
            setLoading(true);
            const data = await getVideoDetails(videoId!);
            setVideo(data);
            setSelectedLanguage(data.source_language);
            setContentUrl(data.file_url);
            setDubbingStatus('ready');
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to load video',
                variant: 'destructive',
            });
            navigate('/enrolled');
        } finally {
            setLoading(false);
        }
    };

    const fetchProgress = async () => {
        try {
            const { progress: savedProgress } = await getProgress(videoId!);
            setProgress(savedProgress);
        } catch (error) {
            console.error('Failed to fetch progress:', error);
        }
    };

    const fetchAvailableLanguages = async () => {
        try {
            const { languages } = await getAvailableLanguages(videoId!);
            setAvailableLanguages(languages);
        } catch (error) {
            console.error('Failed to fetch languages:', error);
        }
    };

    const handleLanguageChange = async (language: string) => {
        if (!video) return;

        setSelectedLanguage(language);

        // If selecting source language, use original URL
        if (language === video.source_language) {
            setContentUrl(video.file_url);
            setDubbingStatus('ready');
            return;
        }

        // Check if dubbed version exists
        setDubbingStatus('loading');

        try {
            const result = await getDubbedContent(videoId!, language);

            if (result.status === 'completed' && result.content_url) {
                setContentUrl(result.content_url);
                setDubbingStatus('ready');

                toast({
                    title: result.cached ? 'Cached Content' : 'Content Ready',
                    description: result.message,
                });

                // Refresh available languages
                fetchAvailableLanguages();
            } else if (result.status === 'processing') {
                setDubbingStatus('processing');

                toast({
                    title: 'Processing',
                    description: result.message,
                });

                // Start polling
                startPolling(language);
            }
        } catch (error: any) {
            setDubbingStatus('error');
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to get dubbed content',
                variant: 'destructive',
            });
        }
    };

    const startPolling = (language: string) => {
        // Clear existing interval
        if (pollingInterval) clearInterval(pollingInterval);

        const interval = setInterval(async () => {
            try {
                const status: DubbingStatusResponse = await checkDubbingStatus(videoId!, language);

                // Update progress
                if (status.progress) {
                    setDubbingProgress(status.progress);
                }

                if (status.status === 'completed' && status.content_url) {
                    setContentUrl(status.content_url);
                    setDubbingStatus('ready');
                    clearInterval(interval);
                    setPollingInterval(null);

                    toast({
                        title: 'Dubbing Complete!',
                        description: 'Video is ready to watch',
                    });

                    fetchAvailableLanguages();
                } else if (status.status === 'failed') {
                    setDubbingStatus('error');
                    clearInterval(interval);
                    setPollingInterval(null);

                    toast({
                        title: 'Dubbing Failed',
                        description: status.error || 'Please try again',
                        variant: 'destructive',
                    });
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 5000); // Poll every 5 seconds

        setPollingInterval(interval);
    };

    const handleCancelDubbing = async () => {
        if (!videoId || !selectedLanguage) return;

        try {
            await cancelDubbing(videoId, selectedLanguage);

            // Clear polling
            if (pollingInterval) {
                clearInterval(pollingInterval);
                setPollingInterval(null);
            }

            setDubbingStatus('ready');
            setContentUrl(video?.file_url || '');
            setSelectedLanguage(video?.source_language || '');

            toast({
                title: 'Cancelled',
                description: 'Dubbing has been cancelled',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to cancel',
                variant: 'destructive',
            });
        }
    };

    const lastUpdatedProgress = useRef(0);

    const handleTimeUpdate = async () => {
        if (!videoRef.current || !video) return;

        const currentTime = videoRef.current.currentTime;
        const duration = videoRef.current.duration;

        if (duration > 0) {
            const newProgress = (currentTime / duration) * 100;
            setProgress(newProgress);

            // Update progress every 5% change
            const currentStep = Math.floor(newProgress / 5) * 5;

            if (currentStep > lastUpdatedProgress.current && currentStep > 0) {
                lastUpdatedProgress.current = currentStep;
                try {
                    await updateProgressService(videoId!, currentStep);
                } catch (error) {
                    console.error('Failed to update progress:', error);
                }
            }

            // Show quiz at 90% completion
            if (newProgress >= 90 && !showQuiz) {
                fetchQuiz();
            }
        }
    };

    const fetchQuiz = async () => {
        try {
            const quizData = await getVideoQuiz(videoId!);
            if (quizData && quizData.length > 0) {
                setQuiz(quizData);
                setShowQuiz(true);
            }
        } catch (error) {
            console.error('Failed to fetch quiz:', error);
        }
    };

    const getLanguageLabel = (code: string) => {
        const labels: Record<string, string> = {
            'en': 'English',
            'hi': 'हिंदी',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'bn': 'বাংলা',
            'mr': 'मराठी',
            'gu': 'ગુજરાતી',
        };
        return labels[code] || code.toUpperCase();
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!video) {
        return null;
    }

    return (
        <div className="min-h-screen bg-background">
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />

            <div className="container px-4 py-8">
                <div className="max-w-5xl mx-auto">
                    <Card>
                        <CardHeader>
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <CardTitle className="text-2xl mb-2">{video.title}</CardTitle>
                                    <p className="text-muted-foreground">{video.description}</p>
                                </div>
                                <Badge variant="outline">{video.domain}</Badge>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Language Selector */}
                            <div className="flex items-center gap-4">
                                <label className="font-medium">Select Language:</label>
                                <Select value={selectedLanguage} onValueChange={handleLanguageChange}>
                                    <SelectTrigger className="w-[200px]">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {availableLanguages.map((lang) => (
                                            <SelectItem key={lang.code} value={lang.code}>
                                                <div className="flex items-center gap-2">
                                                    {getLanguageLabel(lang.code)}
                                                    {lang.status === 'original' && (
                                                        <Badge variant="outline" className="text-xs">Original</Badge>
                                                    )}
                                                    {lang.available && lang.status === 'completed' && (
                                                        <CheckCircle className="h-3 w-3 text-green-600" />
                                                    )}
                                                    {!lang.available && lang.status === 'not_generated' && (
                                                        <Clock className="h-3 w-3 text-yellow-600" />
                                                    )}
                                                </div>
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>

                                {dubbingStatus === 'processing' && (
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            Processing... {dubbingProgress}%
                                        </div>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={handleCancelDubbing}
                                        >
                                            Cancel
                                        </Button>
                                    </div>
                                )}
                            </div>

                            {/* Progress Bar */}
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Progress</span>
                                    <span className="font-medium">{Math.round(progress)}%</span>
                                </div>
                                <Progress value={progress} className="h-2" />
                            </div>

                            {dubbingStatus === 'ready' && contentUrl && (
                                <div className="space-y-4">
                                    {video.content_type === 'video' && (
                                        <div className="relative aspect-video bg-black rounded-lg overflow-hidden shadow-xl border border-border/50">
                                            <video
                                                ref={videoRef}
                                                className="w-full h-full"
                                                controls
                                                onTimeUpdate={handleTimeUpdate}
                                                src={contentUrl}
                                            >
                                                Your browser does not support video playback.
                                            </video>
                                        </div>
                                    )}

                                    {video.content_type === 'audio' && (
                                        <div className="w-full bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 rounded-xl p-8 md:p-12 shadow-2xl overflow-hidden border border-white/10 relative group">
                                            {/* Decorative Background Effects */}
                                            <div className="absolute top-0 left-0 w-full h-full overflow-hidden opacity-30 pointer-events-none">
                                                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600 rounded-full blur-[120px] animate-pulse"></div>
                                                <div className="absolute -top-20 -right-20 w-72 h-72 bg-purple-600 rounded-full blur-[100px] opacity-60"></div>
                                                <div className="absolute -bottom-20 -left-20 w-72 h-72 bg-indigo-600 rounded-full blur-[100px] opacity-60"></div>
                                            </div>

                                            <div className="relative z-10 flex flex-col items-center justify-center space-y-8">
                                                {/* Visual Icon with Glow */}
                                                <div className="relative group/icon">
                                                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur opacity-75 group-hover/icon:opacity-100 transition duration-1000 group-hover/icon:duration-200 animate-tilt"></div>
                                                    <div className="relative bg-black/40 backdrop-blur-xl p-8 rounded-full border border-white/10 shadow-2xl ring-1 ring-white/20 transition-transform duration-500 hover:scale-105">
                                                        <Headphones className="w-16 h-16 text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.5)]" />
                                                    </div>
                                                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 flex items-center gap-1">
                                                        <Sparkles className="w-3 h-3 text-yellow-400" />
                                                        <span className="text-[10px] font-bold text-white tracking-widest uppercase">Premium Audio</span>
                                                    </div>
                                                </div>

                                                {/* Title & Info */}
                                                <div className="text-center space-y-3 max-w-lg">
                                                    <h3 className="text-2xl md:text-3xl font-bold text-white tracking-tight drop-shadow-lg">{video.title}</h3>
                                                    <div className="flex flex-wrap items-center justify-center gap-2">
                                                        <Badge variant="secondary" className="bg-blue-500/20 text-blue-200 hover:bg-blue-500/30 border-blue-500/30 backdrop-blur-sm">
                                                            AUDIO LESSON
                                                        </Badge>
                                                        <Badge variant="outline" className="border-white/20 text-white/80 backdrop-blur-sm">
                                                            {getLanguageLabel(selectedLanguage)}
                                                        </Badge>
                                                        <Badge variant="outline" className="border-purple-500/30 text-purple-200 bg-purple-500/10 backdrop-blur-sm">
                                                            HQ
                                                        </Badge>
                                                    </div>
                                                </div>

                                                {/* Custom Styled Audio Player Container */}
                                                <div className="w-full max-w-3xl bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10 shadow-xl hover:bg-white/10 transition-colors duration-300">
                                                    <audio
                                                        ref={videoRef as any}
                                                        className="w-full h-12 [&::-webkit-media-controls-panel]:bg-transparent [&::-webkit-media-controls-enclosure]:bg-transparent filter invert-[1] brightness-200 contrast-200 sepia-[.2] hue-rotate-[180deg] saturate-[.5]"
                                                        controls
                                                        onTimeUpdate={handleTimeUpdate}
                                                        src={contentUrl}
                                                    >
                                                        Your browser does not support audio playback.
                                                    </audio>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {video.content_type === 'document' && (
                                        <div className="relative aspect-video bg-muted rounded-lg overflow-hidden shadow-md border border-border">
                                            <iframe
                                                src={contentUrl}
                                                className="w-full h-full"
                                                title="Document Viewer"
                                            />
                                        </div>
                                    )}
                                </div>
                            )}

                            {dubbingStatus === 'processing' && (
                                <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                                    <div className="text-center space-y-4">
                                        <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
                                        <div>
                                            <p className="font-medium">Generating Dubbed Content</p>
                                            <p className="text-sm text-muted-foreground">Progress: {dubbingProgress}%</p>
                                            <p className="text-sm text-muted-foreground">This may take 2-5 minutes...</p>
                                        </div>
                                        <Button variant="outline" onClick={handleCancelDubbing}>
                                            Cancel Dubbing
                                        </Button>
                                    </div>
                                </div>
                            )}

                            {dubbingStatus === 'error' && (
                                <div className="aspect-video bg-destructive/10 rounded-lg flex items-center justify-center">
                                    <div className="text-center space-y-4">
                                        <p className="font-medium text-destructive">Failed to generate content</p>
                                        <div className="space-x-2">
                                            <Button onClick={() => handleLanguageChange(selectedLanguage)}>
                                                Retry
                                            </Button>
                                            <Button
                                                variant="outline"
                                                onClick={() => {
                                                    setDubbingStatus('ready');
                                                    setSelectedLanguage(video.source_language);
                                                    setContentUrl(video.file_url);
                                                }}
                                            >
                                                Back to Original
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Quiz Section */}
                            {showQuiz && quiz && (
                                <Card className="border-primary">
                                    <CardHeader>
                                        <CardTitle>Complete the Quiz</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <p className="text-sm text-muted-foreground mb-4">
                                            Test your knowledge about this content!
                                        </p>
                                        <Button onClick={() => navigate(`/quiz/${videoId}`)}>
                                            <Play className="mr-2 h-4 w-4" />
                                            Start Quiz
                                        </Button>
                                    </CardContent>
                                </Card>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default CourseDetail;
