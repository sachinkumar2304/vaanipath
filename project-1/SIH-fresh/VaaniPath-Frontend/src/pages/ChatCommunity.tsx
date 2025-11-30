import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { MessageCircle, ThumbsUp, MessageSquare, Languages } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Post {
  id: string;
  author: string;
  title: string;
  content: string;
  language: string;
  likes: number;
  replies: number;
  timestamp: string;
  tags: string[];
}

const ChatCommunity = () => {
  const { isTeacher } = useAuth();
  const { toast } = useToast();
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [showNewPost, setShowNewPost] = useState(false);
  const [postTitle, setPostTitle] = useState('');
  const [postContent, setPostContent] = useState('');

  // TODO: Fetch posts from backend
  // GET /api/community/posts?language=:language
  const posts: Post[] = [
    {
      id: '1',
      author: 'Rahul S',
      title: 'How to optimize Python loops?',
      content: 'I am working on a large dataset and my loops are taking too long. Any suggestions for optimization?',
      language: 'English',
      likes: 24,
      replies: 8,
      timestamp: '2 hours ago',
      tags: ['Python', 'Performance']
    },
    {
      id: '2',
      author: 'Priya M',
      title: 'Best resources for learning React?',
      content: 'Can someone recommend good tutorials or courses for learning React from scratch?',
      language: 'Hindi',
      likes: 15,
      replies: 12,
      timestamp: '5 hours ago',
      tags: ['React', 'Web Development']
    },
    {
      id: '3',
      author: 'Amit K',
      title: 'Database design question',
      content: 'Should I use SQL or NoSQL for an e-commerce application? What are the pros and cons?',
      language: 'English',
      likes: 31,
      replies: 19,
      timestamp: '1 day ago',
      tags: ['Database', 'Architecture']
    }
  ];

  const handleCreatePost = () => {
    // TODO: Create post via backend with translation
    // POST /api/community/posts
    // Body: { title, content, language, authorId }

    if (!postTitle || !postContent) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Post Created!",
      description: "Your question has been posted to the community",
    });

    setShowNewPost(false);
    setPostTitle('');
    setPostContent('');
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
      <div className="container px-4 py-8 max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">Community Forum</h1>
            <p className="text-muted-foreground">Ask questions and help fellow learners</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Languages className="h-5 w-5 text-muted-foreground" />
              <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="hindi">हिंदी</SelectItem>
                  <SelectItem value="tamil">தமிழ்</SelectItem>
                  <SelectItem value="telugu">తెలుగు</SelectItem>
                  <SelectItem value="marathi">मराठी</SelectItem>
                  <SelectItem value="bengali">বাংলা</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={() => setShowNewPost(!showNewPost)}>
              <MessageCircle className="h-4 w-4 mr-2" />
              New Post
            </Button>
          </div>
        </div>

        {showNewPost && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Create New Post</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Input
                  placeholder="Post title"
                  value={postTitle}
                  onChange={(e) => setPostTitle(e.target.value)}
                />
              </div>
              <div>
                <Textarea
                  placeholder="Describe your question or discussion topic..."
                  value={postContent}
                  onChange={(e) => setPostContent(e.target.value)}
                  rows={5}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleCreatePost}>Post Question</Button>
                <Button variant="outline" onClick={() => setShowNewPost(false)}>Cancel</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-4">
          {posts.map((post) => (
            <Card key={post.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <Avatar>
                    <AvatarFallback>{post.author[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-semibold mb-1">{post.title}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>{post.author}</span>
                          <span>•</span>
                          <span>{post.timestamp}</span>
                          <Badge variant="outline" className="ml-2">{post.language}</Badge>
                        </div>
                      </div>
                    </div>
                    <p className="text-muted-foreground mb-3">{post.content}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex gap-2">
                        {post.tags.map((tag) => (
                          <Badge key={tag} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                      <div className="flex items-center gap-4 ml-auto">
                        <button className="flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors">
                          <ThumbsUp className="h-4 w-4" />
                          <span>{post.likes}</span>
                        </button>
                        <button className="flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors">
                          <MessageSquare className="h-4 w-4" />
                          <span>{post.replies}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatCommunity;
