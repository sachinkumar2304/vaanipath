import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { GraduationCap, ArrowLeft, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { motion } from 'framer-motion';

const StudentLogin = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { login, signup } = useAuth();

  // Login state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  // Signup state
  const [signupData, setSignupData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    preferredLanguage: '',
    region: '',
    state: '',
    city: '',
  });
  const [isSigningUp, setIsSigningUp] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);

    try {
      await login({ email: loginEmail, password: loginPassword });

      // Get user data from localStorage to determine redirect
      const userData = JSON.parse(localStorage.getItem('user') || '{}');

      // REJECT admins and teachers from student login
      if (userData.is_admin) {
        toast({
          title: 'Wrong Login Page',
          description: 'Admins should use /admin to login',
          variant: 'destructive',
        });
        // Logout
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsLoggingIn(false);
        return;
      }

      if (userData.is_teacher) {
        toast({
          title: 'Wrong Login Page',
          description: 'Teachers should use /teacherlogin',
          variant: 'destructive',
        });
        // Logout
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsLoggingIn(false);
        return;
      }

      // Only students reach here
      toast({
        title: 'Login Successful',
        description: 'Welcome back to VAANIपथ!',
      });

      navigate('/homepage');
    } catch (error: any) {
      toast({
        title: 'Login Failed',
        description: error.response?.data?.detail || 'Invalid credentials',
        variant: 'destructive',
      });
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate password match
    if (signupData.password !== signupData.confirmPassword) {
      toast({
        title: 'Password Mismatch',
        description: 'Passwords do not match',
        variant: 'destructive',
      });
      return;
    }

    setIsSigningUp(true);

    try {
      await signup({
        email: signupData.email,
        password: signupData.password,
        full_name: signupData.name,
        is_admin: false
      });

      toast({
        title: 'Account Created',
        description: 'Your account has been created successfully!',
      });

      // Redirect to student dashboard
      navigate('/homepage');
    } catch (error: any) {
      toast({
        title: 'Signup Failed',
        description: error.response?.data?.detail || 'Failed to create account',
        variant: 'destructive',
      });
    } finally {
      setIsSigningUp(false);
    }
  };

  const languages = ['English', 'Hindi', 'Bengali', 'Telugu', 'Tamil', 'Marathi', 'Gujarati', 'Kannada', 'Malayalam', 'Punjabi'];

  return (
    <div className="min-h-screen relative font-sans bg-background text-foreground transition-colors duration-300">
      <PremiumBackground />
      <Header />

      <div className="container px-4 py-20 lg:py-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="mx-auto max-w-lg"
        >
          <div className="text-center mb-10">
            <motion.div
              initial={{ scale: 0, rotate: 10 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.1 }}
              className="inline-flex items-center justify-center rounded-2xl bg-primary/10 backdrop-blur-md border border-primary/20 p-5 mb-6 shadow-xl"
            >
              <GraduationCap className="h-10 w-10 text-primary" />
            </motion.div>
            <h1 className="text-4xl font-bold mb-3 text-foreground font-heading tracking-tight">Student Portal</h1>
            <p className="text-lg text-muted-foreground">Continue your learning journey</p>
          </div>

          <Card className="glass-card border-white/20 dark:border-white/10 shadow-2xl overflow-hidden relative">
            {/* Subtle top highlight */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-50" />

            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 p-1 bg-muted/50 m-6 mb-0 rounded-xl">
                <TabsTrigger value="login" className="data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-lg transition-all font-medium">Login</TabsTrigger>
                <TabsTrigger value="signup" className="data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-lg transition-all font-medium">Sign Up</TabsTrigger>
              </TabsList>

              <div className="p-6 md:p-8 pt-6">
                <TabsContent value="login" className="mt-0 space-y-6">
                  <div className="space-y-2 text-center">
                    <h2 className="text-2xl font-bold text-foreground">Welcome Back</h2>
                    <p className="text-sm text-muted-foreground">Ready to learn something new today?</p>
                  </div>
                  <form onSubmit={handleLogin} className="space-y-5">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="login-email">Student Email</Label>
                        <Input
                          id="login-email"
                          type="email"
                          placeholder="student@example.com"
                          value={loginEmail}
                          onChange={(e) => setLoginEmail(e.target.value)}
                          required
                          className="bg-background/50 border-input focus:ring-primary h-11 transition-all hover:border-primary/50"
                        />
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="login-password">Password</Label>
                          <a href="#" className="text-xs text-primary hover:underline">Forgot password?</a>
                        </div>
                        <Input
                          id="login-password"
                          type="password"
                          value={loginPassword}
                          onChange={(e) => setLoginPassword(e.target.value)}
                          required
                          className="bg-background/50 border-input focus:ring-primary h-11 transition-all hover:border-primary/50"
                        />
                      </div>
                    </div>
                    <Button
                      type="submit"
                      className="w-full h-12 text-base font-medium shadow-lg hover:shadow-primary/25 transition-all duration-300 bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-0.5"
                      disabled={isLoggingIn}
                    >
                      {isLoggingIn ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Logging in...
                        </>
                      ) : 'Start Learning'}
                    </Button>
                  </form>
                </TabsContent>

                <TabsContent value="signup" className="mt-0 space-y-6">
                  <div className="space-y-2 text-center">
                    <h2 className="text-2xl font-bold text-foreground">Join VaaniPath</h2>
                    <p className="text-sm text-muted-foreground">Create your free account to get started</p>
                  </div>
                  <form onSubmit={handleSignup} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="signup-name">Full Name</Label>
                      <Input
                        id="signup-name"
                        placeholder="e.g. Rahul Kumar"
                        value={signupData.name}
                        onChange={(e) => setSignupData({ ...signupData, name: e.target.value })}
                        required
                        className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signup-email">Email Address</Label>
                      <Input
                        id="signup-email"
                        type="email"
                        placeholder="student@example.com"
                        value={signupData.email}
                        onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                        required
                        className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="signup-password">Password</Label>
                        <Input
                          id="signup-password"
                          type="password"
                          value={signupData.password}
                          onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                          required
                          className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm</Label>
                        <Input
                          id="confirm-password"
                          type="password"
                          value={signupData.confirmPassword}
                          onChange={(e) => setSignupData({ ...signupData, confirmPassword: e.target.value })}
                          required
                          className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="language">Preferred Language</Label>
                      <Select onValueChange={(value) => setSignupData({ ...signupData, preferredLanguage: value })}>
                        <SelectTrigger id="language" className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50">
                          <SelectValue placeholder="Select your language" />
                        </SelectTrigger>
                        <SelectContent>
                          {languages.map((lang) => (
                            <SelectItem key={lang} value={lang.toLowerCase()}>{lang}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="state">State</Label>
                        <Input
                          id="state"
                          placeholder="State"
                          value={signupData.state}
                          onChange={(e) => setSignupData({ ...signupData, state: e.target.value })}
                          required
                          className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="city">City</Label>
                        <Input
                          id="city"
                          placeholder="City"
                          value={signupData.city}
                          onChange={(e) => setSignupData({ ...signupData, city: e.target.value })}
                          required
                          className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="region">Region</Label>
                      <Input
                        id="region"
                        placeholder="Region"
                        value={signupData.region}
                        onChange={(e) => setSignupData({ ...signupData, region: e.target.value })}
                        required
                        className="bg-background/50 border-input focus:ring-primary transition-all hover:border-primary/50"
                      />
                    </div>

                    <Button
                      type="submit"
                      className="w-full h-12 text-base font-medium shadow-lg hover:shadow-primary/25 transition-all duration-300 bg-primary text-primary-foreground hover:bg-primary/90 hover:-translate-y-0.5 mt-2"
                      disabled={isSigningUp}
                    >
                      {isSigningUp ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating Account...
                        </>
                      ) : 'Create Free Account'}
                    </Button>
                  </form>
                </TabsContent>
              </div>
            </Tabs>
          </Card>

          <div className="mt-8 text-center">
            <Link to="/landingpage" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-primary transition-colors duration-200 group">
              <ArrowLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
              Back to Home
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default StudentLogin;
