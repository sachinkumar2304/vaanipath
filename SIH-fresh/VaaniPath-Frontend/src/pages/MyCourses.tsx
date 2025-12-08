import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { getMyEnrollments, Enrollment } from '@/services/enrollments';
import { BookOpen, Play, Video, CheckCircle2, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';

const MyCourses = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { toast } = useToast();
    const { user } = useAuth();

    const { data, isLoading } = useQuery({
        queryKey: ['my-enrollments'],
        queryFn: getMyEnrollments,
        enabled: !!user,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });

    const enrollments = data?.enrollments || [];

    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    return (
        <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
            <PremiumBackground />
            <Header isAuthenticated userType={user?.is_teacher ? "teacher" : "student"} />

            <div className="container px-4 py-12 lg:py-16 relative z-10">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mb-10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 rounded-2xl bg-primary/10 backdrop-blur-md border border-primary/20">
                            <BookOpen className="h-6 w-6 text-primary" />
                        </div>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold mb-3 text-foreground font-heading tracking-tight">
                        {t('myCourses.title')}
                    </h1>
                    <p className="text-lg text-muted-foreground">
                        {t('myCourses.subtitle')}
                    </p>
                </motion.div>

                {/* Course Grid */}
                {isLoading ? (
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {[1, 2, 3, 4, 5, 6].map((i) => (
                            <Card key={i} className="h-full flex flex-col overflow-hidden">
                                <div className="aspect-video bg-muted/50 animate-pulse" />
                                <CardHeader className="flex-grow space-y-3">
                                    <div className="h-6 bg-muted/50 rounded animate-pulse" />
                                    <div className="h-4 bg-muted/50 rounded w-3/4 animate-pulse" />
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    <div className="h-2 bg-muted/50 rounded animate-pulse" />
                                    <div className="h-10 bg-muted/50 rounded animate-pulse" />
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : enrollments.length > 0 ? (
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {enrollments.map((enrollment, index) => (
                            <motion.div
                                key={enrollment.id}
                                initial={{ opacity: 0, y: 30 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.05 }}
                                whileHover={{ y: -8 }}
                                className="h-full"
                            >
                                <Card className="h-full flex flex-col glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:shadow-primary/10 transition-all duration-300 overflow-hidden">
                                    {/* Thumbnail */}
                                    <div className="relative aspect-video overflow-hidden bg-gradient-to-br from-primary/10 to-secondary/10">
                                        {enrollment.course_thumbnail ? (
                                            <img
                                                src={enrollment.course_thumbnail}
                                                alt={enrollment.course_title || 'Course'}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                <BookOpen className="h-16 w-16 text-primary/30" />
                                            </div>
                                        )}
                                    </div>

                                    <CardHeader className="flex-grow">
                                        <CardTitle className="line-clamp-2 text-lg">
                                            {enrollment.course_title || t('myCourses.untitled')}
                                        </CardTitle>
                                    </CardHeader>

                                    {/* Stats & Progress */}
                                    <CardContent className="pt-0 space-y-4">
                                        <div className="grid grid-cols-2 gap-3 p-3 bg-muted/30 rounded-lg text-sm">
                                            <div className="flex items-center gap-2">
                                                <Video className="h-4 w-4 text-muted-foreground" />
                                                <span>{enrollment.total_videos || 0} {t('myCourses.videos')}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                                <span>{enrollment.completed_videos || 0} {t('myCourses.done')}</span>
                                            </div>
                                        </div>

                                        {/* Progress Bar */}
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-muted-foreground">{t('myCourses.progress')}</span>
                                                <span className="font-medium">
                                                    {Math.round(enrollment.progress_percentage || 0)}%
                                                </span>
                                            </div>
                                            <Progress value={enrollment.progress_percentage || 0} className="h-2" />
                                        </div>

                                        {/* Continue Button */}
                                        <Button
                                            className="w-full"
                                            asChild
                                        >
                                            <Link to={`/course-player/${enrollment.course_id}`}>
                                                <Play className="mr-2 h-4 w-4" />
                                                {t('myCourses.continue')}
                                            </Link>
                                        </Button>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-20"
                    >
                        <div className="glass-card border-white/20 dark:border-white/10 p-12 rounded-2xl shadow-xl max-w-md mx-auto">
                            <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-6 opacity-50" />
                            <h3 className="text-xl font-bold text-foreground mb-2">{t('myCourses.noCourses')}</h3>
                            <p className="text-muted-foreground mb-6">
                                {t('myCourses.enrollPrompt')}
                            </p>
                            <Button asChild>
                                <Link to="/browse-courses">
                                    <BookOpen className="mr-2 h-4 w-4" />
                                    {t('myCourses.browse')}
                                </Link>
                            </Button>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default MyCourses;
