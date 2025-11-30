import { useState, useEffect } from 'react';
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import {
  Video, Trash2, Plus, Search, Edit, BookOpen,
  Filter, X, Clock, Users
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { getMyCourses, deleteCourse, Course } from '@/services/courses';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { motion } from 'framer-motion';

const TeacherCourses = () => {
  const { isTeacher } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [courses, setCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isTeacher) {
      navigate('/teacherlogin');
      return;
    }
    loadCourses();
  }, [isTeacher, navigate]);

  const loadCourses = async () => {
    try {
      setIsLoading(true);
      const response = await getMyCourses();
      setCourses(response.courses);
    } catch (error) {
      console.error('Failed to load courses:', error);
      toast({
        title: 'Error',
        description: 'Failed to load your courses',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (courseId: string, courseTitle: string) => {
    try {
      await deleteCourse(courseId);
      toast({
        title: 'Course Deleted',
        description: `"${courseTitle}" has been removed successfully`,
      });
      loadCourses();
    } catch (error: any) {
      console.error('Delete error:', error);
      toast({
        title: 'Delete Failed',
        description: error.response?.data?.detail || 'Failed to delete course',
        variant: 'destructive'
      });
    }
  };

  const subjects = ['all', ...new Set(courses.map(c => c.domain))];

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (course.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSubject = selectedSubject === 'all' || course.domain === selectedSubject;

    return matchesSearch && matchesSubject;
  });

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
      <Header isAuthenticated userType="teacher" />

      <div className="container px-4 py-12 lg:py-16 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-10"
        >
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-2xl bg-primary/10 backdrop-blur-md border border-primary/20">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-3 text-foreground font-heading tracking-tight">
              My Courses
            </h1>
            <p className="text-lg text-muted-foreground">
              Manage your courses and track student engagement
            </p>
          </div>
          <Button
            asChild
            className="shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
          >
            <Link to="/teacher/create-course">
              <Plus className="mr-2 h-5 w-5" />
              Create New Course
            </Link>
          </Button>
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
                placeholder="Search courses by title or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 h-12 bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
              />
              {searchQuery && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                  onClick={() => setSearchQuery('')}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>

            {/* Subject Filter */}
            <Select value={selectedSubject} onValueChange={setSelectedSubject}>
              <SelectTrigger className="w-full lg:w-[200px] h-12 bg-background/50 border-input">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-primary" />
                  <SelectValue placeholder="Subject" />
                </div>
              </SelectTrigger>
              <SelectContent>
                {subjects.map((subject) => (
                  <SelectItem key={subject} value={subject}>
                    {subject === 'all' ? 'All Subjects' : subject.charAt(0).toUpperCase() + subject.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Active Filters */}
          {(selectedSubject !== 'all' || searchQuery) && (
            <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-border/50">
              <span className="text-sm text-muted-foreground">Active filters:</span>
              {searchQuery && (
                <Badge variant="secondary" className="gap-1">
                  Search: {searchQuery}
                  <X className="h-3 w-3 cursor-pointer" onClick={() => setSearchQuery('')} />
                </Badge>
              )}
              {selectedSubject !== 'all' && (
                <Badge variant="secondary" className="gap-1">
                  {selectedSubject.charAt(0).toUpperCase() + selectedSubject.slice(1)}
                  <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedSubject('all')} />
                </Badge>
              )}
            </div>
          )}
        </motion.div>

        {/* Course Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <BookOpen className="h-16 w-16 text-primary mb-4 animate-pulse" />
            <p className="text-muted-foreground">Loading your courses...</p>
          </div>
        ) : filteredCourses.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredCourses.map((course, index) => (
              <motion.div
                key={course.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -8 }}
                className="h-full"
              >
                <Card className="h-full flex flex-col glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:shadow-primary/10 transition-all duration-300 overflow-hidden group">
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

                    {/* Overlay on Hover */}
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        asChild
                        className="backdrop-blur-sm"
                      >
                        <Link to={`/teacher/course/${course.id}`}>
                          <Edit className="h-4 w-4 mr-2" />
                          Manage
                        </Link>
                      </Button>
                    </div>
                  </div>

                  <CardHeader className="flex-grow">
                    {/* Subject Badge */}
                    <div className="mb-3">
                      <Badge variant="secondary" className="bg-secondary/20 border-secondary/30">
                        {course.domain}
                      </Badge>
                    </div>

                    <CardTitle className="line-clamp-2 text-lg group-hover:text-primary transition-colors">
                      {course.title}
                    </CardTitle>
                    <p className="text-sm text-muted-foreground line-clamp-2 mt-2">
                      {course.description || 'No description provided'}
                    </p>
                  </CardHeader>

                  {/* Stats */}
                  <CardContent className="pt-0">
                    <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-muted/30 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Video className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{course.total_videos || 0} videos</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{formatDuration(course.total_duration)}</span>
                      </div>
                    </div>

                    {/* Languages */}
                    <div className="flex flex-wrap gap-1 mb-4">
                      {course.target_languages.slice(0, 3).map((lang) => (
                        <Badge
                          key={lang}
                          variant="outline"
                          className="text-xs border-primary/30 text-primary bg-primary/5"
                        >
                          {lang.toUpperCase()}
                        </Badge>
                      ))}
                      {course.target_languages.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{course.target_languages.length - 3}
                        </Badge>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-4 border-t border-border/50">
                      <Button variant="ghost" size="sm" asChild className="text-primary hover:text-primary/80 p-0 h-auto font-medium">
                        <Link to={`/course-player/${course.id}`}>
                          View Course
                        </Link>
                      </Button>

                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" asChild className="h-8 w-8 p-0">
                          <Link to={`/teacher/course/${course.id}`}>
                            <Edit className="h-4 w-4" />
                          </Link>
                        </Button>
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-destructive hover:text-destructive">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete Course?</AlertDialogTitle>
                              <AlertDialogDescription>
                                Are you sure you want to delete "{course.title}"? This will also delete all videos in this course. This action cannot be undone.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() => handleDelete(course.id, course.title)}
                                className="bg-destructive hover:bg-destructive/90"
                              >
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </div>
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
              <h3 className="text-xl font-bold text-foreground mb-2">No courses found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery || selectedSubject !== 'all'
                  ? 'Try adjusting your filters or search query'
                  : 'Create your first course to start teaching'}
              </p>
              <Button asChild>
                <Link to="/teacher/create-course">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Course
                </Link>
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default TeacherCourses;
