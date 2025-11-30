import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getAdminStats } from '@/services/admin';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Users, GraduationCap, Video } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import AdminLayout from '@/components/AdminLayout';

export default function AdminDashboard() {
    const { isAdmin } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();
    const [stats, setStats] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!isAdmin) {
            navigate('/login');
            return;
        }
        loadStats();
    }, [isAdmin]);

    const loadStats = async () => {
        try {
            setIsLoading(true);
            const statsData = await getAdminStats();
            setStats(statsData);
        } catch (error) {
            console.error('Failed to load stats:', error);
            toast({
                title: 'Error',
                description: 'Failed to load dashboard statistics',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AdminLayout>
            <div className="space-y-6">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                    <p className="text-muted-foreground">
                        Overview of your platform statistics
                    </p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                            <Users className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {isLoading ? '...' : (stats?.total_users || 0)}
                            </div>
                        </CardContent>
                    </Card>

                    <Link to="/admin/tutors">
                        <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Tutors</CardTitle>
                                <GraduationCap className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {isLoading ? '...' : (stats?.total_teachers || 0)}
                                </div>
                            </CardContent>
                        </Card>
                    </Link>

                    <Link to="/admin/students">
                        <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Students</CardTitle>
                                <Users className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {isLoading ? '...' : (stats?.total_students || 0)}
                                </div>
                            </CardContent>
                        </Card>
                    </Link>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Videos</CardTitle>
                            <Video className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {isLoading ? '...' : (stats?.total_videos || 0)}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Quick Actions */}
                <div className="grid gap-4 md:grid-cols-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <Link
                                to="/admin/tutors"
                                className="block p-3 rounded-lg border hover:bg-accent transition-colors"
                            >
                                → Manage Tutors
                            </Link>
                            <Link
                                to="/admin/students"
                                className="block p-3 rounded-lg border hover:bg-accent transition-colors"
                            >
                                → View Students
                            </Link>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Platform Stats</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Completed Videos</span>
                                <span className="font-medium">
                                    {isLoading ? '...' : (stats?.videos_by_status?.completed || 0)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Processing</span>
                                <span className="font-medium">
                                    {isLoading ? '...' : (stats?.videos_by_status?.processing || 0)}
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </AdminLayout>
    );
}
