import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { 
    Users, 
    MessageSquare, 
    Trophy, 
    Share2, 
    MoreVertical, 
    Heart, 
    Send,
    Image as ImageIcon,
    Loader2,
    X
} from 'lucide-react';
import { 
    getCommunity, 
    getPosts, 
    createPost, 
    toggleLike,
    createReply,
    getReplies,
    uploadPostMedia
} from '../services/communityApi';
import { CompetitionList } from '../components/CompetitionList';
import type { Community, Post, Reply } from '../types';
import { formatDistanceToNow } from 'date-fns';

export default function CommunityDetailPage() {
    const { communityId } = useParams<{ communityId: string }>();
    const { user, isTeacher } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [community, setCommunity] = useState<Community | null>(null);
    const [posts, setPosts] = useState<Post[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isPostsLoading, setIsPostsLoading] = useState(true);
    const [newPostContent, setNewPostContent] = useState('');
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('discussions');

    useEffect(() => {
        if (communityId) {
            loadCommunityDetails();
            loadPosts();
        }
    }, [communityId]);

    const loadCommunityDetails = async () => {
        try {
            if (!communityId) return;
            const data = await getCommunity(communityId);
            setCommunity(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: 'Failed to load community details',
                variant: 'destructive'
            });
            navigate('/communities');
        } finally {
            setIsLoading(false);
        }
    };

    const loadPosts = async () => {
        try {
            if (!communityId) return;
            setIsPostsLoading(true);
            const data = await getPosts({ community_id: communityId });
            setPosts(data.posts);
        } catch (error: any) {
            console.error('Failed to load posts:', error);
        } finally {
            setIsPostsLoading(false);
        }
    };

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleCreatePost = async () => {
        if (!newPostContent.trim() && !selectedImage) return;
        if (!communityId) return;

        try {
            let mediaUrls: string[] = [];
            if (selectedImage) {
                const uploadRes = await uploadPostMedia(selectedImage);
                if (uploadRes.url) {
                    mediaUrls.push(uploadRes.url);
                }
            }

            const newPost = await createPost({
                community_id: communityId,
                content: newPostContent,
                post_type: 'text',
                media_urls: mediaUrls
            });
            setPosts([newPost, ...posts]);
            setNewPostContent('');
            removeImage();
            toast({
                title: 'Success',
                description: 'Post created successfully'
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: 'Failed to create post',
                variant: 'destructive'
            });
        }
    };

    const handleLikePost = async (postId: string) => {
        try {
            const response = await toggleLike(postId);
            setPosts(posts.map(p => {
                if (p.id === postId) {
                    return {
                        ...p,
                        likes_count: response.likes_count,
                        is_liked_by_user: response.liked
                    };
                }
                return p;
            }));
        } catch (error) {
            console.error('Failed to like post:', error);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!community) return null;

    return (
        <div className="min-h-screen relative bg-background text-foreground">
            <PremiumBackground />
            <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
            
            <div className="container px-4 py-8 relative z-10 max-w-6xl mx-auto">
                {/* Community Header */}
                <Card className="mb-8 border-none shadow-lg bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-6">
                        <div className="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center">
                                    {community.thumbnail_url ? (
                                        <img src={community.thumbnail_url} alt={community.name} className="h-full w-full object-cover rounded-2xl" />
                                    ) : (
                                        <Users className="h-10 w-10 text-primary" />
                                    )}
                                </div>
                                <div>
                                    <h1 className="text-3xl font-bold">{community.name}</h1>
                                    <div className="flex items-center gap-2 text-muted-foreground mt-1">
                                        <Badge variant="secondary" className="bg-primary/10 text-primary hover:bg-primary/20">
                                            {community.domain}
                                        </Badge>
                                        <span>•</span>
                                        <span>{community.member_count} members</span>
                                        <span>•</span>
                                        <span>{community.post_count} posts</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex gap-2 w-full md:w-auto">
                                <Button variant="outline" className="flex-1 md:flex-none">
                                    <Share2 className="h-4 w-4 mr-2" />
                                    Share
                                </Button>
                                {isTeacher && user?.id === community.created_by && (
                                    <Button 
                                        variant="secondary" 
                                        className="flex-1 md:flex-none"
                                        onClick={() => navigate(`/community/${communityId}/create-competition`)}
                                    >
                                        Create Contest
                                    </Button>
                                )}
                            </div>
                        </div>
                        <p className="mt-4 text-muted-foreground">
                            {community.description}
                        </p>
                    </CardContent>
                </Card>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                    <TabsList className="bg-card/50 p-1">
                        <TabsTrigger value="discussions" className="gap-2">
                            <MessageSquare className="h-4 w-4" />
                            Discussions
                        </TabsTrigger>
                        <TabsTrigger value="competitions" className="gap-2">
                            <Trophy className="h-4 w-4" />
                            Competitions
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="discussions" className="space-y-6">
                        {/* Create Post */}
                        <Card className="border-none shadow-md bg-card/80">
                            <CardContent className="p-4">
                                <div className="flex gap-4">
                                    <Avatar>
                                        <AvatarFallback>{user?.full_name?.[0] || 'U'}</AvatarFallback>
                                    </Avatar>
                                    <div className="flex-1 space-y-4">
                                        <Textarea 
                                            placeholder="Start a discussion..." 
                                            className="min-h-[100px] bg-background/50 border-none focus-visible:ring-1"
                                            value={newPostContent}
                                            onChange={(e) => setNewPostContent(e.target.value)}
                                        />
                                        
                                        {imagePreview && (
                                            <div className="relative inline-block">
                                                <img src={imagePreview} alt="Preview" className="h-32 rounded-lg object-cover" />
                                                <button 
                                                    onClick={removeImage}
                                                    className="absolute -top-2 -right-2 bg-destructive text-destructive-foreground rounded-full p-1"
                                                >
                                                    <X className="h-3 w-3" />
                                                </button>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-center">
                                            <div className="flex gap-2">
                                                <input 
                                                    type="file" 
                                                    ref={fileInputRef} 
                                                    className="hidden" 
                                                    accept="image/*"
                                                    onChange={handleImageSelect}
                                                />
                                                <Button 
                                                    variant="ghost" 
                                                    size="sm" 
                                                    className="text-muted-foreground hover:text-primary"
                                                    onClick={() => fileInputRef.current?.click()}
                                                >
                                                    <ImageIcon className="h-4 w-4 mr-2" />
                                                    Add Image
                                                </Button>
                                            </div>
                                            <Button onClick={handleCreatePost} disabled={!newPostContent.trim() && !selectedImage}>
                                                <Send className="h-4 w-4 mr-2" />
                                                Post
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Posts List */}
                        {isPostsLoading ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                            </div>
                        ) : posts.length === 0 ? (
                            <div className="text-center py-12 text-muted-foreground">
                                No posts yet. Be the first to start a conversation!
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {posts.map((post) => (
                                    <PostCard 
                                        key={post.id} 
                                        post={post} 
                                        onLike={() => handleLikePost(post.id)} 
                                    />
                                ))}
                            </div>
                        )}
                    </TabsContent>

                    <TabsContent value="competitions">
                        <CompetitionList communityId={communityId} />
                    </TabsContent>
                </Tabs>
            </div>
            
            <Footer />
        </div>
    );
}

