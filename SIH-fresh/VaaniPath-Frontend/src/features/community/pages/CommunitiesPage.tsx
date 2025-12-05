import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Users, Search, Plus } from 'lucide-react';
import { getCommunities, joinCommunity, createCommunity } from '../services/communityApi';
import type { Community } from '../types';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

export default function CommunitiesPage() {
    const { user, isTeacher } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();
    const [communities, setCommunities] = useState<Community[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [newCommunity, setNewCommunity] = useState({
        name: '',
        domain: '',
        description: ''
    });

    useEffect(() => {
        loadCommunities();
    }, []);

    const loadCommunities = async () => {
        try {
            setIsLoading(true);
            const data = await getCommunities();
            setCommunities(data.communities);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: 'Failed to load communities',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateCommunity = async () => {
        try {
            await createCommunity(newCommunity);
            toast({
                title: 'Success',
                description: 'Community created successfully'
            });
            setCreateDialogOpen(false);
            setNewCommunity({ name: '', domain: '', description: '' });
            loadCommunities();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to create community',
                variant: 'destructive'
            });
        }
    };

    const handleJoinCommunity = async (communityId: string) => {
        try {
            await joinCommunity(communityId);
            toast({
                title: 'Success',
                description: 'Joined community successfully'
            });
            loadCommunities();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to join community',
                variant: 'destructive'
            });
        }
    };

    const filteredCommunities = communities.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.domain.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen relative bg-background text-foreground">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
            
            <div className="container px-4 py-12 lg:py-16 relative z-10">
            <div className="space-y-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Communities</h2>
                        <p className="text-muted-foreground">
                            Join domain-specific communities and connect with learners
                        </p>
                    </div>
                    {isTeacher && (
                        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                            <DialogTrigger asChild>
                                <Button>
                                    <Plus className="h-4 w-4 mr-2" />
                                    Create Community
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Create New Community</DialogTitle>
                                    <DialogDescription>
                                        Create a domain-specific community for your students
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <div>
                                        <Label>Community Name</Label>
                                        <Input
                                            value={newCommunity.name}
                                            onChange={(e) => setNewCommunity({ ...newCommunity, name: e.target.value })}
                                            placeholder="e.g., Python Developers"
                                        />
                                    </div>
                                    <div>
                                        <Label>Domain</Label>
                                        <Input
                                            value={newCommunity.domain}
                                            onChange={(e) => setNewCommunity({ ...newCommunity, domain: e.target.value })}
                                            placeholder="e.g., python, javascript, ai_ml"
                                        />
                                    </div>
                                    <div>
                                        <Label>Description</Label>
                                        <Input
                                            value={newCommunity.description}
                                            onChange={(e) => setNewCommunity({ ...newCommunity, description: e.target.value })}
                                            placeholder="Brief description"
                                        />
                                    </div>
                                    <Button onClick={handleCreateCommunity} className="w-full">
                                        Create Community
                                    </Button>
                                </div>
                            </DialogContent>
                        </Dialog>
                    )}
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search communities..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                    />
                </div>

                {/* Communities Grid */}
                {isLoading ? (
                    <div className="text-center py-12">Loading communities...</div>
                ) : filteredCommunities.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                        No communities found
                    </div>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {filteredCommunities.map((community) => (
                            <Card key={community.id} className="hover:shadow-lg transition-shadow">
                                <CardHeader>
                                    <CardTitle className="flex items-center justify-between">
                                        <span>{community.name}</span>
                                        <Users className="h-5 w-5 text-muted-foreground" />
                                    </CardTitle>
                                    <CardDescription>
                                        <span className="inline-block px-2 py-1 text-xs rounded-full bg-primary/10 text-primary">
                                            {community.domain}
                                        </span>
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground mb-4">
                                        {community.description || 'No description'}
                                    </p>
                                    <div className="flex justify-between items-center text-sm text-muted-foreground mb-4">
                                        <span>{community.member_count} members</span>
                                        <span>{community.post_count} posts</span>
                                    </div>
                                    {community.is_member ? (
                                        <Button
                                            onClick={() => navigate(`/community/${community.id}`)}
                                            className="w-full"
                                        >
                                            View Community
                                        </Button>
                                    ) : (
                                        <Button
                                            onClick={() => handleJoinCommunity(community.id)}
                                            variant="outline"
                                            className="w-full"
                                        >
                                            Join Community
                                        </Button>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
            </div>
            
            <Footer />
        </div>
    );
}
