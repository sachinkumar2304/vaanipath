import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { CourseCard } from '@/components/CourseCard';
import { BookOpen, Loader2 } from 'lucide-react';
import { getEnrolledVideos, type Video } from '@/services/videos';
import { useToast } from '@/hooks/use-toast';

const EnrolledCourses = () => {
  const { user, isTeacher } = useAuth();
  const { toast } = useToast();
  const [courses, setCourses] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEnrolledCourses();
  }, []);

  const fetchEnrolledCourses = async () => {
    try {
      setLoading(true);
      const response = await getEnrolledVideos(1, 100);
      setCourses(response.videos);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load enrolled courses',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const mapVideoToCourse = (video: Video) => ({
    id: video.id,
    title: video.title,
    description: video.description,
    subject: video.domain,
    teacherName: 'Teacher',
    imageUrl: video.thumbnail_url || '/placeholder.svg',
    totalLectures: 1,
    availableLanguages: video.target_languages,
    enrolled: true,
    thumbnail: video.thumbnail_url,
    topic: video.domain,
    duration: `${video.duration || 0} min`,
    lectureCount: 1,
    languages: video.target_languages,
  });

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />

      <div className="container px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            My Courses
          </h1>
          <p className="text-muted-foreground">
            Continue your learning journey
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : courses.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {courses.map((video) => (
              <CourseCard
                key={video.id}
                course={mapVideoToCourse(video)}
                viewType="enrolled"
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center rounded-full bg-muted p-6 mb-4">
              <BookOpen className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No Enrolled Courses Yet</h3>
            <p className="text-muted-foreground mb-4">
              Start learning by enrolling in courses from the browse page
            </p>
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default EnrolledCourses;
