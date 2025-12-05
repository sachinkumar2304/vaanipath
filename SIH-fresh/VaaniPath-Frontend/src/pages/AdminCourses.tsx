import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { deleteCourse } from '@/services/admin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { BookOpen, Search, Trash2, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '@/components/AdminLayout';
import api from '@/services/api';

interface Course {
    id: string;
    title: string;
    description: string;
    domain: string;
    language: string;
    teacher_id: string;
    created_at: string;
    thumbnail_url?: string;
    videos_count?: number;
}

export default function AdminCourses() {
    const { isAdmin } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();
    const [courses, setCourses] = useState<Course[]>([]);
    const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [courseToDelete, setCourseToDelete] = useState<Course | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        if (!isAdmin) {
            navigate('/login');
            return;
        }
        loadCourses();
    }, [isAdmin]);

    useEffect(() => {
        // Filter courses based on search query
        if (searchQuery.trim() === '') {
            setFilteredCourses(courses);
        } else {
            const query = searchQuery.toLowerCase();
            const filtered = courses.filter(
                course =>
                    course.title.toLowerCase().includes(query) ||
                    course.description?.toLowerCase().includes(query) ||
                    course.domain?.toLowerCase().includes(query)
            );
            setFilteredCourses(filtered);
        }
    }, [searchQuery, courses]);

    const loadCourses = async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/courses', {
                params: { page: 1, page_size: 100 }
            });
            setCourses(response.data.courses || []);
            setFilteredCourses(response.data.courses || []);
        } catch (error) {
            console.error('Failed to load courses:', error);
            toast({
                title: 'Error',
                description: 'Failed to load courses list',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteCourse = async () => {
        if (!courseToDelete) return;
        
        try {
            setIsDeleting(true);
            await deleteCourse(courseToDelete.id);
            toast({
                title: 'Course Deleted',
                description: `"${courseToDelete.title}" has been permanently deleted.`,
            });
            loadCourses(); // Refresh the list
            setDeleteDialogOpen(false);
            setCourseToDelete(null);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to delete course',
                variant: 'destructive'
            });
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <AdminLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Courses Management</h2>
                        <p className="text-muted-foreground">
                            View and manage all courses on the platform
                        </p>
                    </div>
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search by title, description, or domain..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                    />
                </div>

                {/* Courses List */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <div>
                                <CardTitle>All Courses</CardTitle>
                                <CardDescription>
                                    Total: {filteredCourses.length} {filteredCourses.length !== courses.length && `of ${courses.length}`}
                                </CardDescription>
                            </div>
                            <BookOpen className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="text-center py-8 text-muted-foreground">
                                Loading courses...
                            </div>
                        ) : filteredCourses.length === 0 ? (
                            <div className="text-center py-8 text-muted-foreground">
                                {searchQuery ? 'No courses found matching your search.' : 'No courses created yet.'}
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {filteredCourses.map((course) => (
                                    <div
                                        key={course.id}
                                        className="flex justify-between items-start p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                                    >
                                        <div className="flex gap-4 flex-1">
                                            {course.thumbnail_url && (
                                                <img 
                                                    src={course.thumbnail_url} 
                                                    alt={course.title}
                                                    className="w-32 h-20 object-cover rounded"
                                                />
                                            )}
                                            <div className="flex-1">
                                                <p className="font-medium mb-1">{course.title}</p>
                                                <p className="text-sm text-muted-foreground line-clamp-2">
                                                    {course.description || 'No description'}
                                                </p>
                                                <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                                                    <span>Domain: {course.domain || 'N/A'}</span>
                                                    <span>Language: {course.language || 'N/A'}</span>
                                                    <span>Videos: {course.videos_count || 0}</span>
                                                    <span>Created: {new Date(course.created_at).toLocaleDateString()}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => navigate(`/course/${course.id}`)}
                                            >
                                                <Eye className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="destructive"
                                                size="sm"
                                                onClick={() => {
                                                    setCourseToDelete(course);
                                                    setDeleteDialogOpen(true);
                                                }}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Delete Confirmation Dialog */}
                <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Delete Course</DialogTitle>
                            <DialogDescription>
                                Are you sure you want to delete <strong>"{courseToDelete?.title}"</strong>?
                            </DialogDescription>
                        </DialogHeader>
                        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 my-4">
                            <p className="text-sm font-semibold text-destructive mb-2">⚠️ Warning: This action cannot be undone!</p>
                            <p className="text-sm text-muted-foreground">This will permanently delete:</p>
                            <ul className="text-sm text-muted-foreground list-disc list-inside mt-2 space-y-1">
                                <li>The course and all its metadata</li>
                                <li>All videos in this course</li>
                                <li>All enrollments and student progress</li>
                                <li>All quizzes and student responses</li>
                                <li>All reviews and ratings</li>
                            </ul>
                        </div>
                        <DialogFooter>
                            <Button
                                variant="outline"
                                onClick={() => {
                                    setDeleteDialogOpen(false);
                                    setCourseToDelete(null);
                                }}
                                disabled={isDeleting}
                            >
                                Cancel
                            </Button>
                            <Button
                                variant="destructive"
                                onClick={handleDeleteCourse}
                                disabled={isDeleting}
                            >
                                {isDeleting ? 'Deleting...' : 'Delete Course'}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </AdminLayout>
    );
}
