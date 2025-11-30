import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { getCourseById, updateCourse, CourseWithVideos } from '@/services/courses';
import { deleteVideo } from '@/services/videos';
import {
    BookOpen, Upload, Video, Trash2, Edit, ArrowLeft,
    GripVertical, Play, Clock, Languages
} from 'lucide-react';
import { motion } from 'framer-motion';

const CourseManagement = () => {
    const { courseId } = useParams<{ courseId: string }>();
    const navigate = useNavigate();
    const { toast } = useToast();
    const { isTeacher } = useAuth();

    const [course, setCourse] = useState<CourseWithVideos | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isEditingCourse, setIsEditingCourse] = useState(false);
    const [editForm, setEditForm] = useState({
        title: '',
        description: '',
    });

    useEffect(() => {
        if (!isTeacher) {
            navigate('/teacherlogin');
            return;
        }
        if (courseId) {
            loadCourse();
        }
    }, [isTeacher, courseId, navigate]);

    const loadCourse = async () => {
        if (!courseId) return;

        try {
            setIsLoading(true);
            const data = await getCourseById(courseId);
            setCourse(data);
            setEditForm({
                title: data.title,
                description: data.description || '',
            });
        } catch (error) {
            console.error('Failed to load course:', error);
            toast({
                title: 'Error',
                description: 'Failed to load course details',
                variant: 'destructive',
            });
            navigate('/teacher/courses');
        } finally {
            setIsLoading(false);
        }
    };

    const handleUpdateCourse = async () => {
        if (!courseId) return;

        try {
            await updateCourse(courseId, editForm);
            toast({
                title: 'Course Updated',
                description: 'Course details have been updated successfully',
            });
            setIsEditingCourse(false);
            loadCourse();
        } catch (error: any) {
            console.error('Update error:', error);
            toast({
                title: 'Update Failed',
                description: error.response?.data?.detail || 'Failed to update course',
                variant: 'destructive',
            });
        }
    };

    const handleDeleteVideo = async (videoId: string, videoTitle: string) => {
        try {
            await deleteVideo(videoId);
            toast({
                title: 'Video Deleted',
                description: `"${videoTitle}" has been removed from the course`,
            });
            loadCourse();
        } catch (error: any) {
            console.error('Delete error:', error);
            toast({
                title: 'Delete Failed',
                description: error.response?.data?.detail || 'Failed to delete video',
                variant: 'destructive',
            });
        }
    };

    const formatDuration = (seconds?: number) => {
        if (!seconds) return 'Unknown';
        const mins = Math.floor(seconds / 60);
        if (mins < 60) return `${mins}m`;
        const hrs = Math.floor(mins / 60);
        const remainMins = mins % 60;
        return `${hrs}h ${remainMins}m`;
    };

    if (isLoading) {
        return (
            <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
                <PremiumBackground />
                <Header isAuthenticated userType="teacher" />
                <div className="flex items-center justify-center min-h-[60vh]">
                    <BookOpen className="h-16 w-16 text-primary animate-pulse" />
                </div>
            </div>
        );
    }

    if (!course) {
        return null;
    }

    return (
        <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
            <PremiumBackground />
            <Header isAuthenticated userType="teacher" />

            <div className="container px-4 py-12 lg:py-16 relative z-10">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mb-10"
                >
                    <Button
                        variant="ghost"
                        className="mb-4"
                        onClick={() => navigate('/teacher/courses')}
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Courses
                    </Button>

                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-3 rounded-2xl bg-primary/10 backdrop-blur-md border border-primary/20">
                                    <BookOpen className="h-6 w-6 text-primary" />
                                </div>
                                <Badge variant="secondary">{course.domain}</Badge>
                            </div>
                            <h1 className="text-4xl md:text-5xl font-bold mb-3 text-foreground font-heading tracking-tight">
                                {course.title}
                            </h1>
                            <p className="text-lg text-muted-foreground max-w-3xl">
                                {course.description || 'No description'}
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <Dialog open={isEditingCourse} onOpenChange={setIsEditingCourse}>
                                <DialogTrigger asChild>
                                    <Button variant="outline">
                                        <Edit className="mr-2 h-4 w-4" />
                                        Edit Course
                                    </Button>
                                </DialogTrigger>
                                <DialogContent>
                                    <DialogHeader>
                                        <DialogTitle>Edit Course</DialogTitle>
                                        <DialogDescription>
                                            Update your course title and description
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="space-y-4 py-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="edit-title">Title</Label>
                                            <Input
                                                id="edit-title"
                                                value={editForm.title}
                                                onChange={(e) =>
                                                    setEditForm({ ...editForm, title: e.target.value })
                                                }
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="edit-description">Description</Label>
                                            <Textarea
                                                id="edit-description"
                                                value={editForm.description}
                                                onChange={(e) =>
                                                    setEditForm({ ...editForm, description: e.target.value })
                                                }
                                                rows={4}
                                            />
                                        </div>
                                    </div>
                                    <div className="flex justify-end gap-3">
                                        <Button
                                            variant="outline"
                                            onClick={() => setIsEditingCourse(false)}
                                        >
                                            Cancel
                                        </Button>
                                        <Button onClick={handleUpdateCourse}>Save Changes</Button>
                                    </div>
                                </DialogContent>
                            </Dialog>

                            <Button asChild variant="secondary">
                                <Link to={`/course/${courseId}`}>
                                    <Play className="mr-2 h-4 w-4" />
                                    View Course
                                </Link>
                            </Button>

                            <Button asChild>
                                <Link to={`/teacher/upload?courseId=${courseId}`}>
                                    <Upload className="mr-2 h-4 w-4" />
                                    Add Video
                                </Link>
                            </Button>
                        </div>
                    </div>
                </motion.div>

                {/* Course Stats */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10"
                >
                    <Card className="glass-card border-white/20 dark:border-white/10">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Video className="h-8 w-8 text-primary" />
                                <div>
                                    <p className="text-2xl font-bold">{course.total_videos || 0}</p>
                                    <p className="text-sm text-muted-foreground">Videos</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="glass-card border-white/20 dark:border-white/10">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Clock className="h-8 w-8 text-primary" />
                                <div>
                                    <p className="text-2xl font-bold">{formatDuration(course.total_duration)}</p>
                                    <p className="text-sm text-muted-foreground">Duration</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="glass-card border-white/20 dark:border-white/10">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Languages className="h-8 w-8 text-primary" />
                                <div>
                                    <p className="text-2xl font-bold">{course.target_languages.length}</p>
                                    <p className="text-sm text-muted-foreground">Languages</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="glass-card border-white/20 dark:border-white/10">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <BookOpen className="h-8 w-8 text-primary" />
                                <div>
                                    <p className="text-2xl font-bold">{course.source_language.toUpperCase()}</p>
                                    <p className="text-sm text-muted-foreground">Source</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Videos List */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                >
                    <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl">
                        <CardHeader>
                            <CardTitle>Course Videos</CardTitle>
                            <CardDescription>
                                Manage the videos in your course. Drag to reorder.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {course.videos.length > 0 ? (
                                <div className="space-y-3">
                                    {course.videos.map((video, index) => (
                                        <div
                                            key={video.id}
                                            className="flex items-center gap-4 p-4 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                                        >
                                            <GripVertical className="h-5 w-5 text-muted-foreground cursor-move" />

                                            <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                                                <Video className="h-6 w-6 text-primary" />
                                            </div>

                                            <div className="flex-1 min-w-0">
                                                <h4 className="font-medium truncate">{video.title}</h4>
                                                <p className="text-sm text-muted-foreground">
                                                    {formatDuration(video.duration)} • {video.status}
                                                </p>
                                            </div>

                                            <div className="flex gap-2">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    asChild
                                                >
                                                    <Link to={`/course-player/${courseId}?videoId=${video.id}`}>
                                                        <Play className="h-4 w-4" />
                                                    </Link>
                                                </Button>

                                                <AlertDialog>
                                                    <AlertDialogTrigger asChild>
                                                        <Button variant="ghost" size="icon" className="text-destructive">
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </AlertDialogTrigger>
                                                    <AlertDialogContent>
                                                        <AlertDialogHeader>
                                                            <AlertDialogTitle>Delete Video?</AlertDialogTitle>
                                                            <AlertDialogDescription>
                                                                Remove "{video.title}" from this course? This action cannot be undone.
                                                            </AlertDialogDescription>
                                                        </AlertDialogHeader>
                                                        <AlertDialogFooter>
                                                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                            <AlertDialogAction
                                                                onClick={() => handleDeleteVideo(video.id, video.title)}
                                                                className="bg-destructive hover:bg-destructive/90"
                                                            >
                                                                Delete
                                                            </AlertDialogAction>
                                                        </AlertDialogFooter>
                                                    </AlertDialogContent>
                                                </AlertDialog>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12">
                                    <Video className="h-16 w-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                                    <h3 className="text-lg font-medium mb-2">No videos yet</h3>
                                    <p className="text-muted-foreground mb-6">
                                        Start adding videos to your course
                                    </p>
                                    <Button asChild>
                                        <Link to={`/teacher/upload?courseId=${courseId}`}>
                                            <Upload className="mr-2 h-4 w-4" />
                                            Add First Video
                                        </Link>
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </motion.div>
            </div>
        </div>
    );
};

export default CourseManagement;
