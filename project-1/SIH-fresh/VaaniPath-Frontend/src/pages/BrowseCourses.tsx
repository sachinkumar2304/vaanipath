import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { getAllCourses, Course } from '@/services/courses';
import { enrollInCourse, isEnrolledInCourse, getMyEnrollments } from '@/services/enrollments';
import {
    BookOpen, Search, Filter, X, Video, Clock, Languages, Users, Check
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const BrowseCourses = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { toast } = useToast();
    const { user, isTeacher } = useAuth();

    const [courses, setCourses] = useState<Course[]>([]);
    const [enrolledCourses, setEnrolledCourses] = useState<Set<string>>(new Set());
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedSubject, setSelectedSubject] = useState<string>('all');
    const [selectedLanguage, setSelectedLanguage] = useState<string>('all');
    const [isLoading, setIsLoading] = useState(true);
    const [enrollingId, setEnrollingId] = useState<string | null>(null);

    useEffect(() => {
        loadCourses();
    }, []);

    const loadCourses = async () => {
        try {
            setIsLoading(true);
            const response = await getAllCourses({
                search: searchQuery || undefined,
                domain: selectedSubject !== 'all' ? selectedSubject : undefined,
                language: selectedLanguage !== 'all' ? selectedLanguage : undefined,
            });
            setCourses(response.courses);

            // Check enrollment status efficiently
            if (user) {
                try {
                    const enrollmentsRes = await getMyEnrollments();
                    const enrolledIds = new Set(enrollmentsRes.enrollments.map(e => e.course_id));
                    setEnrolledCourses(enrolledIds);
                } catch (error) {
                    console.error('Failed to load enrollments:', error);
                }
            }
        } catch (error) {
            console.error('Failed to load courses:', error);
            toast({
                title: 'Error',
                description: 'Failed to load courses',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleEnroll = async (courseId: string, courseTitle: string) => {
        if (!user) {
            toast({
                title: 'Login Required',
                description: 'Please login to enroll in courses',
                variant: 'destructive',
            });
            navigate('/login');
            return;
        }

        try {
            setEnrollingId(courseId);
            await enrollInCourse(courseId);
            setEnrolledCourses(prev => new Set(prev).add(courseId));
            toast({
                title: 'Enrolled Successfully!',
                description: `You are now enrolled in "${courseTitle}"`,
            });
        } catch (error: any) {
            console.error('Enrollment error:', error);
            toast({
                title: 'Enrollment Failed',
                description: error.response?.data?.detail || 'Failed to enroll in course',
                variant: 'destructive',
            });
        } finally {
            setEnrollingId(null);
        }
    };

    const subjects = ['all', ...new Set(courses.map(c => c.domain))];
    const languages = ['all', 'en', 'hi', 'te', 'ta', 'mr', 'bn'];

    const formatDuration = (seconds?: number) => {
        if (!seconds) return 'No content';
        const mins = Math.floor(seconds / 60);
        if (mins < 60) return `${mins}m`;
        const hrs = Math.floor(mins / 60);
        const remainMins = mins % 60;
        return `${hrs}h ${remainMins}m`;
    };

    return (
        <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />

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
                        {t('browseCourses.title')}
                    </h1>
                    <p className="text-lg text-muted-foreground">
                        {t('browseCourses.subtitle')}
                    </p>
                </motion.div>

                {/* Search and Filters */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="glass-card border-white/20 dark:border-white/10 p-6 rounded-2xl shadow-xl mb-10"
                >
                    <div className="flex flex-col lg:flex-row gap-4">
                        {/* Search */}
                        <div className="relative flex-1">
                            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                            <Input
                                placeholder={t('browseCourses.searchPlaceholder')}
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && loadCourses()}
                                className="pl-12 h-12 bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                            />
                            {searchQuery && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                                    onClick={() => {
                                        setSearchQuery('');
                                        loadCourses();
                                    }}
                                >
                                    <X className="h-4 w-4" />
                                </Button>
                            )}
                        </div>

                        {/* Filters */}
                        <div className="flex flex-wrap gap-3">
                            <Select value={selectedSubject} onValueChange={(val) => { setSelectedSubject(val); loadCourses(); }}>
                                <SelectTrigger className="w-full lg:w-[160px] h-12 bg-background/50 border-input">
                                    <div className="flex items-center gap-2">
                                        <Filter className="h-4 w-4 text-primary" />
                                        <SelectValue placeholder={t('browseCourses.subject')} />
                                    </div>
                                </SelectTrigger>
                                <SelectContent>
                                    {subjects.map((subject) => (
                                        <SelectItem key={subject} value={subject}>
                                            {subject === 'all' ? t('browseCourses.allSubjects') : subject.charAt(0).toUpperCase() + subject.slice(1)}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>

                            <Select value={selectedLanguage} onValueChange={(val) => { setSelectedLanguage(val); loadCourses(); }}>
                                <SelectTrigger className="w-full lg:w-[160px] h-12 bg-background/50 border-input">
                                    <div className="flex items-center gap-2">
                                        <Languages className="h-4 w-4 text-primary" />
                                        <SelectValue placeholder={t('browseCourses.language')} />
                                    </div>
                                </SelectTrigger>
                                <SelectContent>
                                    {languages.map((lang) => (
                                        <SelectItem key={lang} value={lang}>
                                            {lang === 'all' ? t('browseCourses.allLanguages') : lang.toUpperCase()}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </motion.div>

                {/* Course Grid */}
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <BookOpen className="h-16 w-16 text-primary mb-4 animate-pulse" />
                        <p className="text-muted-foreground">{t('browseCourses.loading')}</p>
                    </div>
                ) : courses.length > 0 ? (
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {courses.map((course, index) => {
                            const isEnrolled = enrolledCourses.has(course.id);

                            return (
                                <motion.div
                                    key={course.id}
                                    initial={{ opacity: 0, y: 30 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.5, delay: index * 0.1 }}
                                    whileHover={{ y: -8 }}
                                    className="h-full"
                                >
                                    <Card className="h-full flex flex-col glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:shadow-primary/10 transition-all duration-300 overflow-hidden">
                                        {/* Thumbnail */}
                                        <div className="relative aspect-video overflow-hidden bg-gradient-to-br from-primary/10 to-secondary/10">
                                            {course.thumbnail_url ? (
                                                <img
                                                    src={course.thumbnail_url}
                                                    alt={course.title}
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center">
                                                    <BookOpen className="h-16 w-16 text-primary/30" />
                                                </div>
                                            )}

                                            {isEnrolled && (
                                                <div className="absolute top-3 right-3">
                                                    <Badge className="bg-green-500 hover:bg-green-600">
                                                        <Check className="h-3 w-3 mr-1" />
                                                        {t('browseCourses.enrolled')}
                                                    </Badge>
                                                </div>
                                            )}
                                        </div>

                                        <CardHeader className="flex-grow">
                                            {/* Subject & Teacher */}
                                            <div className="flex items-center justify-between mb-3">
                                                <Badge variant="secondary" className="bg-secondary/20 border-secondary/30">
                                                    {course.domain}
                                                </Badge>
                                                {course.teacher_name && (
                                                    <span className="text-xs text-muted-foreground">
                                                        {t('browseCourses.by')} {course.teacher_name}
                                                    </span>
                                                )}
                                            </div>

                                            <CardTitle className="line-clamp-2 text-lg">
                                                {course.title}
                                            </CardTitle>
                                            <p className="text-sm text-muted-foreground line-clamp-2 mt-2">
                                                {course.description || t('browseCourses.noDescription')}
                                            </p>
                                        </CardHeader>

                                        {/* Stats */}
                                        <CardContent className="pt-0">
                                            <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-muted/30 rounded-lg text-sm">
                                                <div className="flex items-center gap-2">
                                                    <Video className="h-4 w-4 text-muted-foreground" />
                                                    <span>{course.total_videos || 0} videos</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <Clock className="h-4 w-4 text-muted-foreground" />
                                                    <span>{formatDuration(course.total_duration)}</span>
                                                </div>
                                            </div>

                                            {/* Languages */}
                                            <div className="flex flex-wrap gap-1 mb-4">
                                                <Badge variant="outline" className="text-xs">
                                                    {course.source_language.toUpperCase()}
                                                </Badge>
                                                {course.target_languages.slice(0, 2).map((lang) => (
                                                    <Badge
                                                        key={lang}
                                                        variant="outline"
                                                        className="text-xs border-primary/30 text-primary bg-primary/5"
                                                    >
                                                        {lang.toUpperCase()}
                                                    </Badge>
                                                ))}
                                                {course.target_languages.length > 2 && (
                                                    <Badge variant="outline" className="text-xs">
                                                        +{course.target_languages.length - 2}
                                                    </Badge>
                                                )}
                                            </div>

                                            {/* Action Button */}
                                            {isEnrolled ? (
                                                <Button
                                                    className="w-full"
                                                    onClick={() => navigate('/my-courses')}
                                                >
                                                    {t('myCourses.continue')}
                                                </Button>
                                            ) : (
                                                <Button
                                                    className="w-full"
                                                    onClick={() => navigate(`/course/${course.id}`)}
                                                >
                                                    {t('common.viewCourse')}
                                                </Button>
                                            )}
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            );
                        })}
                    </div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-20"
                    >
                        <div className="glass-card border-white/20 dark:border-white/10 p-12 rounded-2xl shadow-xl max-w-md mx-auto">
                            <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-6 opacity-50" />
                            <h3 className="text-xl font-bold text-foreground mb-2">{t('browseCourses.noCourses')}</h3>
                            <p className="text-muted-foreground">
                                {t('browseCourses.adjustFilters')}
                            </p>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default BrowseCourses;
