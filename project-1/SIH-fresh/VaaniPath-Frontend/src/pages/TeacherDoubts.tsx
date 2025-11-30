import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { MessageCircle, User, Clock, CheckCircle, Send, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getTeacherDoubts, answerDoubt, Doubt } from '@/services/doubts';

const TeacherDoubts = () => {
  const { toast } = useToast();
  const [doubts, setDoubts] = useState<Doubt[]>([]);
  const [selectedDoubt, setSelectedDoubt] = useState<Doubt | null>(null);
  const [answer, setAnswer] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'answered'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadDoubts();
  }, []);

  const loadDoubts = async () => {
    try {
      setIsLoading(true);
      const data = await getTeacherDoubts();
      setDoubts(data);
    } catch (error) {
      console.error('Failed to load doubts:', error);
      toast({
        title: "Error",
        description: "Failed to load student doubts",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const filteredDoubts = doubts.filter(doubt =>
    filter === 'all' ? true : doubt.status === filter
  );

  const pendingCount = doubts.filter(d => d.status === 'pending').length;
  const answeredCount = doubts.filter(d => d.status === 'answered').length;

  const handleAnswerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedDoubt || !answer.trim()) return;

    try {
      setIsSubmitting(true);
      await answerDoubt(selectedDoubt.id, answer);

      toast({
        title: "Answer Submitted",
        description: "Your answer has been sent to the student.",
      });

      setAnswer('');
      setSelectedDoubt(null);
      loadDoubts(); // Refresh list
    } catch (error) {
      console.error('Failed to submit answer:', error);
      toast({
        title: "Error",
        description: "Failed to submit answer",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="teacher" />

      <div className="container px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2 flex items-center gap-2">
            <MessageCircle className="h-8 w-8 text-primary" />
            Student Doubts
          </h1>
          <p className="text-muted-foreground">
            Answer student questions and help them learn better
          </p>
        </div>

        {/* Statistics */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Doubts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{doubts.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending Doubts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-500">{pendingCount}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Answered Doubts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-500">{answeredCount}</div>
            </CardContent>
          </Card>
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
          >
            All Doubts
          </Button>
          <Button
            variant={filter === 'pending' ? 'default' : 'outline'}
            onClick={() => setFilter('pending')}
          >
            Pending
          </Button>
          <Button
            variant={filter === 'answered' ? 'default' : 'outline'}
            onClick={() => setFilter('answered')}
          >
            Answered
          </Button>
        </div>

        {/* Doubts List */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-4">
            {isLoading ? (
              <div className="text-center py-12">
                <Loader2 className="h-8 w-8 mx-auto animate-spin text-muted-foreground" />
                <p className="text-muted-foreground mt-2">Loading doubts...</p>
              </div>
            ) : filteredDoubts.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No doubts found.</p>
                </CardContent>
              </Card>
            ) : (
              filteredDoubts.map((doubt) => (
                <Card
                  key={doubt.id}
                  className={`cursor-pointer transition-colors hover:border-primary ${selectedDoubt?.id === doubt.id ? 'border-primary' : ''
                    }`}
                  onClick={() => setSelectedDoubt(doubt)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-1">{doubt.subject || 'General'}</CardTitle>
                        <CardDescription>
                          {doubt.course_name} - Lecture {doubt.lecture_number}
                        </CardDescription>
                      </div>
                      <Badge variant={doubt.status === 'answered' ? 'default' : 'secondary'}>
                        {doubt.status === 'answered' ? (
                          <><CheckCircle className="mr-1 h-3 w-3" /> Answered</>
                        ) : (
                          <><Clock className="mr-1 h-3 w-3" /> Pending</>
                        )}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <User className="h-4 w-4" />
                      <span>{doubt.student_name}</span>
                    </div>

                    <div>
                      <p className="text-sm font-medium mb-1">Question:</p>
                      <p className="text-sm text-muted-foreground line-clamp-2">{doubt.question}</p>
                    </div>

                    <p className="text-xs text-muted-foreground">
                      Asked on {new Date(doubt.created_at).toLocaleString('en-IN')}
                    </p>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Answer Panel */}
          <div className="lg:sticky lg:top-4 h-fit">
            {selectedDoubt ? (
              <Card>
                <CardHeader>
                  <CardTitle>Doubt Details</CardTitle>
                  <CardDescription>
                    {selectedDoubt.status === 'answered' ? 'View answered doubt' : 'Provide your answer'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-medium mb-1">Student:</p>
                    <p className="text-sm text-muted-foreground">{selectedDoubt.student_name}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-1">Course:</p>
                    <p className="text-sm text-muted-foreground">
                      {selectedDoubt.course_name} - Lecture {selectedDoubt.lecture_number}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-1">Topic:</p>
                    <p className="text-sm text-muted-foreground">{selectedDoubt.subject || 'General'}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-1">Question:</p>
                    <p className="text-sm">{selectedDoubt.question}</p>
                  </div>

                  {selectedDoubt.status === 'answered' && selectedDoubt.answer ? (
                    <div className="pt-4 border-t">
                      <p className="text-sm font-medium mb-1 text-primary">Your Answer:</p>
                      <p className="text-sm">{selectedDoubt.answer}</p>
                    </div>
                  ) : (
                    <form onSubmit={handleAnswerSubmit} className="pt-4 border-t space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="answer">Your Answer</Label>
                        <Textarea
                          id="answer"
                          placeholder="Type your detailed answer here..."
                          value={answer}
                          onChange={(e) => setAnswer(e.target.value)}
                          required
                          rows={6}
                        />
                      </div>
                      <Button type="submit" className="w-full" disabled={isSubmitting}>
                        {isSubmitting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Submitting...
                          </>
                        ) : (
                          <>
                            <Send className="mr-2 h-4 w-4" />
                            Submit Answer
                          </>
                        )}
                      </Button>
                    </form>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select a doubt to view details and answer</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDoubts;
