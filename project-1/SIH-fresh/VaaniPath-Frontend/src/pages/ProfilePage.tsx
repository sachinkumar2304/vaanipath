import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { User, Mail, Award } from 'lucide-react';

import { useEffect, useState } from 'react';
import { getGyanPoints } from '@/features/community/services/communityApi';

export default function ProfilePage() {
    const { user, isTeacher } = useAuth();
    const [points, setPoints] = useState(0);

    useEffect(() => {
        const fetchPoints = async () => {
            try {
                const data = await getGyanPoints();
                setPoints(data.total_points || 0);
            } catch (error) {
                console.error("Failed to fetch GyanPoints", error);
            }
        };
        fetchPoints();
    }, []); 

    return (
        <div className="min-h-screen relative bg-background text-foreground">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
            
            <main className="container px-4 py-12 relative z-10 max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold mb-8">My Profile</h1>
                
                <Card className="bg-card/40 backdrop-blur-md border-white/10 mb-8">
                    <CardHeader>
                        <CardTitle>Personal Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center gap-6">
                            <Avatar className="h-24 w-24 border-2 border-primary">
                                <AvatarImage src="/placeholder-avatar.jpg" />
                                <AvatarFallback className="text-2xl mt-3">{user?.email?.charAt(0).toUpperCase()}</AvatarFallback>
                            </Avatar>
                            <div>
                                <Button variant="outline" size="sm">Change Avatar</Button>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Email</Label>
                            <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-md text-muted-foreground">
                                <Mail className="h-4 w-4" />
                                {user?.email}
                            </div>
                        </div>

                         <div className="space-y-2">
                            <Label>Username</Label>
                            <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-md text-muted-foreground">
                                <User className="h-4 w-4" />
                                Student User
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-card/40 backdrop-blur-md border-white/10">
                    <CardHeader>
                        <CardTitle>Achievements</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-4 p-4 bg-primary/10 rounded-lg border border-primary/20">
                            <div className="p-3 bg-primary/20 rounded-full">
                                <Award className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Total GyanPoints</p>
                                <p className="text-2xl font-bold text-primary">{points}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </main>
        </div>
    );
}
