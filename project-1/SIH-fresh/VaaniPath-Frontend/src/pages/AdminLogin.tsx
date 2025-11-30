import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const AdminLogin = () => {
    const navigate = useNavigate();
    const { toast } = useToast();
    const { login } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoggingIn(true);

        try {
            await login({ email, password });

            // Get user data to check if admin
            const userData = JSON.parse(localStorage.getItem('user') || '{}');

            // Check if user is actually an admin
            if (!userData.is_admin) {
                toast({
                    title: 'Access Denied',
                    description: 'This login is for administrators only',
                    variant: 'destructive',
                });
                // Logout and redirect
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                return;
            }

            toast({
                title: 'Welcome Admin',
                description: 'Login successful!',
            });

            navigate('/admin/dashboard');
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

    return (
        <div className="min-h-screen bg-background flex items-center justify-center">
            <div className="w-full max-w-md px-4">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center rounded-full bg-primary/10 p-3 mb-4">
                        <Shield className="h-8 w-8 text-primary" />
                    </div>
                    <h1 className="text-3xl font-bold mb-2">Admin Portal</h1>
                    <p className="text-muted-foreground">VAANIपथ Administration</p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>Admin Login</CardTitle>
                        <CardDescription>Access the admin dashboard</CardDescription>
                    </CardHeader>
                    <form onSubmit={handleLogin}>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="admin-email">Email</Label>
                                <Input
                                    id="admin-email"
                                    type="email"
                                    placeholder="admin@vaanipath.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="admin-password">Password</Label>
                                <Input
                                    id="admin-password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </CardContent>
                        <CardFooter className="flex flex-col space-y-4">
                            <Button type="submit" className="w-full" disabled={isLoggingIn}>
                                {isLoggingIn ? 'Logging in...' : 'Login as Admin'}
                            </Button>
                            <div className="text-sm text-center text-muted-foreground">
                                <Link to="/login" className="text-primary hover:underline">
                                    Student Login
                                </Link>
                                {' • '}
                                <Link to="/teacherlogin" className="text-primary hover:underline">
                                    Teacher Login
                                </Link>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default AdminLogin;
