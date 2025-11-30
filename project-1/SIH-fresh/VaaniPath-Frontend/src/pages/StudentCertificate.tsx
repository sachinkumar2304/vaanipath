import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Award, Download, Share2, CheckCircle2 } from 'lucide-react';
import { dummyCourses } from '@/data/dummyCourses';

const StudentCertificate = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  // TODO: Fetch certificate data from backend
  // GET /api/courses/:courseId/certificate/:studentId
  const course = dummyCourses.find(c => c.id === courseId);
  const studentName = "Student Name"; // TODO: Get from auth context
  const completionDate = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  if (!course) {
    return (
      <div className="min-h-screen bg-background">
        <Header isAuthenticated userType="student" />
        <div className="container px-4 py-8">
          <p>Course not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="student" />
      <div className="container px-4 py-8 max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
            <Award className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Certificate of Completion</h1>
          <p className="text-muted-foreground">Congratulations on completing the course!</p>
        </div>

        <Card className="mb-6 bg-gradient-hero border-2 border-primary/20">
          <CardContent className="p-8 md:p-12">
            <div className="text-center space-y-6">
              <div className="mb-6">
                <Award className="h-16 w-16 mx-auto text-primary mb-4" />
                <h2 className="text-2xl font-bold mb-2">Certificate of Achievement</h2>
                <p className="text-muted-foreground">This is to certify that</p>
              </div>

              <div className="py-6 border-y-2 border-primary/20">
                <h3 className="text-3xl md:text-4xl font-bold text-primary mb-2">{studentName}</h3>
                <p className="text-muted-foreground">has successfully completed the course</p>
              </div>

              <div className="space-y-4">
                <h4 className="text-2xl font-bold">{course.title}</h4>
                <p className="text-muted-foreground">Instructed by {course.teacherName}</p>
                <p className="text-sm text-muted-foreground">Completed on {completionDate}</p>
              </div>

              <div className="flex items-center justify-center gap-4 pt-6">
                <CheckCircle2 className="h-6 w-6 text-success" />
                <span className="text-sm font-medium">Verified by VANNIपथ</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-4 justify-center">
          <Button onClick={() => navigate(`/course/${courseId}`)}>
            Back to Course
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
          <Button variant="outline">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </div>
    </div>
  );
};

export default StudentCertificate;
