import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { Upload, Video, FileAudio, FileText, CheckCircle, ArrowLeft } from 'lucide-react';
import { uploadVideo } from '@/services/videos';
import { getMyCourses, Course } from '@/services/courses';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { INDIAN_LANGUAGES } from '@/constants/languages';

const TeacherUpload = () => {
  const { toast } = useToast();
  const { isTeacher } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const courseIdParam = searchParams.get('courseId');

  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [contentType, setContentType] = useState<'video' | 'audio' | 'document'>('video');
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<string>(courseIdParam || '');

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    domain: '',
    source_language: 'en',
    target_languages: 'hi,ta,te',
    file: null as File | null,
  });

  useEffect(() => {
    if (!isTeacher) {
      navigate('/teacherlogin');
      return;
    }
    loadCourses();
  }, [isTeacher, navigate]);

  useEffect(() => {
    if (selectedCourseId && courses.length > 0) {
      const course = courses.find(c => c.id === selectedCourseId);
      if (course) {
        setFormData(prev => ({
          ...prev,
          domain: course.domain,
          source_language: course.source_language,
          target_languages: course.target_languages.join(','),
        }));
      }
    }
  }, [selectedCourseId, courses]);

  const loadCourses = async () => {
    try {
      const response = await getMyCourses();
      setCourses(response.courses);
    } catch (error) {
      console.error('Failed to load courses:', error);
      toast({
        title: 'Error',
        description: 'Failed to load courses. Please create a course first.',
        variant: 'destructive'
      });
    }
  };

  const getAcceptedFileTypes = () => {
    switch (contentType) {
      case 'video':
        return '.mp4,.avi,.mov,.mkv,.webm';
      case 'audio':
        return '.mp3,.wav,.m4a,.aac';
      case 'document':
        return '.pdf,.doc,.docx,.ppt,.pptx,.txt';
      default:
        return '';
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const maxSize = 500 * 1024 * 1024; // 500MB
      if (file.size > maxSize) {
        toast({
          title: 'File too large',
          description: 'Maximum file size is 500MB',
          variant: 'destructive'
        });
        return;
      }
      setFormData({ ...formData, file });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.file) {
      toast({
        title: 'No file selected',
        description: `Please select a ${contentType} file to upload`,
        variant: 'destructive'
      });
      return;
    }

    if (!selectedCourseId) {
      toast({
        title: 'Course required',
        description: 'Please select a course for this video',
        variant: 'destructive'
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      await uploadVideo(
        formData.file,
        {
          title: formData.title,
          description: formData.description,
          domain: formData.domain,
          source_language: formData.source_language,
          target_languages: formData.target_languages,
          course_id: selectedCourseId
        },
        (progress) => {
          setUploadProgress(progress);
        }
      );

      toast({
        title: '✅ Content Uploaded Successfully!',
        description: `Your ${contentType} "${formData.title}" has been uploaded.`,
      });

      setFormData({
        title: '',
        description: '',
        domain: '',
        source_language: 'en',
        target_languages: 'hi,ta,te',
        file: null,
      });
      setUploadProgress(0);

      setTimeout(() => {
        navigate(`/teacher/course/${selectedCourseId}`);
      }, 1500);

    } catch (error: any) {
      console.error('Upload error:', error);
      toast({
        title: '❌ Upload Failed',
        description: error.response?.data?.detail || 'Failed to upload content.',
        variant: 'destructive'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative transition-colors duration-300">
      <PremiumBackground />
      <Header isAuthenticated userType="teacher" />

      <div className="container px-4 py-8 relative z-10">
        <Button
          variant="ghost"
          className="mb-6"
          onClick={() => navigate(courseIdParam ? `/teacher/course/${courseIdParam}` : '/teacher/courses')}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to {courseIdParam ? 'Course' : 'Courses'}
        </Button>

        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            Upload Content
          </h1>
          <p className="text-muted-foreground">
            Add a new video to your course
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          <Card className="glass-card border-white/20 dark:border-white/10 shadow-xl">
            <CardHeader>
              <CardTitle>Content Details</CardTitle>
              <CardDescription>
                Fill in the details and upload your educational content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">

                {/* Course Selection */}
                <div className="space-y-2">
                  <Label htmlFor="course">Course *</Label>
                  <Select
                    value={selectedCourseId}
                    onValueChange={setSelectedCourseId}
                    disabled={!!courseIdParam || isUploading}
                  >
                    <SelectTrigger id="course">
                      <SelectValue placeholder="Select a course" />
                    </SelectTrigger>
                    <SelectContent>
                      {courses.map((course) => (
                        <SelectItem key={course.id} value={course.id}>
                          {course.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {!courses.length && (
                    <p className="text-xs text-destructive">
                      No courses found. <span className="underline cursor-pointer" onClick={() => navigate('/teacher/create-course')}>Create a course first</span>.
                    </p>
                  )}
                </div>

                {/* Content Type Selection */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <button
                    type="button"
                    onClick={() => setContentType('video')}
                    className={`p-4 rounded-lg border-2 transition-all flex flex-col items-center justify-center gap-2 ${contentType === 'video'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 text-muted-foreground'
                      }`}
                  >
                    <Video className="h-6 w-6" />
                    <span className="text-sm font-medium">Video</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setContentType('audio')}
                    className={`p-4 rounded-lg border-2 transition-all flex flex-col items-center justify-center gap-2 ${contentType === 'audio'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 text-muted-foreground'
                      }`}
                  >
                    <FileAudio className="h-6 w-6" />
                    <span className="text-sm font-medium">Audio</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setContentType('document')}
                    className={`p-4 rounded-lg border-2 transition-all flex flex-col items-center justify-center gap-2 ${contentType === 'document'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 text-muted-foreground'
                      }`}
                  >
                    <FileText className="h-6 w-6" />
                    <span className="text-sm font-medium">Document</span>
                  </button>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    placeholder={`Enter ${contentType} title`}
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                    disabled={isUploading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder={`Describe the ${contentType} content`}
                    rows={4}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    disabled={isUploading}
                  />
                </div>

                {/* Inherited but editable fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2 opacity-70 pointer-events-none">
                    <Label>Subject (Inherited)</Label>
                    <Input value={formData.domain} readOnly />
                  </div>
                  <div className="space-y-2">
                    <Label>Source Language</Label>
                    <Select
                      value={formData.source_language}
                      onValueChange={(value) => setFormData({ ...formData, source_language: value })}
                      disabled={isUploading}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select language" />
                      </SelectTrigger>
                      <SelectContent>
                        {INDIAN_LANGUAGES.map((lang) => (
                          <SelectItem key={lang.code} value={lang.code}>
                            {lang.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="file">Upload {contentType === 'video' ? 'Video' : contentType === 'audio' ? 'Audio' : 'Document'} File *</Label>
                  <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-smooth">
                    {contentType === 'video' && <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />}
                    {contentType === 'audio' && <FileAudio className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />}
                    {contentType === 'document' && <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />}

                    <Input
                      id="file"
                      type="file"
                      accept={getAcceptedFileTypes()}
                      onChange={handleFileChange}
                      className="hidden"
                      required
                      disabled={isUploading}
                    />
                    <Label htmlFor="file" className="cursor-pointer">
                      {formData.file ? (
                        <div>
                          <span className="text-primary font-medium">{formData.file.name}</span>
                          <p className="text-xs text-muted-foreground mt-1">
                            {(formData.file.size / (1024 * 1024)).toFixed(2)} MB
                          </p>
                        </div>
                      ) : (
                        <>
                          <span className="text-primary font-medium">Click to upload</span>
                          <span className="text-muted-foreground"> or drag and drop</span>
                        </>
                      )}
                    </Label>
                    <p className="text-xs text-muted-foreground mt-2">
                      Accepted: {getAcceptedFileTypes().replace(/\./g, '').toUpperCase().replace(/,/g, ', ')} (Max 500MB)
                    </p>
                  </div>
                </div>

                {isUploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uploading...</span>
                      <span className="font-medium">{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} className="w-full" />
                    {uploadProgress === 100 && (
                      <div className="flex items-center gap-2 text-sm text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span>Upload complete! Processing...</span>
                      </div>
                    )}
                  </div>
                )}

                <Button
                  type="submit"
                  size="lg"
                  className="w-full"
                  disabled={isUploading}
                >
                  {isUploading ? (
                    <>
                      <Upload className="mr-2 h-4 w-4 animate-pulse" />
                      Uploading... {uploadProgress}%
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload {contentType === 'video' ? 'Video' : contentType === 'audio' ? 'Audio' : 'Document'}
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TeacherUpload;
