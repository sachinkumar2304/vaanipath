import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { getCourseById, CourseWithVideos } from '@/services/courses';
import { enrollInCourse, getMyEnrollments } from '@/services/enrollments';
import {
  PlayCircle, CheckCircle2, Clock, ChevronLeft,
  BookOpen, Video, Users, Play
} from 'lucide-react';
import { motion } from 'framer-motion';

const CourseDetails = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const { user, isTeacher } = useAuth();
  const { toast } = useToast();

  const [course, setCourse] = useState<CourseWithVideos | null>(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isEnrolling, setIsEnrolling] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (courseId) {
      loadData();
    }
  }, [user, courseId, navigate]);

  const loadData = async () => {
    if (!courseId) return;

    try {
      setIsLoading(true);
      const [courseData, enrollmentsRes] = await Promise.all([
        getCourseById(courseId),
        getMyEnrollments().catch(() => ({ enrollments: [] }))
      ]);

      setCourse(courseData);

      const enrolled = enrollmentsRes.enrollments?.some(
        (e: any) => e.course_id === courseId
      );
      setIsEnrolled(!!enrolled);

    } catch (error) {
      console.error('Failed to load course data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load course details',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnroll = async () => {
    if (!courseId) return;

    try {
      setIsEnrolling(true);
      await enrollInCourse(courseId);

      toast({
        title: 'Success!',
        description: 'You have successfully enrolled in the course.',
      });

      setIsEnrolled(true);
      // Navigate to player after short delay
      setTimeout(() => {
        navigate(`/course-player/${courseId}`);
      }, 1500);

    } catch (error: any) {
      console.error('Enrollment failed:', error);
      toast({
        title: 'Enrollment Failed',
        description: error.response?.data?.detail || 'Failed to enroll in course',
        variant: 'destructive',
      });
    } finally {
      setIsEnrolling(false);
    }
  };

  if (isLoading) {
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

  if (!course) {
    return (
      <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
        <PremiumBackground />
        <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
        <div className="container px-4 py-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Course not found</h2>
          <Button asChild>
            <Link to="/browse-courses">Browse Courses</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
      <PremiumBackground />
      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />

      <div className="container px-4 py-12 lg:py-16 relative z-10">
        <Button
          variant="ghost"
          className="mb-8"
          onClick={() => navigate(-1)}
        >
          <ChevronLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        <div className="grid lg:grid-cols-[1fr_350px] gap-8">
          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-4">
                <Badge variant="secondary" className="text-sm px-3 py-1">
                  {course.domain}
                </Badge>
                <div className="flex items-center text-sm text-muted-foreground">
                  <Clock className="h-4 w-4 mr-1" />
                  {Math.floor(course.total_duration / 60)}m {course.total_duration % 60}s
                </div>
              </div>

              <h1 className="text-4xl md:text-5xl font-bold mb-6 text-foreground font-heading tracking-tight">
                {course.title}
              </h1>

              <p className="text-lg text-muted-foreground leading-relaxed mb-8">
                {course.description || 'No description available for this course.'}
              </p>

              <div className="flex flex-wrap gap-2 mb-8">
                {course.target_languages.map((lang) => (
                  <Badge key={lang} variant="outline" className="border-primary/30 text-primary bg-primary/5">
                    {lang.toUpperCase()}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Course Content Preview */}
            <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl mb-8">
              <CardContent className="p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Video className="h-5 w-5 text-primary" />
                  Course Content ({course.total_videos} videos)
                </h3>
                <div className="space-y-3">
                  {course.videos.map((video, index) => (
                    <div
                      key={video.id}
                      className="flex items-center gap-4 p-3 rounded-lg bg-muted/30 border border-border/50"
                    >
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <span className="text-sm font-medium text-primary">{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{video.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {Math.floor(video.duration / 60)}m {video.duration % 60}s
                        </p>
                      </div>
                      {isEnrolled ? (
                        <PlayCircle className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <div className="h-5 w-5" />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="space-y-6"
          >
            <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl sticky top-24">
              <div className="aspect-video relative bg-muted rounded-t-xl overflow-hidden">
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
              </div>
              <CardContent className="p-6">
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-muted-foreground">Instructor</span>
                    <span className="font-medium">{course.teacher_name || 'VaaniPath Instructor'}</span>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-muted-foreground">Videos</span>
                    <span className="font-medium">{course.total_videos}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Language</span>
                    <span className="font-medium">{course.source_language.toUpperCase()}</span>
                  </div>
                </div>

                {isEnrolled ? (
                  <Button
                    className="w-full text-lg h-12 shadow-lg shadow-primary/20"
                    onClick={() => navigate(`/course-player/${courseId}`)}
                  >
                    <Play className="mr-2 h-5 w-5" />
                    Go to Course
                  </Button>
                ) : (
                  <Button
                    className="w-full text-lg h-12 shadow-lg shadow-primary/20"
                    onClick={handleEnroll}
                    disabled={isEnrolling}
                  >
                    {isEnrolling ? 'Enrolling...' : 'Enroll Now'}
                  </Button>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetails;
