import { useState, useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { AnimatePresence } from "framer-motion";
import { WelcomeIntro } from "@/components/WelcomeIntro";

// Pages
import LandingPage from "./pages/LandingPage";
import StudentLogin from "./pages/StudentLogin";
import TeacherLogin from "./pages/TeacherLogin";
import AdminLogin from "./pages/AdminLogin";
import StudentDashboard from "./pages/StudentDashboard";
import StudentDoubts from "./pages/StudentDoubts";
import CourseDetails from "./pages/CourseDetails";
import CourseDetail from "./pages/CourseDetail";
import StudentQuizzes from "./pages/StudentQuizzes";
import StudentCertificate from "./pages/StudentCertificate";
import StudentRewards from "./pages/StudentRewards";
import AIRoadmap from "./pages/AIRoadmap";
import StudentFeedback from "./pages/StudentFeedback";
import PodcastPage from "./pages/PodcastPage";
import TeacherDashboard from "./pages/TeacherDashboard";
import TeacherUpload from "./pages/TeacherUpload";
import TeacherCourses from "./pages/TeacherCourses";
import CreateCourse from "./pages/CreateCourse";
import CourseManagement from "./pages/CourseManagement";
import TeacherQuizzes from "./pages/TeacherQuizzes";
import TeacherDoubts from "./pages/TeacherDoubts";
import TeacherAnalytics from "./pages/TeacherAnalytics";
import AdminDashboard from "./pages/AdminDashboard";
import TutorsList from "./pages/TutorsList";
import StudentsList from "./pages/StudentsList";
import AdminCourses from "./pages/AdminCourses";
import BrowseCourses from "./pages/BrowseCourses";
import MyCourses from "./pages/MyCourses";
import CoursePlayer from "./pages/CoursePlayer";
import NotFound from "./pages/NotFound";
import { Settings } from "./pages/Settings";
import CommunitiesPage from "./features/community/pages/CommunitiesPage";
import CommunityDetailPage from "./features/community/pages/CommunityDetailPage";

const queryClient = new QueryClient();

const AppContent = () => {
  const [showWelcome, setShowWelcome] = useState(true);

  // Only show welcome on first visit (persisted across reloads)
  useEffect(() => {
    const hasVisited = sessionStorage.getItem("hasVisited");
    if (hasVisited) {
      setShowWelcome(false);
    }
  }, []);

  const handleWelcomeComplete = () => {
    setShowWelcome(false);
    sessionStorage.setItem("hasVisited", "true");
  };

  return (
    <>
      <AnimatePresence mode="wait">
        {showWelcome && <WelcomeIntro onComplete={handleWelcomeComplete} />}
      </AnimatePresence>

      {!showWelcome && (
        <Routes>
          {/* Landing and Auth Routes */}
          <Route path="/" element={<Navigate to="/landingpage" replace />} />
          <Route path="/landingpage" element={<LandingPage />} />
          <Route path="/login" element={<StudentLogin />} />
          <Route path="/teacherlogin" element={<TeacherLogin />} />
          <Route path="/admin" element={<AdminLogin />} />

          {/* Admin Routes */}
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/tutors" element={<TutorsList />} />
          <Route path="/admin/students" element={<StudentsList />} />
          <Route path="/admin/courses" element={<AdminCourses />} />

          {/* Student Routes */}
          <Route path="/homepage" element={<StudentDashboard />} />
          <Route path="/enrolled" element={<MyCourses />} />
          <Route path="/doubts" element={<StudentDoubts />} />
          <Route path="/course/:courseId" element={<CourseDetails />} />
          <Route path="/content/:videoId" element={<CourseDetail />} />
          <Route path="/quiz/:courseId" element={<StudentQuizzes />} />
          <Route path="/certificate/:courseId" element={<StudentCertificate />} />
          <Route path="/rewards" element={<StudentRewards />} />
          <Route path="/roadmap" element={<AIRoadmap />} />
          <Route path="/feedback" element={<StudentFeedback />} />
          <Route path="/podcast" element={<PodcastPage />} />
          <Route path="/browse-courses" element={<BrowseCourses />} />
          <Route path="/my-courses" element={<MyCourses />} />
          <Route path="/course-player/:courseId" element={<CoursePlayer />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/community/:communityId" element={<CommunityDetailPage />} />
          <Route path="/community" element={<Navigate to="/communities" replace />} />
          <Route path="/communities" element={<CommunitiesPage />} />

          {/* Teacher Routes */}
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/teacher/upload" element={<TeacherUpload />} />
          <Route path="/teacher/courses" element={<TeacherCourses />} />
          <Route path="/teacher/create-course" element={<CreateCourse />} />
          <Route path="/teacher/course/:courseId" element={<CourseManagement />} />
          <Route path="/teacher/quizzes" element={<TeacherQuizzes />} />
          <Route path="/teacher/doubts" element={<TeacherDoubts />} />
          <Route path="/teacher/analytics" element={<TeacherAnalytics />} />

          {/* Catch-all route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      )}
    </>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <AppContent />
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
