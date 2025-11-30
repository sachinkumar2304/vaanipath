export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  points: number;
}

export interface Quiz {
  id: string;
  courseId: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  totalPoints: number;
  passingScore: number;
}

export const dummyQuizzes: Quiz[] = [
  {
    id: 'quiz1',
    courseId: '1',
    title: 'Python Basics Quiz',
    description: 'Test your understanding of Python fundamentals',
    totalPoints: 50,
    passingScore: 35,
    questions: [
      {
        id: 'q1',
        question: 'What is the correct way to declare a variable in Python?',
        options: ['var x = 5', 'x = 5', 'int x = 5', 'let x = 5'],
        correctAnswer: 1,
        points: 10
      },
      {
        id: 'q2',
        question: 'Which data type is mutable in Python?',
        options: ['Tuple', 'String', 'List', 'Integer'],
        correctAnswer: 2,
        points: 10
      },
      {
        id: 'q3',
        question: 'What does the len() function do?',
        options: ['Returns the length of an object', 'Returns the type', 'Returns the value', 'Returns nothing'],
        correctAnswer: 0,
        points: 10
      },
      {
        id: 'q4',
        question: 'How do you start a comment in Python?',
        options: ['//', '/*', '#', '--'],
        correctAnswer: 2,
        points: 10
      },
      {
        id: 'q5',
        question: 'What is the output of print(type([]))?',
        options: ['<class "array">', '<class "list">', '<class "tuple">', '<class "dict">'],
        correctAnswer: 1,
        points: 10
      }
    ]
  },
  {
    id: 'quiz2',
    courseId: '2',
    title: 'Web Development Fundamentals',
    description: 'Test your HTML, CSS and JavaScript knowledge',
    totalPoints: 40,
    passingScore: 28,
    questions: [
      {
        id: 'q1',
        question: 'What does HTML stand for?',
        options: ['Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Markup Language'],
        correctAnswer: 0,
        points: 10
      },
      {
        id: 'q2',
        question: 'Which CSS property is used to change text color?',
        options: ['text-color', 'font-color', 'color', 'text-style'],
        correctAnswer: 2,
        points: 10
      },
      {
        id: 'q3',
        question: 'What is the correct JavaScript syntax to change the content of an HTML element?',
        options: ['document.getElement("p").innerHTML = "Hello"', 'document.getElementById("demo").innerHTML = "Hello"', '#demo.innerHTML = "Hello"', 'document.getElementByName("p").innerHTML = "Hello"'],
        correctAnswer: 1,
        points: 10
      },
      {
        id: 'q4',
        question: 'Which HTML tag is used to define an internal style sheet?',
        options: ['<css>', '<script>', '<style>', '<styles>'],
        correctAnswer: 2,
        points: 10
      }
    ]
  },
  {
    id: 'quiz3',
    courseId: '3',
    title: 'Data Science Intro',
    description: 'Basics of Data Science and Machine Learning',
    totalPoints: 30,
    passingScore: 20,
    questions: [
      {
        id: 'q1',
        question: 'Which library is primarily used for data manipulation in Python?',
        options: ['NumPy', 'Pandas', 'Matplotlib', 'Scikit-learn'],
        correctAnswer: 1,
        points: 10
      },
      {
        id: 'q2',
        question: 'What is a supervised learning algorithm?',
        options: ['K-Means', 'Linear Regression', 'Apriori', 'PCA'],
        correctAnswer: 1,
        points: 10
      },
      {
        id: 'q3',
        question: 'What is the purpose of a confusion matrix?',
        options: ['To confuse the user', 'To visualize the performance of an algorithm', 'To clean data', 'To sort data'],
        correctAnswer: 1,
        points: 10
      }
    ]
  },
  {
    id: 'quiz4',
    courseId: '4',
    title: 'React Mastery',
    description: 'Advanced concepts in React',
    totalPoints: 30,
    passingScore: 20,
    questions: [
      {
        id: 'q1',
        question: 'What hook is used for side effects?',
        options: ['useState', 'useEffect', 'useContext', 'useReducer'],
        correctAnswer: 1,
        points: 10
      },
      {
        id: 'q2',
        question: 'What is the virtual DOM?',
        options: ['A direct copy of the real DOM', 'A lightweight copy of the real DOM', 'A database', 'A browser extension'],
        correctAnswer: 1,
        points: 10
      },
      {
        id: 'q3',
        question: 'How do you pass data to a child component?',
        options: ['State', 'Props', 'Context', 'Refs'],
        correctAnswer: 1,
        points: 10
      }
    ]
  }
];
