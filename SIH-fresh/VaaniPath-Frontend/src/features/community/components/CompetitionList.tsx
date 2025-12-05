import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';
import { Calendar as CalendarIcon, Trophy, Users, Clock, Plus } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import api from '@/services/api';
import type { Competition, CompetitionCreate } from '../types';

export function CompetitionList({ communityId }: { communityId: string }) {
    const { isTeacher } = useAuth();
    const { toast } = useToast();
    const [competitions, setCompetitions] = useState<Competition[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [createOpen, setCreateOpen] = useState(false);

    // Form state
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [startDate, setStartDate] = useState<Date>();
    const [endDate, setEndDate] = useState<Date>();
    
    useEffect(() => {
        loadCompetitions();
    }, [communityId]);

    const loadCompetitions = async () => {
        try {
             setIsLoading(true);
             const response = await api.get(`/community/competitions/by-community/${communityId}`);
             setCompetitions(response.data); 
        } catch (error) {
            console.error(error);
            // setCompetitions([]); // Keep empty if error
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreate = async () => {
       if (!startDate || !endDate) return;

       const data: CompetitionCreate = {
           community_id: communityId,
           title,
           description,
           start_time: startDate.toISOString(),
           end_time: endDate.toISOString(),
           points_first: 100,
           points_second: 50,
           points_third: 25,
           points_top10: 10
       };

       try {
           await api.post('/community/competitions', data);
           toast({ title: 'Success', description: 'Competition created' });
           setCreateOpen(false);
           loadCompetitions();
       } catch (error: any) {
           toast({ title: 'Error', description: 'Failed to create competition', variant: 'destructive' });
       }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold">Active Competitions</h3>
                {isTeacher && (
                    <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="h-4 w-4 mr-2" />
                                Create Competition
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[425px]">
                            <DialogHeader>
                                <DialogTitle>Host a Competition</DialogTitle>
                                <DialogDescription>Create a live quiz competition for this community.</DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="space-y-2">
                                    <Label>Title</Label>
                                    <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Weekly Java Quiz" />
                                </div>
                                <div className="space-y-2">
                                    <Label>Description</Label>
                                    <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Test your knowledge..." />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Start Date</Label>
                                        <Popover>
                                            <PopoverTrigger asChild>
                                                <Button variant={"outline"} className={cn("w-full pl-3 text-left font-normal", !startDate && "text-muted-foreground")}>
                                                    {startDate ? format(startDate, "PPP") : <span>Pick a date</span>}
                                                    <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                                </Button>
                                            </PopoverTrigger>
                                            <PopoverContent className="w-auto p-0" align="start">
                                                <Calendar mode="single" selected={startDate} onSelect={setStartDate} initialFocus />
                                            </PopoverContent>
                                        </Popover>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>End Date</Label>
                                        <Popover>
                                            <PopoverTrigger asChild>
                                                <Button variant={"outline"} className={cn("w-full pl-3 text-left font-normal", !endDate && "text-muted-foreground")}>
                                                    {endDate ? format(endDate, "PPP") : <span>Pick a date</span>}
                                                    <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                                </Button>
                                            </PopoverTrigger>
                                            <PopoverContent className="w-auto p-0" align="start">
                                                <Calendar mode="single" selected={endDate} onSelect={setEndDate} initialFocus />
                                            </PopoverContent>
                                        </Popover>
                                    </div>
                                </div>
                                <Button onClick={handleCreate}>Create</Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                )}
            </div>

            {competitions.length === 0 ? (
                <div className="text-center py-12 border rounded-lg bg-muted/10">
                    <Trophy className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
                    <p className="text-muted-foreground">No active competitions</p>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2">
                    {competitions.map((comp) => (
                        <Card key={comp.id}>
                            <CardHeader>
                                <div className="flex justify-between items-start">
                                    <CardTitle className="text-lg">{comp.title}</CardTitle>
                                    <Badge>{comp.status}</Badge>
                                </div>
                                <CardDescription>
                                    {format(new Date(comp.start_time), "MMM d, h:mm a")} - {format(new Date(comp.end_time), "MMM d, h:mm a")}
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{comp.description}</p>
                                <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                                    <div className="flex items-center gap-1">
                                        <Users className="h-4 w-4" />
                                        {comp.participants_count} joined
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <Trophy className="h-4 w-4" />
                                        {comp.points_first} pts
                                    </div>
                                </div>
                                <Button className="w-full">View Details</Button>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
