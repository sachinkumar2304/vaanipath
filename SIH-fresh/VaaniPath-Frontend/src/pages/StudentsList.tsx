import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { listStudents, type Student } from '@/services/admin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Users, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '@/components/AdminLayout';

export default function StudentsList() {
    const { isAdmin } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();
    const [students, setStudents] = useState<Student[]>([]);
    const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!isAdmin) {
            navigate('/login');
            return;
        }
        loadStudents();
    }, [isAdmin]);

    useEffect(() => {
        // Filter students based on search query
        if (searchQuery.trim() === '') {
            setFilteredStudents(students);
        } else {
            const query = searchQuery.toLowerCase();
            const filtered = students.filter(
                student =>
                    student.full_name.toLowerCase().includes(query) ||
                    student.email.toLowerCase().includes(query)
            );
            setFilteredStudents(filtered);
        }
    }, [searchQuery, students]);

    const loadStudents = async () => {
        try {
            setIsLoading(true);
            const response = await listStudents();
            setStudents(response.students);
            setFilteredStudents(response.students);
        } catch (error) {
            console.error('Failed to load students:', error);
            toast({
                title: 'Error',
                description: 'Failed to load students list',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AdminLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Students Management</h2>
                    <p className="text-muted-foreground">
                        View and manage all registered students
                    </p>
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

                {/* Students List */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <div>
                                <CardTitle>All Students</CardTitle>
                                <CardDescription>
                                    Total: {filteredStudents.length} {filteredStudents.length !== students.length && `of ${students.length}`}
                                </CardDescription>
                            </div>
                            <Users className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="text-center py-8 text-muted-foreground">
                                Loading students...
                            </div>
                        ) : filteredStudents.length === 0 ? (
                            <div className="text-center py-8 text-muted-foreground">
                                {searchQuery ? 'No students found matching your search.' : 'No students registered yet.'}
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {filteredStudents.map((student) => (
                                    <div
                                        key={student.id}
                                        className="flex justify-between items-center p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                                    >
                                        <div>
                                            <p className="font-medium">{student.full_name}</p>
                                            <p className="text-sm text-muted-foreground">{student.email}</p>
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            Joined: {new Date(student.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </AdminLayout>
    );
}
