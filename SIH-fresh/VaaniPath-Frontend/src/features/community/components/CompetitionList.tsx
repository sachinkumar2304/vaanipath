import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trophy, Clock, Users, Calendar, ArrowRight, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { Competition } from '../types';
import { getCompetitions } from '../services/communityApi';
import { toast } from 'sonner';

interface CompetitionListProps {
    communityId: string;
}

import { useAuth } from '@/contexts/AuthContext';

export const CompetitionList = ({ communityId }: CompetitionListProps) => {
    const navigate = useNavigate();
    const { isTeacher } = useAuth();
    
    const [competitions, setCompetitions] = useState<Competition[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const loadCompetitions = async () => {
            if (!communityId) return;
            try {
                const data = await getCompetitions(communityId);
                setCompetitions(data);
            } catch (error) {
                console.error("Failed to load competitions", error);
                toast.error("Failed to load competitions");
            } finally {
                setIsLoading(false);
            }
        };
        loadCompetitions();
    }, [communityId]);

    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {isTeacher && (
                <div className="flex justify-end">
                    <Button onClick={() => navigate(`/community/${communityId}/create-competition`)}>
                        Create Competition
                    </Button>
                </div>
            )}
            
            {!competitions.length ? (
                <Card className="bg-muted/50 border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                        <Trophy className="h-12 w-12 mb-4 opacity-50" />
                        <p>No active competitions found.</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {competitions.map((comp) => (
                        <Card key={comp.id} className="group hover:border-primary/50 transition-all duration-300 overflow-hidden bg-card/50 backdrop-blur">
                            <CardHeader className="p-0">
                                <div className="h-32 bg-gradient-to-br from-primary/20 via-purple-500/10 to-transparent p-6 relative overflow-hidden">
                                    <div className="absolute top-4 right-4">
                                        <Badge variant={comp.status === 'active' ? "default" : "secondary"} className="uppercase text-xs font-bold tracking-wider">
                                            {comp.status}
                                        </Badge>
                                    </div>
                                    <div className="absolute top-4 left-4 p-2 bg-background/30 backdrop-blur rounded-lg">
                                        <Trophy className="h-6 w-6 text-primary" />
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="p-6">
                                <div className="mb-4">
                                    <h3 className="font-bold text-xl mb-2 group-hover:text-primary transition-colors line-clamp-1">{comp.title}</h3>
                                    <p className="text-sm text-muted-foreground line-clamp-2 min-h-[2.5rem]">{comp.description}</p>
                                </div>

                                <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                                    <div className="flex items-center gap-2 text-muted-foreground bg-muted/30 p-2 rounded-md">
                                        <Calendar className="h-4 w-4 text-primary" />
                                        <span className="text-xs">
                                            {format(new Date(comp.start_time), 'MMM d, yyyy')}
                                        </span>
                                    </div>
                                     <div className="flex items-center gap-2 text-muted-foreground bg-muted/30 p-2 rounded-md">
                                        <Clock className="h-4 w-4 text-purple-500" />
                                        <span className="text-xs">
                                            {format(new Date(comp.end_time), 'HH:mm')}
                                        </span>
                                    </div>
                                </div>

                                 <div className="flex items-center justify-between text-sm text-muted-foreground mb-6 border-t border-border/50 pt-4">
                                    <div className="flex items-center gap-1.5">
                                        <Users className="h-4 w-4" />
                                        {comp.participants_count} joined
                                    </div>
                                    <div className="flex items-center gap-1.5 font-medium text-foreground">
                                        <Trophy className="h-4 w-4 text-yellow-500" />
                                        {comp.points_first} pts
                                    </div>
                                </div>
                                
                                <Button 
                                    className="w-full bg-primary/10 hover:bg-primary hover:text-primary-foreground text-primary font-semibold transition-all group-hover:shadow-lg group-hover:shadow-primary/20"
                                    onClick={() => navigate(`/community/competition/${comp.id}`)}
                                >
                                    View Contest
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};
