import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, Clock, Languages, User, Play } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export interface Course {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  teacherName: string;
  subject: string;
  topic: string;
  duration: string;
  lectureCount: number;
  languages: string[];
  enrolled?: boolean;
}

interface CourseCardProps {
  course: Course;
  onEnroll?: (courseId: string) => void;
  viewType?: 'browse' | 'enrolled';
  index?: number;
}

export const CourseCard = ({ course, onEnroll, viewType = 'browse', index = 0 }: CourseCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, delay: index * 0.1, ease: "easeOut" }}
      whileHover={{ y: -8 }}
      className="h-full"
    >
      <Card className="h-full flex flex-col glass-card border-white/20 dark:border-white/10 shadow-xl hover:shadow-2xl hover:shadow-primary/10 transition-all duration-300 overflow-hidden group relative">
        {/* Subtle top accent */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Thumbnail with overlay */}
        <div className="relative aspect-video overflow-hidden bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-100/50 via-purple-50/50 to-teal-50/50 dark:from-blue-900/20 dark:via-purple-900/20 dark:to-teal-900/20 flex items-center justify-center">
            <BookOpen className="h-16 w-16 text-primary/20 dark:text-primary/10" />
          </div>

          {/* Play overlay on hover */}
          <div className="absolute inset-0 bg-primary/80 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
            <div className="bg-white/20 backdrop-blur-sm rounded-full p-4 transform scale-75 group-hover:scale-100 transition-transform duration-300">
              <Play className="h-8 w-8 text-white fill-white" />
            </div>
          </div>
        </div>

        <CardHeader className="p-5 pb-3 flex-grow">
          {/* Subject badge and language chips */}
          <div className="flex items-start justify-between gap-2 mb-3">
            <Badge
              variant="secondary"
              className="text-xs px-2.5 py-1 rounded-full bg-secondary/20 dark:bg-secondary/10 border border-secondary/30 text-secondary-foreground font-medium"
            >
              {course.subject}
            </Badge>
            <div className="flex gap-1 flex-wrap justify-end">
              {course.languages.slice(0, 2).map((lang) => (
                <Badge
                  key={lang}
                  variant="outline"
                  className="text-[10px] px-2 py-0.5 rounded-full border-primary/30 text-primary bg-primary/5"
                >
                  {lang}
                </Badge>
              ))}
              {course.languages.length > 2 && (
                <Badge
                  variant="outline"
                  className="text-[10px] px-2 py-0.5 rounded-full border-primary/30 text-primary bg-primary/5"
                >
                  +{course.languages.length - 2}
                </Badge>
              )}
            </div>
          </div>

          <CardTitle className="line-clamp-2 group-hover:text-primary transition-colors duration-300 text-lg font-bold text-foreground leading-tight mb-2">
            {course.title}
          </CardTitle>
          <p className="line-clamp-2 text-sm text-muted-foreground leading-relaxed">
            {course.description}
          </p>
        </CardHeader>

        <CardContent className="space-y-3 px-5 pb-4">
          {/* Teacher info */}
          <div className="flex items-center text-sm text-muted-foreground">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-secondary/20 dark:bg-secondary/10 flex items-center justify-center mr-2">
              <User className="h-3.5 w-3.5 text-secondary-foreground" />
            </div>
            <span className="truncate font-medium">{course.teacherName}</span>
          </div>

          {/* Course meta */}
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <BookOpen className="h-3.5 w-3.5 text-primary/70" />
              <span>{course.lectureCount} Lectures</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5 text-primary/70" />
              <span>{course.duration}</span>
            </div>
          </div>

          {/* Language availability */}
          <div className="flex items-center text-xs bg-accent/10 dark:bg-accent/5 rounded-lg px-3 py-2 border border-accent/20">
            <Languages className="h-3.5 w-3.5 text-accent mr-2 flex-shrink-0" />
            <span className="text-accent-foreground font-medium">
              Available in {course.languages.length} language{course.languages.length !== 1 ? 's' : ''}
            </span>
          </div>
        </CardContent>

        <CardFooter className="p-5 pt-0 mt-auto">
          {viewType === 'browse' && !course.enrolled ? (
            <Button
              className="w-full h-11 text-base font-medium shadow-md hover:shadow-lg hover:shadow-primary/20 transition-all duration-300 bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-0.5"
              onClick={() => onEnroll?.(course.id)}
            >
              Enroll Now
            </Button>
          ) : (
            <Button
              className="w-full h-11 text-base font-medium shadow-md hover:shadow-lg hover:shadow-primary/20 transition-all duration-300 bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-0.5"
              asChild
            >
              <Link to={`/course-player/${course.id}`}>
                Continue Learning
              </Link>
            </Button>
          )}
        </CardFooter>
      </Card>
    </motion.div>
  );
};
