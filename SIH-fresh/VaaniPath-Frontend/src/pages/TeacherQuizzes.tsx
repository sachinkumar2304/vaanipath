import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, Save, Loader2 } from 'lucide-react';
import { getMyVideos, Video } from '@/services/videos';
import { createQuiz, Question } from '@/services/quiz';

const TeacherQuizzes = () => {
  const { t } = useTranslation();
  const { toast } = useToast();
  const [courses, setCourses] = useState<Video[]>([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [quizTitle, setQuizTitle] = useState('');
  const [quizDescription, setQuizDescription] = useState('');
  const [questions, setQuestions] = useState<Question[]>([
    { question: '', options: ['', '', '', ''], correctAnswer: 0, points: 10 }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setIsLoading(true);
      const response = await getMyVideos(1, 100); // Fetch up to 100 videos
      setCourses(response.videos);
    } catch (error) {
      console.error('Failed to load courses:', error);
      toast({
        title: t('common.error'),
        description: "Failed to load your courses",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const addQuestion = () => {
    setQuestions([...questions, { question: '', options: ['', '', '', ''], correctAnswer: 0, points: 10 }]);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const updateQuestion = (index: number, field: keyof Question, value: any) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], [field]: value };
    setQuestions(updated);
  };

  const updateOption = (questionIndex: number, optionIndex: number, value: string) => {
    const updated = [...questions];
    updated[questionIndex].options[optionIndex] = value;
    setQuestions(updated);
  };

  const handleSaveQuiz = async () => {
    if (!selectedCourse || !quizTitle || questions.length === 0) {
      toast({
        title: t('common.error'),
        description: t('teacherQuizzes.validationError'),
        variant: "destructive",
      });
      return;
    }

    // Validate questions
    for (const q of questions) {
      if (!q.question || q.options.some(opt => !opt)) {
        toast({
          title: t('common.error'),
          description: t('teacherQuizzes.validationError'),
          variant: "destructive",
        });
        return;
      }
    }

    try {
      setIsSaving(true);
      await createQuiz({
        courseId: selectedCourse,
        title: quizTitle,
        description: quizDescription,
        questions: questions
      });

      toast({
        title: t('teacherQuizzes.success'),
        description: "Your quiz has been successfully created",
      });

      // Reset form
      setSelectedCourse('');
      setQuizTitle('');
      setQuizDescription('');
      setQuestions([{ question: '', options: ['', '', '', ''], correctAnswer: 0, points: 10 }]);
    } catch (error: any) {
      console.error('Failed to save quiz:', error);
      toast({
        title: t('common.error'),
        description: error.response?.data?.detail || "Failed to create quiz",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="teacher" />
      <div className="container px-4 py-8 max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">{t('teacherQuizzes.title')}</h1>
          <p className="text-muted-foreground">{t('teacherQuizzes.subtitle')}</p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>{t('teacherQuizzes.quizDetails')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>{t('teacherQuizzes.selectCourseVideo')}</Label>
              <Select value={selectedCourse} onValueChange={setSelectedCourse} disabled={isLoading}>
                <SelectTrigger>
                  <SelectValue placeholder={isLoading ? t('common.loading') : t('teacherQuizzes.chooseCourse')} />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id}>
                      {course.title}
                    </SelectItem>
                  ))}
                  {courses.length === 0 && !isLoading && (
                    <div className="p-2 text-sm text-muted-foreground text-center">{t('teacherCourses.noCourses')}</div>
                  )}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>{t('teacherQuizzes.quizTitle')}</Label>
              <Input
                value={quizTitle}
                onChange={(e) => setQuizTitle(e.target.value)}
                placeholder={t('teacherQuizzes.enterQuizTitle')}
              />
            </div>

            <div>
              <Label>{t('teacherQuizzes.description')}</Label>
              <Textarea
                value={quizDescription}
                onChange={(e) => setQuizDescription(e.target.value)}
                placeholder={t('teacherQuizzes.enterDescription')}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {questions.map((question, qIndex) => (
            <Card key={qIndex}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{t('teacherQuizzes.question')} {qIndex + 1}</CardTitle>
                  {questions.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeQuestion(qIndex)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>{t('teacherQuizzes.question')}</Label>
                  <Input
                    value={question.question}
                    onChange={(e) => updateQuestion(qIndex, 'question', e.target.value)}
                    placeholder={t('teacherQuizzes.enterQuestion')}
                  />
                </div>

                <div className="space-y-2">
                  <Label>{t('teacherQuizzes.options')}</Label>
                  {question.options.map((option, oIndex) => (
                    <div key={oIndex} className="flex items-center gap-2">
                      <Input
                        value={option}
                        onChange={(e) => updateOption(qIndex, oIndex, e.target.value)}
                        placeholder={`${t('teacherQuizzes.options')} ${oIndex + 1}`}
                      />
                      <input
                        type="radio"
                        name={`correct-${qIndex}`}
                        checked={question.correctAnswer === oIndex}
                        onChange={() => updateQuestion(qIndex, 'correctAnswer', oIndex)}
                        className="cursor-pointer"
                      />
                    </div>
                  ))}
                  <p className="text-xs text-muted-foreground">Select the correct answer using the radio button</p>
                </div>

                <div>
                  <Label>{t('teacherQuizzes.points')}</Label>
                  <Input
                    type="number"
                    value={question.points}
                    onChange={(e) => updateQuestion(qIndex, 'points', parseInt(e.target.value))}
                    min="1"
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="flex gap-4 mt-6">
          <Button onClick={addQuestion} variant="outline" className="flex-1">
            <Plus className="h-4 w-4 mr-2" />
            {t('teacherQuizzes.addQuestion')}
          </Button>
          <Button onClick={handleSaveQuiz} className="flex-1" disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t('teacherQuizzes.saving')}
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {t('teacherQuizzes.saveQuiz')}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TeacherQuizzes;
