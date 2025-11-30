import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { dummyQuizzes } from '@/data/dummyQuizzes';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle2, XCircle, ArrowLeft, Trophy } from 'lucide-react';

const StudentQuizzes = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: string]: number }>({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [earnedPoints, setEarnedPoints] = useState(0);

  // TODO: Replace with actual API call
  // GET /api/courses/:courseId/quizzes
  const quiz = dummyQuizzes.find(q => q.courseId === courseId);

  if (!quiz) {
    return (
      <div className="min-h-screen bg-background">
        <Header isAuthenticated userType="student" />
        <div className="container px-4 py-8">
          <p>No quiz available for this course</p>
        </div>
      </div>
    );
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestion.id]: answerIndex
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      handleSubmitQuiz();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = () => {
    // TODO: Submit quiz to backend
    // POST /api/quizzes/:quizId/submit
    // Body: { studentId, answers: selectedAnswers }

    let totalScore = 0;
    let pointsEarned = 0;

    quiz.questions.forEach(question => {
      const selectedAnswer = selectedAnswers[question.id];
      if (selectedAnswer === question.correctAnswer) {
        totalScore++;
        pointsEarned += question.points;
      }
    });

    setScore(totalScore);
    setEarnedPoints(pointsEarned);
    setShowResults(true);

    toast({
      title: "Quiz Submitted!",
      description: `You scored ${totalScore}/${quiz.questions.length} and earned ${pointsEarned} Kaushalya points!`,
    });
  };

  if (showResults) {
    const passed = earnedPoints >= quiz.passingScore;

    return (
      <div className="min-h-screen bg-background">
        <Header isAuthenticated userType="student" />
        <div className="container px-4 py-8 max-w-3xl mx-auto">
          <Card className="glass">
            <CardHeader>
              <CardTitle className="text-center text-2xl">Quiz Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${passed ? 'bg-success/20' : 'bg-destructive/20'} mb-4`}>
                  {passed ? (
                    <CheckCircle2 className="h-12 w-12 text-success" />
                  ) : (
                    <XCircle className="h-12 w-12 text-destructive" />
                  )}
                </div>
                <h3 className="text-2xl font-bold mb-2">
                  {passed ? 'Congratulations!' : 'Keep Learning!'}
                </h3>
                <p className="text-muted-foreground mb-4">
                  {passed ? 'You passed the quiz!' : 'You need more practice'}
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                  <span className="font-medium">Score</span>
                  <Badge variant={passed ? "default" : "secondary"}>
                    {score}/{quiz.questions.length}
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                  <span className="font-medium">Points Earned</span>
                  <Badge variant="default" className="flex items-center gap-1">
                    <Trophy className="h-4 w-4" />
                    {earnedPoints} Kaushalya Points
                  </Badge>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                  <span className="font-medium">Passing Score</span>
                  <span className="text-muted-foreground">{quiz.passingScore}/{quiz.totalPoints}</span>
                </div>
              </div>

              <div className="space-y-2">
                <Button onClick={() => navigate(`/course/${courseId}`)} className="w-full">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Course
                </Button>
                {!passed && (
                  <Button variant="outline" onClick={() => window.location.reload()} className="w-full">
                    Retake Quiz
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="student" />
      <div className="container px-4 py-8 max-w-3xl mx-auto">
        <Button variant="ghost" onClick={() => navigate(`/course/${courseId}`)} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Course
        </Button>

        <Card className="glass">
          <CardHeader>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <CardTitle>{quiz.title}</CardTitle>
                <Badge>Question {currentQuestionIndex + 1}/{quiz.questions.length}</Badge>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">{currentQuestion.question}</h3>
              <RadioGroup
                value={selectedAnswers[currentQuestion.id]?.toString()}
                onValueChange={(value) => handleAnswerSelect(parseInt(value))}
              >
                {currentQuestion.options.map((option, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 rounded-lg border border-white/10 hover:bg-white/5 transition-colors">
                    <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                    <Label htmlFor={`option-${index}`} className="flex-1 cursor-pointer">
                      {option}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            <div className="flex justify-between">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>
              <Button
                onClick={handleNext}
                disabled={selectedAnswers[currentQuestion.id] === undefined}
              >
                {currentQuestionIndex === quiz.questions.length - 1 ? 'Submit Quiz' : 'Next'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StudentQuizzes;
