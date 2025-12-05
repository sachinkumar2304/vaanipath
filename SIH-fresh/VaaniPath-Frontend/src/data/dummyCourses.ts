import { Course } from '@/components/CourseCard';

// Dummy course data for demonstration
// TODO: Replace with actual API calls when backend is integrated
// API endpoints:
// - GET /api/courses - Fetch all available courses
// - GET /api/student/enrolled-courses - Fetch student's enrolled courses
// - POST /api/courses/:id/enroll - Enroll in a course

export const dummyCourses: Course[] = [
  {
    id: '1',
    title: 'Introduction to Python Programming',
    description: 'Learn Python basics, data structures, and programming fundamentals in your preferred language',
    thumbnail: '/placeholder-course1.jpg',
    teacherName: 'Dr. Priya Sharma',
    subject: 'Computer Science',
    topic: 'Programming',
    duration: '6 weeks',
    lectureCount: 24,
    languages: ['English', 'Hindi', 'Tamil', 'Telugu', 'Bengali'],
    enrolled: false,
  },
  {
    id: '2',
    title: 'Advanced Mathematics - Calculus',
    description: 'Master differential and integral calculus with real-world applications',
    thumbnail: '/placeholder-course2.jpg',
    teacherName: 'Prof. Rajesh Kumar',
    subject: 'Mathematics',
    topic: 'Calculus',
    duration: '8 weeks',
    lectureCount: 32,
    languages: ['English', 'Hindi', 'Marathi', 'Gujarati'],
    enrolled: false,
  },
  {
    id: '3',
    title: 'Physics: Mechanics and Motion',
    description: 'Understand the fundamentals of classical mechanics and Newton\'s laws',
    thumbnail: '/placeholder-course3.jpg',
    teacherName: 'Dr. Anita Desai',
    subject: 'Physics',
    topic: 'Mechanics',
    duration: '5 weeks',
    lectureCount: 20,
    languages: ['English', 'Hindi', 'Kannada', 'Malayalam'],
    enrolled: true,
  },
  {
    id: '4',
    title: 'Organic Chemistry Fundamentals',
    description: 'Explore the world of carbon compounds and organic reactions',
    thumbnail: '/placeholder-course4.jpg',
    teacherName: 'Prof. Suresh Patel',
    subject: 'Chemistry',
    topic: 'Organic Chemistry',
    duration: '7 weeks',
    lectureCount: 28,
    languages: ['English', 'Hindi', 'Bengali', 'Punjabi'],
    enrolled: false,
  },
  {
    id: '5',
    title: 'Indian History: Ancient Civilizations',
    description: 'Journey through ancient India - from Indus Valley to Mauryan Empire',
    thumbnail: '/placeholder-course5.jpg',
    teacherName: 'Dr. Meera Reddy',
    subject: 'History',
    topic: 'Ancient India',
    duration: '4 weeks',
    lectureCount: 16,
    languages: ['English', 'Hindi', 'Tamil', 'Telugu', 'Malayalam', 'Kannada'],
    enrolled: true,
  },
  {
    id: '6',
    title: 'English Literature: Shakespeare',
    description: 'Explore the works of William Shakespeare with contextual analysis',
    thumbnail: '/placeholder-course6.jpg',
    teacherName: 'Prof. Arjun Mehta',
    subject: 'Literature',
    topic: 'English Literature',
    duration: '6 weeks',
    lectureCount: 18,
    languages: ['English', 'Hindi', 'Bengali'],
    enrolled: false,
  },
];

export interface Lecture {
  id: string;
  courseId: string;
  title: string;
  description: string;
  duration: string; // e.g., "45 mins"
  videoUrl: string;
  completed?: boolean;
  order: number;
}

// Dummy lecture data for courses
export const dummyLectures: Record<string, Lecture[]> = {
  '1': [
    {
      id: 'l1-1',
      courseId: '1',
      title: 'Introduction to Python',
      description: 'What is Python and why should you learn it?',
      duration: '30 mins',
      videoUrl: 'https://example.com/video1',
      completed: false,
      order: 1,
    },
    {
      id: 'l1-2',
      courseId: '1',
      title: 'Setting Up Your Environment',
      description: 'Installing Python and your first program',
      duration: '45 mins',
      videoUrl: 'https://example.com/video2',
      completed: false,
      order: 2,
    },
    {
      id: 'l1-3',
      courseId: '1',
      title: 'Variables and Data Types',
      description: 'Understanding Python data types and variables',
      duration: '50 mins',
      videoUrl: 'https://example.com/video3',
      completed: false,
      order: 3,
    },
  ],
  '3': [
    {
      id: 'l3-1',
      courseId: '3',
      title: 'Introduction to Mechanics',
      description: 'Overview of classical mechanics concepts',
      duration: '40 mins',
      videoUrl: 'https://example.com/video4',
      completed: true,
      order: 1,
    },
    {
      id: 'l3-2',
      courseId: '3',
      title: 'Newton\'s First Law',
      description: 'Understanding inertia and the first law of motion',
      duration: '55 mins',
      videoUrl: 'https://example.com/video5',
      completed: true,
      order: 2,
    },
    {
      id: 'l3-3',
      courseId: '3',
      title: 'Newton\'s Second Law',
      description: 'Force, mass, and acceleration relationship',
      duration: '60 mins',
      videoUrl: 'https://example.com/video6',
      completed: false,
      order: 3,
    },
  ],
  '5': [
    {
      id: 'l5-1',
      courseId: '5',
      title: 'Indus Valley Civilization',
      description: 'Exploring the first urban civilization of India',
      duration: '50 mins',
      videoUrl: 'https://example.com/video7',
      completed: true,
      order: 1,
    },
    {
      id: 'l5-2',
      courseId: '5',
      title: 'Vedic Period',
      description: 'Understanding the Vedic age and its significance',
      duration: '45 mins',
      videoUrl: 'https://example.com/video8',
      completed: false,
      order: 2,
    },
  ],
};
