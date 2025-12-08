import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { listTutors, createTutor, deleteTutor, type Tutor, type TutorCreate, type TutorResponse } from '@/services/admin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { GraduationCap, UserPlus, Copy, Search, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '@/components/AdminLayout';

export default function TutorsList() {
    const { isAdmin } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();
    const [tutors, setTutors] = useState<Tutor[]>([]);
    const [filteredTutors, setFilteredTutors] = useState<Tutor[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [createdTutor, setCreatedTutor] = useState<TutorResponse | null>(null);
    const [newTutor, setNewTutor] = useState<TutorCreate>({
        email: '',
        password: '',
        full_name: ''
    });
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [tutorToDelete, setTutorToDelete] = useState<Tutor | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        if (!isAdmin) {
            navigate('/login');
            return;
        }
        loadTutors();
    }, [isAdmin]);

    useEffect(() => {
        // Filter tutors based on search query
        if (searchQuery.trim() === '') {
            setFilteredTutors(tutors);
        } else {
            const query = searchQuery.toLowerCase();
            const filtered = tutors.filter(
                tutor =>
                    tutor.full_name.toLowerCase().includes(query) ||
                    tutor.email.toLowerCase().includes(query)
            );
            setFilteredTutors(filtered);
        }
    }, [searchQuery, tutors]);

    const loadTutors = async () => {
        try {
            setIsLoading(true);
            const response = await listTutors();
            setTutors(response.tutors);
            setFilteredTutors(response.tutors);
        } catch (error) {
            console.error('Failed to load tutors:', error);
            toast({
                title: 'Error',
                description: 'Failed to load tutors list',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateTutor = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await createTutor(newTutor);
            setCreatedTutor(response);
            toast({
                title: 'Tutor Created!',
                description: `Tutor account created for ${response.email}`,
            });
            loadTutors(); // Refresh data
            setNewTutor({ email: '', password: '', full_name: '' });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to create tutor',
                variant: 'destructive'
            });
        }
    };

    const copyCredentials = () => {
        if (createdTutor) {
            const credentials = `Email: ${createdTutor.email}\nPassword: ${createdTutor.temporary_password}`;
            navigator.clipboard.writeText(credentials);
            toast({
                title: 'Copied!',
                description: 'Credentials copied to clipboard'
            });
        }
    };

    const handleDeleteTutor = async () => {
        if (!tutorToDelete) return;
        
        try {
            setIsDeleting(true);
            const result = await deleteTutor(tutorToDelete.id);
            toast({
                title: 'Tutor Deleted',
                description: `${result.tutor_name} and all associated data have been permanently deleted. Courses: ${result.deleted_resources.courses}, Videos: ${result.deleted_resources.videos}`,
            });
            loadTutors(); // Refresh the list
            setDeleteDialogOpen(false);
            setTutorToDelete(null);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to delete tutor',
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
                        <h2 className="text-3xl font-bold tracking-tight">Tutors Management</h2>
                        <p className="text-muted-foreground">
                            Create and manage tutor accounts
                        </p>
                    </div>
                    <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
                        <DialogTrigger asChild>
                            <Button>
                                <UserPlus className="h-4 w-4 mr-2" />
                                Create Tutor
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Create Tutor Account</DialogTitle>
                                <DialogDescription>
                                    Create a new tutor account. You'll receive credentials to share with the tutor.
                                </DialogDescription>
                            </DialogHeader>

                            {!createdTutor ? (
                                <form onSubmit={handleCreateTutor} className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="email">Email</Label>
                                        <Input
                                            id="email"
                                            type="email"
                                            value={newTutor.email}
                                            onChange={(e) => setNewTutor({ ...newTutor, email: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="full_name">Full Name</Label>
                                        <Input
                                            id="full_name"
                                            value={newTutor.full_name}
                                            onChange={(e) => setNewTutor({ ...newTutor, full_name: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="password">Temporary Password</Label>
                                        <Input
                                            id="password"
                                            type="password"
                                            value={newTutor.password}
                                            onChange={(e) => setNewTutor({ ...newTutor, password: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <Button type="submit" className="w-full">Create Tutor</Button>
                                </form>
                            ) : (
                                <div className="space-y-4">
                                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                                        <h3 className="font-semibold mb-2">✅ Tutor Created Successfully!</h3>
                                        <p className="text-sm mb-4">Share these credentials with the tutor:</p>
                                        <div className="bg-background p-3 rounded border font-mono text-sm">
                                            <div><strong>Email:</strong> {createdTutor.email}</div>
                                            <div><strong>Password:</strong> {createdTutor.temporary_password}</div>
                                        </div>
                                        <Button
                                            onClick={copyCredentials}
                                            variant="outline"
                                            className="w-full mt-3"
                                        >
                                            <Copy className="h-4 w-4 mr-2" />
                                            Copy Credentials
                                        </Button>
                                    </div>
                                    <Button
                                        onClick={() => {
                                            setCreatedTutor(null);
                                            setIsCreateModalOpen(false);
                                        }}
                                        className="w-full"
                                    >
                                        Done
                                    </Button>
                                </div>
                            )}
                        </DialogContent>
                    </Dialog>
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search by name or email..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                    />
                </div>

                {/* Tutors List */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <div>
                                <CardTitle>All Tutors</CardTitle>
                                <CardDescription>
                                    Total: {filteredTutors.length} {filteredTutors.length !== tutors.length && `of ${tutors.length}`}
                                </CardDescription>
                            </div>
                            <GraduationCap className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="text-center py-8 text-muted-foreground">
                                Loading tutors...
                            </div>
                        ) : filteredTutors.length === 0 ? (
                            <div className="text-center py-8 text-muted-foreground">
                                {searchQuery ? 'No tutors found matching your search.' : 'No tutors created yet. Create one to get started!'}
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {filteredTutors.map((tutor) => (
                                    <div
                                        key={tutor.id}
                                        className="flex justify-between items-center p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                                    >
                                        <div>
                                            <p className="font-medium">{tutor.full_name}</p>
                                            <p className="text-sm text-muted-foreground">{tutor.email}</p>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-sm text-muted-foreground">
                                                Joined: {new Date(tutor.created_at).toLocaleDateString()}
                                            </div>
                                            <Button
                                                variant="destructive"
                                                size="sm"
                                                onClick={() => {
                                                    setTutorToDelete(tutor);
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
                            <DialogTitle>Delete Tutor Account</DialogTitle>
                            <DialogDescription>
                                Are you sure you want to delete <strong>{tutorToDelete?.full_name}</strong>?
                            </DialogDescription>
                        </DialogHeader>
                        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 my-4">
                            <p className="text-sm font-semibold text-destructive mb-2">⚠️ Warning: This action cannot be undone!</p>
                            <p className="text-sm text-muted-foreground">This will permanently delete:</p>
                            <ul className="text-sm text-muted-foreground list-disc list-inside mt-2 space-y-1">
                                <li>The tutor account</li>
                                <li>All courses created by this tutor</li>
                                <li>All videos uploaded by this tutor</li>
                                <li>All enrollments, quizzes, and related data</li>
                            </ul>
                        </div>
                        <DialogFooter>
                            <Button
                                variant="outline"
                                onClick={() => {
                                    setDeleteDialogOpen(false);
                                    setTutorToDelete(null);
                                }}
                                disabled={isDeleting}
                            >
                                Cancel
                            </Button>
                            <Button
                                variant="destructive"
                                onClick={handleDeleteTutor}
                                disabled={isDeleting}
                            >
                                {isDeleting ? 'Deleting...' : 'Delete Tutor'}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </AdminLayout>
    );
}
