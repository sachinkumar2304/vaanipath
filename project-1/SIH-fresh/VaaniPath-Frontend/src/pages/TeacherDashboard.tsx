import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  BookOpen, Users, Video, TrendingUp, Upload, MessageSquare,
  Edit, Eye, Clock, Languages, Play, BarChart3, Plus, CheckCircle
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { getMyCourses, Course, getTeacherStats } from '@/services/courses';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const TeacherDashboard = () => {
  const { t } = useTranslation();
  const { isTeacher, user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    totalVideos: 0,
    totalStudents: 0,
    totalViews: 0
  });

  useEffect(() => {
    if (!isTeacher) {
      navigate('/teacherlogin');
      return;
    }
    loadData();
  }, [isTeacher, navigate]);

  const loadData = async () => {
    try {
      setIsLoading(true);

      const [coursesResponse, statsResponse] = await Promise.all([
        getMyCourses(),
        getTeacherStats()
      ]);

      setCourses(coursesResponse.courses);
      setStats(statsResponse);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dashboard data',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    {
      title: t('teacherDashboard.createCourse'),
      description: t('teacherDashboard.createCourseDesc'),
      icon: Plus,
      link: '/teacher/create-course',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      hoverColor: 'hover:bg-blue-500/20'
    },
    {
      title: t('teacherDashboard.myCourses'),
      description: t('teacherDashboard.manageContent'),
      icon: BookOpen,
      link: '/teacher/courses',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      hoverColor: 'hover:bg-purple-500/20'
    },
    {
      title: t('teacherDashboard.analytics'),
      description: t('teacherDashboard.viewPerformance'),
      icon: BarChart3,
      link: '/teacher/analytics',
      color: 'from-teal-500 to-teal-600',
      bgColor: 'bg-teal-500/10',
      hoverColor: 'hover:bg-teal-500/20'
    },
    {
      title: t('teacherDashboard.studentDoubts'),
      description: t('teacherDashboard.answerQuestions'),
      icon: MessageSquare,
      link: '/teacher/doubts',
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      hoverColor: 'hover:bg-orange-500/20'
    },
  ];

  return (
    <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
      <PremiumBackground />
      <Header isAuthenticated userType="teacher" />

      <div className="container px-4 py-12 lg:py-16 relative z-10">
        {/* Hero Section */}
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
            {t('teacherDashboard.welcomeTeacher')}, {user?.full_name?.split(' ')[0] || 'Teacher'}!
          </h1>
          <p className="text-lg text-muted-foreground">
            {t('teacherDashboard.subtitle')}
          </p>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-10"
        >
          {quickActions.map((action, index) => (
            <Link key={index} to={action.link}>
              <Card className={`glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group ${action.bgColor} ${action.hoverColor}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${action.color} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <action.icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-foreground mb-1">{action.title}</h3>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </motion.div>

        {/* Analytics Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-10"
        >
          <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {t('teacherDashboard.totalVideos')}
              </CardTitle>
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Video className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {isLoading ? '...' : stats.totalVideos}
              </div>
              <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-600" />
                Uploaded lectures
              </p>
            </CardContent>
          </Card>

          <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {t('teacherDashboard.totalStudents')}
              </CardTitle>
              <div className="p-2 rounded-lg bg-purple-500/10">
                <Users className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {isLoading ? '...' : stats.totalStudents}
              </div>
              <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-600" />
                Learning from you
              </p>
            </CardContent>
          </Card>

          <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {t('teacherDashboard.totalViews')}
              </CardTitle>
              <div className="p-2 rounded-lg bg-teal-500/10">
                <Eye className="h-4 w-4 text-teal-600 dark:text-teal-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {isLoading ? '...' : stats.totalViews}
              </div>
              <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-600" />
                Across all videos
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Courses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-xl font-bold text-foreground">{t('teacherDashboard.recentCourses')}</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/teacher/courses">{t('teacherDashboard.viewAll')}</Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">{t('browseCourses.loading')}</div>
              ) : courses.length > 0 ? (
                courses.slice(0, 3).map((course) => (
                  <div
                    key={course.id}
                    className="glass-card border-white/20 dark:border-white/10 p-4 rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 group"
                  >
                    <div className="flex items-start gap-4">
                      {/* Thumbnail */}
                      <div className="w-24 h-16 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center flex-shrink-0 overflow-hidden">
                        {course.thumbnail_url ? (
                          <img src={course.thumbnail_url} alt={course.title} className="w-full h-full object-cover" />
                        ) : (
                          <Play className="h-8 w-8 text-primary/60" />
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">
                            {course.title}
                          </h4>
                          <Badge variant="secondary" className="flex-shrink-0">
                            {course.domain}
                          </Badge>
                        </div>

                        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground mb-3">
                          <span className="flex items-center gap-1">
                            <Video className="h-3 w-3" />
                            {course.total_videos || 0} videos
                          </span>
                          <span className="flex items-center gap-1">
                            <Languages className="h-3 w-3" />
                            {course.target_languages.length} languages
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2 flex-shrink-0">
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/teacher/course/${course.id}`}>
                            <Edit className="h-4 w-4" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
                    <Video className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-bold text-foreground mb-2">{t('teacherDashboard.noCourses')}</h3>
                  <p className="text-muted-foreground mb-4">
                    {t('teacherDashboard.createFirst')}
                  </p>
                  <Button asChild>
                    <Link to="/teacher/create-course">
                      <Plus className="mr-2 h-4 w-4" />
                      {t('teacherDashboard.createCourse')}
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
