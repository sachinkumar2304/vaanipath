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
        <div className="min-h-screen relative bg-background text-foreground overflow-hidden">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
            
            <main className="container px-4 py-12 relative z-10 max-w-7xl mx-auto">
                <div className="space-y-8">
                    {/* Hero Section */}
                    <div className="text-center space-y-4 mb-16">
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                            Discover Communities
                        </h1>
                        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                            Join domain-specific hubs, connect with peers, and accelerate your learning journey together.
                        </p>
                        
                        {/* Search Bar */}
                        <div className="max-w-md mx-auto relative mt-8">
                            <div className="relative group">
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-purple-600 rounded-lg blur opacity-30 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
                                <div className="relative flex items-center bg-card rounded-lg">
                                    <Search className="absolute left-3 h-5 w-5 text-muted-foreground" />
                                    <Input
                                        placeholder="Search by name or domain..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="pl-10 h-12 bg-transparent border-none focus-visible:ring-0 focus-visible:ring-offset-0"
                                    />
                                </div>
                            </div>
                        </div>

                        {isTeacher && (
                            <div className="mt-8">
                                <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                                    <DialogTrigger asChild>
                                        <Button size="lg" className="bg-gradient-to-r from-primary to-purple-600 hover:opacity-90 shadow-lg shadow-primary/20">
                                            <Plus className="h-5 w-5 mr-2" />
                                            Create Community
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-md">
                                        <DialogHeader>
                                            <DialogTitle>Create New Community</DialogTitle>
                                            <DialogDescription>
                                                Launch a new learning hub for your students
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="space-y-4 py-4">
                                            <div className="space-y-2">
                                                <Label>Community Name</Label>
                                                <Input
                                                    value={newCommunity.name}
                                                    onChange={(e) => setNewCommunity({ ...newCommunity, name: e.target.value })}
                                                    placeholder="e.g., Python Masters"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label>Domain</Label>
                                                <Input
                                                    value={newCommunity.domain}
                                                    onChange={(e) => setNewCommunity({ ...newCommunity, domain: e.target.value })}
                                                    placeholder="e.g., python, ai, web-dev"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label>Description</Label>
                                                <Input
                                                    value={newCommunity.description}
                                                    onChange={(e) => setNewCommunity({ ...newCommunity, description: e.target.value })}
                                                    placeholder="Brief description of the community"
                                                />
                                            </div>
                                            <Button onClick={handleCreateCommunity} className="w-full bg-gradient-to-r from-primary to-purple-600">
                                                Launch Community
                                            </Button>
                                        </div>
                                    </DialogContent>
                                </Dialog>
                            </div>
                        )}
                    </div>

                    {/* Communities Grid */}
                    {isLoading ? (
                        <div className="flex justify-center py-20">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                        </div>
                    ) : filteredCommunities.length === 0 ? (
                        <div className="text-center py-20">
                            <div className="bg-card/50 backdrop-blur-sm rounded-2xl p-8 max-w-md mx-auto border border-white/10">
                                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                                <h3 className="text-xl font-semibold mb-2">No communities found</h3>
                                <p className="text-muted-foreground">
                                    Try adjusting your search or create a new one!
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                            {filteredCommunities.map((community) => (
                                <Card 
                                    key={community.id} 
                                    className="group overflow-hidden border-none bg-card/40 backdrop-blur-md hover:bg-card/60 transition-all duration-300 hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-1"
                                >
                                    <div className="h-32 bg-gradient-to-br from-primary/10 to-purple-500/10 relative overflow-hidden">
                                        <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-20"></div>
                                        {community.thumbnail_url ? (
                                            <img src={community.thumbnail_url} alt={community.name} className="w-full h-full object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center">
                                                <Users className="h-12 w-12 text-primary/40" />
                                            </div>
                                        )}
                                    </div>
                                    <CardContent className="p-6">
                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                                <h3 className="font-bold text-xl group-hover:text-primary transition-colors line-clamp-1">
                                                    {community.name}
                                                </h3>
                                                <div className="inline-flex items-center mt-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                                                    {community.domain}
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <p className="text-sm text-muted-foreground mb-6 line-clamp-2 h-10">
                                            {community.description || 'Join this community to connect with learners and experts.'}
                                        </p>

                                        <div className="flex items-center justify-between text-sm text-muted-foreground mb-6 bg-background/30 rounded-lg p-3">
                                            <div className="flex items-center gap-1.5">
                                                <Users className="h-4 w-4" />
                                                <span>{community.member_count} members</span>
                                            </div>
                                            <div className="w-px h-4 bg-border"></div>
                                            <div>
                                                <span>{community.post_count} posts</span>
                                            </div>
                                        </div>

                                        {community.is_member ? (
                                            <Button
                                                onClick={() => navigate(`/community/${community.id}`)}
                                                className="w-full bg-secondary/50 hover:bg-secondary/80 text-secondary-foreground"
                                                variant="secondary"
                                            >
                                                Enter Community
                                            </Button>
                                        ) : (
                                            <Button
                                                onClick={() => handleJoinCommunity(community.id)}
                                                className="w-full bg-gradient-to-r from-primary to-purple-600 hover:opacity-90 transition-opacity"
                                            >
                                                Join Now
                                            </Button>
                                        )}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </main>
            <Footer />
        </div>
    );
}
