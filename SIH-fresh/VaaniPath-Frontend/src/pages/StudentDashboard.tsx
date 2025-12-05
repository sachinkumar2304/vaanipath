import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { getAllCourses, Course } from '@/services/courses';
import { getMyEnrollments, Enrollment } from '@/services/enrollments';
import {
  BookOpen, Search, ArrowRight, Play, Video, Clock, CheckCircle2, Settings as SettingsIcon
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const StudentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useTranslation();

  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [featuredCourses, setFeaturedCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [enrollmentsRes, coursesRes] = await Promise.all([
          getMyEnrollments().catch(() => ({ enrollments: [] })),
          getAllCourses().catch(() => ({ courses: [] }))
        ]);

        setEnrollments(enrollmentsRes.enrollments || []);
        setFeaturedCourses(coursesRes.courses?.slice(0, 4) || []);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);

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
      <Header isAuthenticated userType="student" />

      <div className="container px-4 py-12 lg:py-16 relative z-10">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-foreground font-heading tracking-tight">
            {t('common.welcome')}!
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl">
            {t('dashboard.welcomeMessage')}
          </p>
        </motion.div>

        {/* Continue Learning Section */}
        {enrollments.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mb-16"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Play className="h-6 w-6 text-primary" />
                {t('common.continueLearning')}
              </h2>
              <Button variant="ghost" asChild>
                <Link to="/my-courses">
                  {t('common.all')} <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {enrollments.slice(0, 3).map((enrollment, index) => (
                <motion.div
                  key={enrollment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                >
                  <Card className="h-full flex flex-col glass-card border-white/20 dark:border-white/10 shadow-lg hover:shadow-xl transition-all duration-300">
                    <div className="relative aspect-video overflow-hidden rounded-t-xl bg-muted">
                      {enrollment.course_thumbnail ? (
                        <img
                          src={enrollment.course_thumbnail}
                          alt={enrollment.course_title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <BookOpen className="h-12 w-12 text-muted-foreground/50" />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
                        <Button size="icon" className="rounded-full h-12 w-12" asChild>
                          <Link to={`/course-player/${enrollment.course_id}`}>
                            <Play className="h-6 w-6 ml-1" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                    <CardContent className="p-4 flex-1 flex flex-col">
                      <h3 className="font-semibold text-lg mb-2 line-clamp-1">{enrollment.course_title}</h3>
                      <div className="mt-auto space-y-3">
                        <div className="flex justify-between text-sm text-muted-foreground">
                          <span>{Math.round(enrollment.progress_percentage || 0)}% {t('common.completed')}</span>
                          <span>{enrollment.completed_videos}/{enrollment.total_videos} {t('myCourses.videos')}</span>
                        </div>
                        <Progress value={enrollment.progress_percentage || 0} className="h-2" />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Featured Courses Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-primary" />
              {t('common.recentCourses')}
            </h2>
            <Button variant="ghost" asChild>
              <Link to="/browse-courses">
                {t('common.all')} <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>

          {isLoading ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-[300px] rounded-xl bg-muted/20 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {featuredCourses.map((course, index) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                >
                  <Card className="h-full flex flex-col glass-card border-white/20 dark:border-white/10 shadow-lg hover:shadow-xl transition-all duration-300">
                    <div className="relative aspect-video overflow-hidden rounded-t-xl bg-muted">
                      {course.thumbnail_url ? (
                        <img
                          src={course.thumbnail_url}
                          alt={course.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <BookOpen className="h-12 w-12 text-muted-foreground/50" />
                        </div>
                      )}
                      <Badge className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm text-foreground hover:bg-background/90">
                        {course.domain}
                      </Badge>
                    </div>
                    <CardContent className="p-4 flex-1 flex flex-col">
                      <h3 className="font-semibold text-lg mb-2 line-clamp-2">{course.title}</h3>
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-4 flex-1">
                        {course.description || t('dashboard.noDescription')}
                      </p>

                      <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                        <div className="flex items-center gap-1">
                          <Video className="h-4 w-4" />
                          <span>{course.total_videos}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>{formatDuration(course.total_duration)}</span>
                        </div>
                      </div>

                      <Button className="w-full mt-auto" asChild>
                        <Link to={`/course/${course.id}`}>{t('common.viewCourse')}</Link>
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
      <Link
        to="/settings"
        className="fixed bottom-8 right-8 z-50 p-4 rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl transition-all hover:scale-110"
      >
        <SettingsIcon className="h-6 w-6" />
      </Link>

      <Footer />
    </div>
  );
};

export default StudentDashboard;
