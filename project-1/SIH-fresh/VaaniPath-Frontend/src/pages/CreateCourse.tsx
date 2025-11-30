import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { createCourse, uploadCourseThumbnail } from '@/services/courses';
import { Upload, X, BookOpen, Languages, Tag } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';

import { INDIAN_LANGUAGES } from '@/constants/languages';

const CreateCourse = () => {
    const navigate = useNavigate();
    const { toast } = useToast();
    const { isTeacher } = useAuth();

    const [formData, setFormData] = useState({
        title: '',
        description: '',
        domain: '',
        source_language: 'en-IN',
        target_languages: INDIAN_LANGUAGES.filter(l => l.code !== 'en-IN').map(l => l.code),
    });

    const [thumbnail, setThumbnail] = useState<File | null>(null);
    const [thumbnailPreview, setThumbnailPreview] = useState<string>('');
    const [isUploading, setIsUploading] = useState(false);

    const domains = [
        'agriculture',
        'technology',
        'healthcare',
        'education',
        'business',
        'other',
    ];

    // Use INDIAN_LANGUAGES directly
    const languages = INDIAN_LANGUAGES;

    const handleThumbnailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {
                toast({
                    title: 'File too large',
                    description: 'Thumbnail should be less than 5MB',
                    variant: 'destructive',
                });
                return;
            }

            setThumbnail(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setThumbnailPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleLanguageToggle = (langCode: string) => {
        setFormData(prev => ({
            ...prev,
            target_languages: prev.target_languages.includes(langCode)
                ? prev.target_languages.filter(l => l !== langCode)
                : [...prev.target_languages, langCode],
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.title.trim()) {
            toast({
                title: 'Title required',
                description: 'Please enter a course title',
                variant: 'destructive',
            });
            return;
        }

        if (!formData.domain) {
            toast({
                title: 'Subject required',
                description: 'Please select a subject',
                variant: 'destructive',
            });
            return;
        }

        if (formData.target_languages.length === 0) {
            toast({
                title: 'Languages required',
                description: 'Please select at least one target language',
                variant: 'destructive',
            });
            return;
        }

        try {
            setIsUploading(true);

            let thumbnailUrl = '';
            if (thumbnail) {
                thumbnailUrl = await uploadCourseThumbnail(thumbnail);
            }

            const courseData = {
                ...formData,
                thumbnail_url: thumbnailUrl || undefined,
            };

            const newCourse = await createCourse(courseData);

            toast({
                title: 'Course created!',
                description: `"${newCourse.title}" has been created successfully`,
            });

            navigate(`/teacher/course/${newCourse.id}`);
        } catch (error: any) {
            console.error('Error creating course:', error);
            toast({
                title: 'Failed to create course',
                description: error.response?.data?.detail || 'An error occurred',
                variant: 'destructive',
            });
        } finally {
            setIsUploading(false);
        }
    };

    if (!isTeacher) {
        navigate('/teacherlogin');
        return null;
    }

    return (
        <div className="min-h-screen relative bg-background text-foreground transition-colors duration-300">
            <PremiumBackground />
            <Header isAuthenticated userType="teacher" />

            <div className="container px-4 py-12 lg:py-16 relative z-10 max-w-4xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mb-10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 rounded-2xl bg-primary/10 backdrop-blur-md border border-primary/20">
                            <BookOpen className="h-6 w-6 text-primary" />
                        </div>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-bold mb-3 text-foreground font-heading tracking-tight">
                        Create New Course
                    </h1>
                    <p className="text-lg text-muted-foreground">
                        Set up your course details and start adding content
                    </p>
                </motion.div>

                {/* Form */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                >
                    <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl">
                        <CardHeader>
                            <CardTitle>Course Information</CardTitle>
                            <CardDescription>
                                Fill in the basic details about your course
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleSubmit} className="space-y-6">
                                {/* Title */}
                                <div className="space-y-2">
                                    <Label htmlFor="title">Course Title *</Label>
                                    <Input
                                        id="title"
                                        placeholder="e.g., Introduction to Organic Farming"
                                        value={formData.title}
                                        onChange={(e) =>
                                            setFormData({ ...formData, title: e.target.value })
                                        }
                                        className="bg-background/50"
                                        required
                                    />
                                </div>

                                {/* Description */}
                                <div className="space-y-2">
                                    <Label htmlFor="description">Description</Label>
                                    <Textarea
                                        id="description"
                                        placeholder="Describe what students will learn in this course..."
                                        value={formData.description}
                                        onChange={(e) =>
                                            setFormData({ ...formData, description: e.target.value })
                                        }
                                        className="bg-background/50 min-h-[100px]"
                                        rows={4}
                                    />
                                </div>

                                {/* Subject */}
                                <div className="space-y-2">
                                    <Label htmlFor="domain">Subject *</Label>
                                    <Select
                                        value={formData.domain}
                                        onValueChange={(value) =>
                                            setFormData({ ...formData, domain: value })
                                        }
                                        required
                                    >
                                        <SelectTrigger className="bg-background/50">
                                            <div className="flex items-center gap-2">
                                                <Tag className="h-4 w-4 text-primary" />
                                                <SelectValue placeholder="Select subject" />
                                            </div>
                                        </SelectTrigger>
                                        <SelectContent>
                                            {domains.map((domain) => (
                                                <SelectItem key={domain} value={domain}>
                                                    {domain.charAt(0).toUpperCase() + domain.slice(1)}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Source Language */}
                                <div className="space-y-2">
                                    <Label htmlFor="source_language">Course Language *</Label>
                                    <Select
                                        value={formData.source_language}
                                        onValueChange={(value) =>
                                            setFormData({
                                                ...formData,
                                                source_language: value,
                                                target_languages: INDIAN_LANGUAGES
                                                    .filter(l => l.code !== value)
                                                    .map(l => l.code)
                                            })
                                        }
                                        required
                                    >
                                        <SelectTrigger className="bg-background/50">
                                            <div className="flex items-center gap-2">
                                                <Languages className="h-4 w-4 text-primary" />
                                                <SelectValue />
                                            </div>
                                        </SelectTrigger>
                                        <SelectContent>
                                            {languages.map((lang) => (
                                                <SelectItem key={lang.code} value={lang.code}>
                                                    {lang.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Target Languages */}
                                <div className="space-y-2">
                                    <Label>Translation Languages *</Label>
                                    <p className="text-sm text-muted-foreground mb-3">
                                        Select languages for course translation
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {languages
                                            .filter((lang) => lang.code !== formData.source_language)
                                            .map((lang) => (
                                                <Button
                                                    key={lang.code}
                                                    type="button"
                                                    variant={
                                                        formData.target_languages.includes(lang.code)
                                                            ? 'default'
                                                            : 'outline'
                                                    }
                                                    size="sm"
                                                    onClick={() => handleLanguageToggle(lang.code)}
                                                    className="transition-all"
                                                >
                                                    {lang.name}
                                                </Button>
                                            ))}
                                    </div>
                                </div>

                                {/* Thumbnail */}
                                <div className="space-y-2">
                                    <Label>Course Thumbnail (Optional)</Label>
                                    <p className="text-sm text-muted-foreground mb-3">
                                        Upload a thumbnail or we'll use the first video's thumbnail
                                    </p>

                                    {thumbnailPreview ? (
                                        <div className="relative aspect-video w-full max-w-md rounded-lg overflow-hidden border-2 border-border">
                                            <img
                                                src={thumbnailPreview}
                                                alt="Thumbnail preview"
                                                className="w-full h-full object-cover"
                                            />
                                            <Button
                                                type="button"
                                                variant="destructive"
                                                size="icon"
                                                className="absolute top-2 right-2"
                                                onClick={() => {
                                                    setThumbnail(null);
                                                    setThumbnailPreview('');
                                                }}
                                            >
                                                <X className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    ) : (
                                        <label className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors block max-w-md">
                                            <input
                                                type="file"
                                                accept="image/*"
                                                onChange={handleThumbnailChange}
                                                className="hidden"
                                            />
                                            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                                            <p className="text-sm text-muted-foreground">
                                                Click to upload thumbnail
                                                <br />
                                                (Max 5MB, JPG/PNG)
                                            </p>
                                        </label>
                                    )}
                                </div>

                                {/* Submit */}
                                <div className="flex gap-4 pt-6 border-t">
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={() => navigate('/teacher/courses')}
                                        disabled={isUploading}
                                    >
                                        Cancel
                                    </Button>
                                    <Button type="submit" disabled={isUploading} className="flex-1">
                                        {isUploading ? 'Creating Course...' : 'Create Course'}
                                    </Button>
                                </div>
                            </form>
                        </CardContent>
                    </Card>
                </motion.div>
            </div>
        </div>
    );
};

export default CreateCourse;
