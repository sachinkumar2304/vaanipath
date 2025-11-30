import { Link, useLocation, useNavigate } from 'react-router-dom';
import { GraduationCap, Menu, X, LogOut, Trophy, User, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from './ThemeToggle';
import { useState } from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface HeaderProps {
  isAuthenticated?: boolean;
  userType?: 'student' | 'teacher';
  userName?: string;
  onLogout?: () => void;
}

export const Header = ({ isAuthenticated = false, userType, userName = "User", onLogout }: HeaderProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    // TODO: Integrate with backend logout API
    // Call API: POST /api/auth/logout
    if (onLogout) onLogout();
    setMobileMenuOpen(false);
    navigate('/landingpage');
  };

  // TODO: Fetch student points from backend
  // GET /api/students/:studentId/points
  const studentPoints = 850;

  const getNavLinks = () => {
    if (!isAuthenticated) {
      return [
        { path: '/landingpage', label: 'Home' },
        { path: '/login', label: 'Student Login' },
        { path: '/teacherlogin', label: 'Teacher Login' },
      ];
    }

    if (userType === 'student') {
      return [
        { path: '/homepage', label: 'Browse Courses' },
        { path: '/enrolled', label: 'My Courses' },
        { path: '/doubts', label: 'Ask Doubts' },
        { path: '/community', label: 'Community' },
        { path: '/rewards', label: 'Rewards' },
        { path: '/roadmap', label: 'AI Roadmap' },
        { path: '/podcast', label: 'Podcast' },
        { path: '/feedback', label: 'Feedback' },
      ];
    }

    if (userType === 'teacher') {
      return [
        { path: '/teacher/dashboard', label: 'Dashboard' },
        { path: '/teacher/courses', label: 'My Courses' },
        { path: '/teacher/upload', label: 'Upload Content' },
        { path: '/teacher/quizzes', label: 'Create Quiz' },
        { path: '/teacher/doubts', label: 'Student Doubts' },
      ];
    }

    return [];
  };

  const navLinks = getNavLinks();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to={isAuthenticated ? (userType === 'student' ? '/homepage' : '/teacher/dashboard') : '/landingpage'} className="flex items-center space-x-2">
          <div className="rounded-lg bg-gradient-primary p-2">
            <GraduationCap className="h-6 w-6 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            VAANIपथ
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`text-sm font-medium transition-colors hover:text-primary ${isActive(link.path) ? 'text-primary' : 'text-foreground/80'
                }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right side actions */}
        <div className="flex items-center space-x-2">
          {isAuthenticated && userType === 'student' && (
            <Link to="/rewards" className="hidden md:flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-primary text-primary-foreground hover:opacity-90 transition-opacity">
              <Trophy className="h-4 w-4" />
              <span className="font-semibold">{studentPoints}</span>
            </Link>
          )}
          <ThemeToggle />

          {isAuthenticated ? (
            <div className="hidden md:block">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar className="h-10 w-10 border border-border">
                      <AvatarImage src="/placeholder-avatar.jpg" alt={userName} />
                      <AvatarFallback className="bg-primary/10 text-primary">
                        {userName.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{userName}</p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {userType === 'student' ? 'student@example.com' : 'teacher@example.com'}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="cursor-pointer text-destructive focus:text-destructive" onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : null}

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-background">
          <nav className="container px-4 py-4 space-y-2">
            {isAuthenticated && (
              <div className="flex items-center gap-3 px-4 py-3 mb-2 bg-muted/50 rounded-lg">
                <Avatar className="h-10 w-10 border border-border">
                  <AvatarFallback className="bg-primary/10 text-primary">
                    {userName.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">{userName}</p>
                  <p className="text-xs text-muted-foreground capitalize">{userType}</p>
                </div>
              </div>
            )}

            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive(link.path)
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted'
                  }`}
              >
                {link.label}
              </Link>
            ))}

            {isAuthenticated && (
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 rounded-lg text-sm font-medium hover:bg-muted flex items-center space-x-2 text-destructive"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            )}
          </nav>
        </div>
      )}
    </header>
  );
};
