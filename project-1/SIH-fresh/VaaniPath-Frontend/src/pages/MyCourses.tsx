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

const MyCourses = () => {
    const navigate = useNavigate();
    const { toast } = useToast();
    const { user } = useAuth();

    const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        loadEnrollments();
    }, [user, navigate]);

    const loadEnrollments = async () => {
        try {
            setIsLoading(true);
            const response = await getMyEnrollments();
            setEnrollments(response.enrollments);
        } catch (error) {
            console.error('Failed to load enrollments:', error);
            toast({
                title: 'Error',
                description: 'Failed to load your courses',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
        }
    };

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
                        My Courses
                    </h1>
                    <p className="text-lg text-muted-foreground">
                        Continue your learning journey
                    </p>
                </motion.div>

                {/* Course Grid */}
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <BookOpen className="h-16 w-16 text-primary mb-4 animate-pulse" />
                        <p className="text-muted-foreground">Loading your courses...</p>
                    </div>
                ) : enrollments.length > 0 ? (
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {enrollments.map((enrollment, index) => (
                            <motion.div
                                key={enrollment.id}
                                initial={{ opacity: 0, y: 30 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
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
                                            {enrollment.course_title || 'Untitled Course'}
                                        </CardTitle>
                                    </CardHeader>

                                    {/* Stats & Progress */}
                                    <CardContent className="pt-0 space-y-4">
                                        <div className="grid grid-cols-2 gap-3 p-3 bg-muted/30 rounded-lg text-sm">
                                            <div className="flex items-center gap-2">
                                                <Video className="h-4 w-4 text-muted-foreground" />
                                                <span>{enrollment.total_videos || 0} videos</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                                <span>{enrollment.completed_videos || 0} done</span>
                                            </div>
                                        </div>

                                        {/* Progress Bar */}
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-muted-foreground">Progress</span>
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
                                                Continue Learning
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
                            <h3 className="text-xl font-bold text-foreground mb-2">No courses yet</h3>
                            <p className="text-muted-foreground mb-6">
                                Enroll in courses to start your learning journey
                            </p>
                            <Button asChild>
                                <Link to="/browse-courses">
                                    <BookOpen className="mr-2 h-4 w-4" />
                                    Browse Courses
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
