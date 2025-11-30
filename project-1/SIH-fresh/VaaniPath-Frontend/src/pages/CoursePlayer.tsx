import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { getCourseById, CourseWithVideos } from '@/services/courses';
import { getCourseProgress, updateVideoProgress } from '@/services/enrollments';
import { INDIAN_LANGUAGES } from '@/constants/languages';
import {
    CheckCircle2, Circle, Play, ArrowLeft, BookOpen, Clock, Languages, Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';

import { triggerDubbing, pollDubbingStatus, checkDubbedVersion } from '@/services/dubbing';
import api from '@/services/api';


const CoursePlayer = () => {
    const { courseId } = useParams<{ courseId: string }>();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { toast } = useToast();
    const { user, isTeacher } = useAuth();
    const videoRef = useRef<HTMLVideoElement>(null);

    const [course, setCourse] = useState<CourseWithVideos | null>(null);
    const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
    const [progress, setProgress] = useState<Record<string, any>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [watchedPercentage, setWatchedPercentage] = useState(0);
    const [selectedLanguage, setSelectedLanguage] = useState('en-IN');
    const [isDubbing, setIsDubbing] = useState(false);
    const [dubbedUrl, setDubbedUrl] = useState<string | null>(null);
    const [availableLanguages, setAvailableLanguages] = useState<string[]>(['en-IN']); // Languages available for current video

    const currentVideo = course?.videos?.[currentVideoIndex];

    // Fetch available dubbed languages for current video
    useEffect(() => {
        const fetchAvailableLanguages = async () => {
            if (!currentVideo) return;

            try {
                // Use batch endpoint to get all available languages at once
                const response = await api.get(`/videos/${currentVideo.id}/available-languages`);
                const availableLangs = response.data.available_languages || [];

                // Original language is always available
                setAvailableLanguages(['en-IN', ...availableLangs]);
            } catch (error) {
                console.error('Error fetching available languages:', error);
                // Fallback to just original language
                setAvailableLanguages(['en-IN']);
            }
        };

        fetchAvailableLanguages();
    }, [currentVideo]);

    // Increment view count when video loads (after 5 seconds)
    useEffect(() => {
        if (currentVideo?.id) {
            const timer = setTimeout(() => {
                api.post(`/videos/${currentVideo.id}/view`)
                    .catch(err => console.error("Failed to count view", err));
            }, 5000);

            return () => clearTimeout(timer);
        }
    }, [currentVideo?.id]);

    // Reset language and dubbed = URL when video changes
    useEffect(() => {
        setSelectedLanguage('en-IN');
        setDubbedUrl(null);
        setIsDubbing(false);
    }, [currentVideoIndex]);

    // Only trigger dubbing when user explicitly changes language
    useEffect(() => {
        if (!currentVideo || selectedLanguage === 'en-IN') return;

        handleLanguageChange(selectedLanguage);
    }, [selectedLanguage]); // Only depend on selectedLanguage, NOT currentVideo

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        if (courseId) {
            loadCourse();
            loadProgress();
        }
    }, [user, courseId, navigate]);


    const handleLanguageChange = async (language: string) => {
        if (!currentVideo || !courseId) return;

        if (language === 'en-IN') {
            // Reset to original video
            setDubbedUrl(null);
            return;
        }

        try {
            setIsDubbing(true);

            // Check if already dubbed
            const existingUrl = await checkDubbedVersion(currentVideo.id, language);
            if (existingUrl) {
                setDubbedUrl(existingUrl);
                toast({
                    title: 'Cached Content',
                    description: 'Playing previously dubbed version',
                });
                return;
            }

            toast({
                title: 'Dubbing Started',
                description: `Preparing ${INDIAN_LANGUAGES.find(l => l.code === language)?.name} version...`,
            });

            // Trigger dubbing via backend
            await triggerDubbing(
                currentVideo.file_url,
                (currentVideo.source_language || 'en').split('-')[0],
                language,
                currentVideo.id,
                courseId
            );

            // Poll for completion via backend
            const dubbedPath = await pollDubbingStatus(currentVideo.id, language);

            if (dubbedPath) {
                setDubbedUrl(dubbedPath);
                // Add to available languages
                if (!availableLanguages.includes(language)) {
                    setAvailableLanguages([...availableLanguages, language]);
                }
                toast({
                    title: 'Dubbing Complete!',
                    description: 'Now playing in selected language',
                });
            } else {
                throw new Error('Dubbing timeout');
            }
        } catch (error) {
            console.error('Dubbing error:', error);
            toast({
                title: 'Dubbing Failed',
                description: 'Playing original version',
                variant: 'destructive',
            });
            setSelectedLanguage('en-IN');
        } finally {
            setIsDubbing(false);
        }
    };

    const loadCourse = async () => {
        if (!courseId) return;

        try {
            setIsLoading(true);
            const data = await getCourseById(courseId);
            setCourse(data);

            // If videoId is in query params, find and set that video
            const videoId = searchParams.get('videoId');
            if (videoId && data.videos) {
                const videoIndex = data.videos.findIndex(v => v.id === videoId);
                if (videoIndex !== -1) {
                    setCurrentVideoIndex(videoIndex);
                }
            }
        } catch (error) {
            console.error('Failed to load course:', error);
            toast({
                title: 'Error',
                description: 'Failed to load course',
                variant: 'destructive',
            });
            navigate('/my-courses');
        } finally {
            setIsLoading(false);
        }
    };

    const loadProgress = async () => {
        if (!courseId) return;

        try {
            const enrollmentData = await getCourseProgress(courseId);
            setProgress(enrollmentData.progress || {});
        } catch (error: any) {
            // Ignore 404 (not enrolled or no progress yet)
            if (error.response?.status === 404) {
                setProgress({});
                return;
            }
            console.error('Failed to load progress:', error);
        }
    };

    const handleVideoEnd = async () => {
        if (!course || !courseId) return;

        const currentVideo = course.videos[currentVideoIndex];
        if (!currentVideo) return;

        try {
            await updateVideoProgress(courseId, {
                video_id: currentVideo.id,
                completed: true,
                watched_duration: currentVideo.duration || 0,
            });

            // Update local progress
            setProgress(prev => ({
                ...prev,
                [currentVideo.id]: {
                    completed: true,
                    watched_duration: currentVideo.duration || 0,
                },
            }));

            toast({
                title: 'Video Completed!',
                description: 'Your progress has been saved',
            });

            // Auto-play next video if available
            if (currentVideoIndex < course.videos.length - 1) {
                setTimeout(() => {
                    setCurrentVideoIndex(currentVideoIndex + 1);
                }, 2000);
            }
        } catch (error) {
            console.error('Failed to update progress:', error);
        }
    };

    const handleVideoTimeUpdate = () => {
        if (!videoRef.current || !course) return;

        const video = videoRef.current;
        const percentage = (video.currentTime / video.duration) * 100;
        setWatchedPercentage(percentage);

        // Mark as complete if watched 90%+
        if (percentage >= 90 && !progress[course.videos[currentVideoIndex]?.id]?.completed) {
            handleVideoEnd();
        }
    };

    const handleVideoSelect = (index: number) => {
        setCurrentVideoIndex(index);
        setWatchedPercentage(0);
        // Reset language to default when switching videos
        setSelectedLanguage('en-IN');
        setDubbedUrl(null);
    };

    if (isLoading || !course) {
        return (
            <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
                <PremiumBackground />
                <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
                <div className="flex items-center justify-center min-h-[60vh]">
                    <BookOpen className="h-16 w-16 text-primary animate-pulse" />
                </div>
            </div>
        );
    }


    const completedCount = Object.values(progress).filter((p: any) => p.completed).length;
    const totalVideos = course.videos.length;
    const overallProgress = totalVideos > 0 ? (completedCount / totalVideos) * 100 : 0;

    return (
        <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />

            <div className="container px-4 py-6 lg:py-8 relative z-10">
                {/* Back Button */}
                <Button
                    variant="ghost"
                    className="mb-4"
                    onClick={() => navigate(isTeacher ? '/teacher/courses' : '/my-courses')}
                >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to My Courses
                </Button>

                <div className="grid lg:grid-cols-[1fr_380px] gap-6">
                    {/* Video Player */}
                    <div className="space-y-6">
                        {/* Language Selector */}
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <Languages className="h-5 w-5 text-primary" />
                                <h2 className="text-lg font-semibold">Video Language</h2>
                            </div>
                            <Select
                                value={selectedLanguage}
                                onValueChange={setSelectedLanguage}
                                disabled={isDubbing}
                            >
                                <SelectTrigger className="w-[200px] glass-card border-white/20">
                                    <SelectValue placeholder="Select Language" />
                                </SelectTrigger>
                                <SelectContent>
                                    {INDIAN_LANGUAGES.map((lang) => {
                                        const isAvailable = availableLanguages.includes(lang.code);
                                        return (
                                            <SelectItem key={lang.code} value={lang.code}>
                                                <div className="flex items-center gap-2">
                                                    <span>{lang.name} ({lang.native})</span>
                                                    {isAvailable && (
                                                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                                                    )}
                                                </div>
                                            </SelectItem>
                                        );
                                    })}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Video */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                            className="aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl"
                        >
                            {currentVideo ? (
                                <video
                                    ref={videoRef}
                                    key={currentVideo.id + (dubbedUrl || '')}
                                    src={dubbedUrl || currentVideo.file_url}
                                    poster={currentVideo.thumbnail_url}
                                    controls
                                    className="w-full h-full"
                                    onEnded={handleVideoEnd}
                                    onTimeUpdate={handleVideoTimeUpdate}
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-white">
                                    <p>No video selected</p>
                                </div>
                            )}
                        </motion.div>

                        {/* Video Info */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                        >
                            <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl">
                                <CardContent className="p-6">
                                    <h1 className="text-2xl font-bold mb-2">
                                        {currentVideo?.title || 'No video selected'}
                                    </h1>
                                    <p className="text-muted-foreground mb-4">
                                        {currentVideo?.description || 'No description available'}
                                    </p>
                                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                        <div className="flex items-center gap-1">
                                            <Clock className="h-4 w-4" />
                                            <span>{Math.round((currentVideo?.duration || 0) / 60)} mins</span>
                                        </div>
                                        {progress[currentVideo?.id || '']?.completed && (
                                            <div className="flex items-center gap-1 text-green-500">
                                                <CheckCircle2 className="h-4 w-4" />
                                                <span>Completed</span>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    </div>

                    {/* Course Content List */}
                    <div className="space-y-6">
                        <Card className="glass-card border-white/20 dark:border-white/10 h-fit">
                            <CardContent className="p-6">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <BookOpen className="h-5 w-5 text-primary" />
                                    Course Content
                                </h3>

                                {/* Overall Progress */}
                                <div className="mb-6">
                                    <div className="flex justify-between text-sm mb-2">
                                        <span>Course Progress</span>
                                        <span>{Math.round(overallProgress)}%</span>
                                    </div>
                                    <Progress value={overallProgress} className="h-2" />
                                </div>

                                <div className="space-y-3">
                                    {course.videos.map((video, index) => {
                                        const isCompleted = progress[video.id]?.completed;
                                        const isActive = currentVideoIndex === index;

                                        return (
                                            <motion.div
                                                key={video.id}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: index * 0.05 }}
                                            >
                                                <button
                                                    onClick={() => handleVideoSelect(index)}
                                                    className={`w-full text-left p-3 rounded-xl transition-all duration-200 flex items-start gap-3 group ${isActive
                                                        ? 'bg-primary/10 border border-primary/20'
                                                        : 'hover:bg-white/5 border border-transparent hover:border-white/10'
                                                        }`}
                                                >
                                                    <div className={`mt-1 ${isCompleted ? 'text-green-500' : isActive ? 'text-primary' : 'text-muted-foreground'
                                                        }`}>
                                                        {isActive ? (
                                                            <Play className="h-4 w-4 fill-current" />
                                                        ) : isCompleted ? (
                                                            <CheckCircle2 className="h-4 w-4" />
                                                        ) : (
                                                            <Circle className="h-4 w-4" />
                                                        )}
                                                    </div>
                                                    <div className="flex-1">
                                                        <p className={`text-sm font-medium line-clamp-2 ${isActive ? 'text-primary' : 'text-foreground'
                                                            }`}>
                                                            {video.title}
                                                        </p>
                                                        <p className="text-xs text-muted-foreground mt-1">
                                                            {Math.round(video.duration / 60)} mins
                                                        </p>
                                                    </div>
                                                </button>
                                            </motion.div>
                                        );
                                    })}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CoursePlayer;
