import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Trophy, Users, Clock, ArrowLeft } from 'lucide-react';

export default function CompetitionDetailPage() {
    const { competitionId } = useParams();
    const navigate = useNavigate();
    const [competition, setCompetition] = useState<any | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const loadCompetition = async () => {
            if (!competitionId) return;
            try {
                // Fetch competition details check
                // For now assuming we have an API function
                const data = await import('@/features/community/services/communityApi').then(mod => mod.getCompetition(competitionId));
                setCompetition(data);
            } catch (error) {
                console.error("Failed to load competition", error);
            } finally {
                setIsLoading(false);
            }
        };
        loadCompetition();
    }, [competitionId]);

    if (isLoading) {
         return (
             <div className="min-h-screen relative bg-background text-foreground flex items-center justify-center">
                 <PremiumBackground />
                 <div className="z-10 text-center">
                     <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary border-b-2 border-purple-500 mx-auto mb-4"></div>
                     <p className="text-muted-foreground">Loading competition...</p>
                 </div>
             </div>
         );
    }

    if (!competition) {
        return (
            <div className="min-h-screen relative bg-background text-foreground flex items-center justify-center">
                 <PremiumBackground />
                 <div className="z-10 text-center">
                     <p className="text-xl font-bold">Competition not found</p>
                     <Button variant="link" onClick={() => navigate('/communities')}>Back to Communities</Button>
                 </div>
             </div>
        )
    }

    return (
        <div className="min-h-screen relative bg-background text-foreground">
            <PremiumBackground />
            <Header isAuthenticated userType="student" /> 
            
            <main className="container px-4 py-8 relative z-10 max-w-4xl mx-auto">
                <Button variant="ghost" className="mb-6 pl-0 hover:bg-transparent hover:text-primary" onClick={() => navigate(-1)}>
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back
                </Button>

                <div className="space-y-6">
                    <div className="flex flex-col md:flex-row justify-between gap-4">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                                    {competition.title}
                                </h1>
                                <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${competition.status === 'active' ? 'bg-green-500/20 text-green-500' : 'bg-muted text-muted-foreground'}`}>
                                    {competition.status}
                                </span>
                            </div>
                            <p className="text-muted-foreground">{competition.description}</p>
                        </div>
                        <div className="flex gap-2">
                             {/* Join / Play Button */}
                             {competition.status === 'active' || (competition.status === 'upcoming' && new Date(competition.start_time) <= new Date()) ? (
                                 <Button 
                                     size="lg" 
                                     className="bg-gradient-to-r from-primary to-purple-600 shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all"
                                     onClick={async () => {
                                         // 1. Register if needed (auto-register for simplicity or check)
                                         // For now, assuming direct entry registers you or api handles it.
                                         // But backend `register_for_competition` is separate.
                                         // Let's try to register first silently, ignoring "already registered" error.
                                         try {
                                             await import('../services/communityApi').then(mod => mod.registerForCompetition(competition.id));
                                         } catch (e) {
                                             // Ignore if already registered
                                         }
                                         navigate(`/community/competition/${competition.id}/play`);
                                     }}
                                 >
                                     Enter Contest
                                 </Button>
                             ) : (
                                 <Button size="lg" disabled className="bg-muted text-muted-foreground">
                                     {competition.status === 'completed' ? 'Contest Ended' : 'Starts Soon'}
                                 </Button>
                             )}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Card className="bg-card/40 backdrop-blur border-white/5">
                            <CardContent className="p-4 flex flex-col items-center text-center">
                                <Users className="h-5 w-5 text-primary mb-1" />
                                <span className="text-2xl font-bold">{competition.participants_count || 0}</span>
                                <span className="text-xs text-muted-foreground">Participants</span>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/40 backdrop-blur border-white/5">
                            <CardContent className="p-4 flex flex-col items-center text-center">
                                <Trophy className="h-5 w-5 text-yellow-500 mb-1" />
                                <span className="text-2xl font-bold">{competition.points_first}</span>
                                <span className="text-xs text-muted-foreground">Winning Pts</span>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/40 backdrop-blur border-white/5">
                            <CardContent className="p-4 flex flex-col items-center text-center">
                                <Clock className="h-5 w-5 text-blue-500 mb-1" />
                                <span className="text-sm font-semibold">{new Date(competition.end_time).toLocaleDateString()}</span>
                                <span className="text-xs text-muted-foreground">Ends On</span>
                            </CardContent>
                        </Card>
                    </div>

                    <Tabs defaultValue="details" className="w-full">
                        <TabsList className="grid w-full grid-cols-2 bg-muted/50">
                            <TabsTrigger value="details">Details</TabsTrigger>
                            <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
                        </TabsList>
                        <TabsContent value="details" className="mt-6">
                            <Card className="bg-card/40 backdrop-blur-md border-white/10">
                                <CardHeader>
                                    <CardTitle>About this Competition</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <h3 className="font-semibold mb-2">Instructions</h3>
                                        <p className="text-muted-foreground text-sm leading-relaxed">
                                            Participate in this quiz to test your knowledge and earn GyanPoints. 
                                            The top performers will be featured on the leaderboard. 
                                            Make sure to submit your answers before the time runs out!
                                        </p>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border/50">
                                        <div>
                                            <span className="text-sm text-muted-foreground block">Questions</span>
                                            <span className="font-medium">{competition.total_questions || 0}</span>
                                        </div>
                                         <div>
                                            <span className="text-sm text-muted-foreground block">Duration</span>
                                            <span className="font-medium">30 Mins</span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>
                        <TabsContent value="leaderboard" className="mt-6">
                             <Card className="bg-card/40 backdrop-blur-md border-white/10">
                                <CardHeader>
                                    <CardTitle>Top Performers</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                                        <Trophy className="h-12 w-12 mb-4 opacity-50" />
                                        <p>Leaderboard will be available after the competition ends.</p>
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                </div>
            </main>
        </div>
    );
}
