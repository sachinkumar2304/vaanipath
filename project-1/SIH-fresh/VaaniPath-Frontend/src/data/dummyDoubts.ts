export interface Doubt {
  id: string;
  studentName: string;
  studentId: string;
  courseName: string;
  lectureNumber: string;
  subject: string;
  question: string;
  timestamp: string;
  status: 'pending' | 'answered';
  answer?: string;
}

// TODO: Replace with backend API
// GET /api/doubts - Fetch all doubts (for teachers)
// GET /api/doubts?studentId=xxx - Fetch student's doubts
// POST /api/doubts - Submit new doubt
// PUT /api/doubts/:id - Update doubt (add answer)

export const dummyDoubts: Doubt[] = [
  {
    id: '1',
    studentName: 'Priya Sharma',
    studentId: 'student1',
    courseName: 'Introduction to Programming',
    lectureNumber: '1.2',
    subject: 'Variables and Data Types',
    question: 'Can you explain the difference between let and const in JavaScript?',
    timestamp: '2024-01-15T10:30:00',
    status: 'answered',
    answer: 'let allows you to reassign values, while const creates a constant reference that cannot be reassigned.'
  },
  {
    id: '2',
    studentName: 'Rahul Kumar',
    studentId: 'student2',
    courseName: 'Web Development Basics',
    lectureNumber: '2.1',
    subject: 'HTML Fundamentals',
    question: 'What is the difference between div and span tags?',
    timestamp: '2024-01-15T14:20:00',
    status: 'pending'
  },
  {
    id: '3',
    studentName: 'Ananya Patel',
    studentId: 'student3',
    courseName: 'Data Structures',
    lectureNumber: '3.3',
    subject: 'Linked Lists',
    question: 'How do we reverse a singly linked list?',
    timestamp: '2024-01-16T09:15:00',
    status: 'pending'
  }
];
