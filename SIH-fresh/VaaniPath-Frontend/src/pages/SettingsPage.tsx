import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useAuth } from '@/contexts/AuthContext';
import { Bell, Moon, Languages } from 'lucide-react';

import { useTheme } from '@/contexts/ThemeContext';

export default function SettingsPage() {
    const { isTeacher } = useAuth();
    const { theme, setTheme } = useTheme();

    return (
        <div className="min-h-screen relative bg-background text-foreground">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
            
            <main className="container px-4 py-12 relative z-10 max-w-2xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold">Settings</h1>
                    <p className="text-muted-foreground">Manage your preferences and application settings</p>
                </div>
                
                <div className="space-y-6">
                    <Card className="bg-card/40 backdrop-blur-md border-white/10">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Moon className="h-5 w-5" />
                                Appearance
                            </CardTitle>
                            <CardDescription>Customize how Gyanify looks on your device</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <Label>Dark Mode</Label>
                                    <p className="text-sm text-muted-foreground">Enable dark mode for better viewing at night</p>
                                </div>
                                <Switch 
                                    checked={theme === 'dark'} 
                                    onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')} 
                                />
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-card/40 backdrop-blur-md border-white/10">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Bell className="h-5 w-5" />
                                Notifications
                            </CardTitle>
                            <CardDescription>Manage your email and push notifications</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <Label>Competition Alerts</Label>
                                    <p className="text-sm text-muted-foreground">Get notified when new competitions start</p>
                                </div>
                                <Switch checked={true} />
                            </div>
                             <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <Label>Community Mentions</Label>
                                    <p className="text-sm text-muted-foreground">Receive alerts when someone replies to you</p>
                                </div>
                                <Switch checked={true} />
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-card/40 backdrop-blur-md border-white/10">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Languages className="h-5 w-5" />
                                Language
                            </CardTitle>
                             <CardDescription>Select your preferred language</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="p-4 bg-muted/50 rounded-md text-sm text-muted-foreground text-center">
                                Language selection is available in the top bar.
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </main>
        </div>
    );
}