function PostCard({ post, onLike }: { post: Post; onLike: () => void }) {
    const [showReplies, setShowReplies] = useState(false);
    const [replies, setReplies] = useState<Reply[]>([]);
    const [replyContent, setReplyContent] = useState('');
    const [isLoadingReplies, setIsLoadingReplies] = useState(false);

    const handleLoadReplies = async () => {
        if (showReplies) {
            setShowReplies(false);
            return;
        }
        
        try {
            setIsLoadingReplies(true);
            const data = await getReplies(post.id);
            setReplies(data.replies);
            setShowReplies(true);
        } catch (error) {
            console.error('Failed to load replies:', error);
        } finally {
            setIsLoadingReplies(false);
        }
    };

    const handleSubmitReply = async () => {
        if (!replyContent.trim()) return;

        try {
            const newReply = await createReply(post.id, { content: replyContent });
            setReplies([...replies, newReply]);
            setReplyContent('');
        } catch (error) {
            console.error('Failed to submit reply:', error);
        }
    };

    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
            return formatDistanceToNow(date, { addSuffix: true });
        } catch (e) {
            return "just now";
        }
    };

    return (
        <Card className="border-none shadow-md hover:shadow-lg transition-shadow duration-200">
            <CardContent className="p-6">
                <div className="flex gap-4">
                    <Avatar>
                        <AvatarFallback>{post.user_name?.[0] || 'U'}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-semibold">{post.user_name || 'Anonymous User'}</h3>
                                <p className="text-xs text-muted-foreground">
                                    {formatDate(post.created_at)}
                                </p>
                            </div>
                            <Button variant="ghost" size="icon">
                                <MoreVertical className="h-4 w-4" />
                            </Button>
                        </div>
                        
                        <div className="mt-3 mb-4 text-sm leading-relaxed whitespace-pre-wrap">
                            {post.content}
                        </div>

                        {post.media_urls && post.media_urls.length > 0 && (
                            <div className="mb-4 rounded-lg overflow-hidden">
                                <img src={post.media_urls[0]} alt="Post content" className="max-h-[400px] w-full object-cover" />
                            </div>
                        )}

                        <div className="flex items-center gap-6">
                            <Button 
                                variant="ghost" 
                                size="sm" 
                                className={`gap-2 ${post.is_liked_by_user ? 'text-red-500 hover:text-red-600' : 'text-muted-foreground'}`}
                                onClick={onLike}
                            >
                                <Heart className={`h-4 w-4 ${post.is_liked_by_user ? 'fill-current' : ''}`} />
                                {post.likes_count}
                            </Button>
                            <Button 
                                variant="ghost" 
                                size="sm" 
                                className="gap-2 text-muted-foreground"
                                onClick={handleLoadReplies}
                            >
                                <MessageSquare className="h-4 w-4" />
                                {post.replies_count} Replies
                            </Button>
                        </div>

                        {showReplies && (
                            <div className="mt-4 pl-4 border-l-2 border-primary/10 space-y-4">
                                {isLoadingReplies ? (
                                    <div className="text-center py-2">Loading replies...</div>
                                ) : (
                                    <>
                                        {replies.map(reply => (
                                            <div key={reply.id} className="flex gap-3">
                                                <Avatar className="h-8 w-8">
                                                    <AvatarFallback>{reply.user_name?.[0] || 'U'}</AvatarFallback>
                                                </Avatar>
                                                <div className="bg-muted/50 p-3 rounded-lg flex-1">
                                                    <div className="flex justify-between items-center mb-1">
                                                        <span className="font-medium text-sm">{reply.user_name}</span>
                                                        <span className="text-xs text-muted-foreground">
                                                            {formatDate(reply.created_at)}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm">{reply.content}</p>
                                                </div>
                                            </div>
                                        ))}
                                        
                                        <div className="flex gap-3 mt-4">
                                            <Avatar className="h-8 w-8">
                                                <AvatarFallback>Me</AvatarFallback>
                                            </Avatar>
                                            <div className="flex-1 flex gap-2">
                                                <Textarea 
                                                    value={replyContent}
                                                    onChange={(e) => setReplyContent(e.target.value)}
                                                    placeholder="Write a reply..."
                                                    className="min-h-[60px]"
                                                />
                                                <Button size="icon" onClick={handleSubmitReply} disabled={!replyContent.trim()}>
                                                    <Send className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
