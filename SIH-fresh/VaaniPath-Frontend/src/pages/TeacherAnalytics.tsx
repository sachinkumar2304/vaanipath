import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

const TeacherAnalytics = () => {
    const studentPerformanceData = [
        { name: 'Python Basics', avgScore: 85, passingRate: 92 },
        { name: 'Web Dev', avgScore: 78, passingRate: 88 },
        { name: 'Data Science', avgScore: 72, passingRate: 75 },
        { name: 'React Mastery', avgScore: 80, passingRate: 85 },
    ];

    const engagementData = [
        { day: 'Mon', activeStudents: 120 },
        { day: 'Tue', activeStudents: 145 },
        { day: 'Wed', activeStudents: 132 },
        { day: 'Thu', activeStudents: 156 },
        { day: 'Fri', activeStudents: 140 },
        { day: 'Sat', activeStudents: 95 },
        { day: 'Sun', activeStudents: 85 },
    ];

    const deviceData = [
        { name: 'Desktop', value: 400 },
        { name: 'Mobile', value: 300 },
        { name: 'Tablet', value: 100 },
    ];

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    return (
        <div className="min-h-screen bg-background">
            <Header isAuthenticated userType="teacher" />
            <div className="container px-4 py-8">
                <Button variant="ghost" asChild className="mb-6">
                    <Link to="/teacher/dashboard">
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back to Dashboard
                    </Link>
                </Button>

                <h1 className="text-3xl font-bold mb-8">Analytics Dashboard</h1>

                <div className="grid gap-6 md:grid-cols-2 mb-8">
                    <Card className="glass">
                        <CardHeader>
                            <CardTitle>Student Performance</CardTitle>
                            <CardDescription>Average scores and passing rates by course</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={studentPerformanceData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Bar dataKey="avgScore" fill="hsl(var(--primary))" name="Avg Score" />
                                        <Bar dataKey="passingRate" fill="hsl(var(--secondary))" name="Passing Rate %" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="glass">
                        <CardHeader>
                            <CardTitle>Weekly Engagement</CardTitle>
                            <CardDescription>Active students over the last week</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={engagementData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="day" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Line type="monotone" dataKey="activeStudents" stroke="hsl(var(--accent))" strokeWidth={2} name="Active Students" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                    <Card className="glass col-span-1">
                        <CardHeader>
                            <CardTitle>Device Usage</CardTitle>
                            <CardDescription>Student device distribution</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={deviceData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={80}
                                            fill="#8884d8"
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {deviceData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="glass md:col-span-2">
                        <CardHeader>
                            <CardTitle>Recent Activity</CardTitle>
                            <CardDescription>Latest student actions</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {[1, 2, 3, 4, 5].map((i) => (
                                    <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                                                S{i}
                                            </div>
                                            <div>
                                                <p className="font-medium">Student {i} completed "Python Basics"</p>
                                                <p className="text-sm text-muted-foreground">2 hours ago</p>
                                            </div>
                                        </div>
                                        <div className="text-success font-medium">+50 pts</div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default TeacherAnalytics;
