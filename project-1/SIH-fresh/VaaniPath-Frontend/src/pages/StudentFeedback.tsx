import { useState } from 'react';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useToast } from '@/hooks/use-toast';
import { MessageSquare, Star } from 'lucide-react';

const StudentFeedback = () => {
  const { toast } = useToast();
  const [rating, setRating] = useState('');
  const [feedback, setFeedback] = useState('');
  const [category, setCategory] = useState('');

  const handleSubmit = () => {
    // TODO: Submit feedback to backend
    // POST /api/feedback
    // Body: { studentId, rating, feedback, category }
    
    if (!rating || !feedback || !category) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Feedback Submitted!",
      description: "Thank you for helping us improve VANNIपथ",
    });

    setRating('');
    setFeedback('');
    setCategory('');
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="student" />
      <div className="container px-4 py-8 max-w-2xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
            <MessageSquare className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Share Your Feedback</h1>
          <p className="text-muted-foreground">Help us improve your learning experience</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>We Value Your Opinion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label className="mb-3 block">How would you rate your experience?</Label>
              <RadioGroup value={rating} onValueChange={setRating}>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <label
                      key={value}
                      className={`flex items-center justify-center w-12 h-12 rounded-lg border-2 cursor-pointer transition-colors ${
                        rating === value.toString()
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <RadioGroupItem value={value.toString()} className="sr-only" />
                      <Star
                        className={`h-6 w-6 ${
                          rating === value.toString() ? 'fill-primary text-primary' : 'text-muted-foreground'
                        }`}
                      />
                    </label>
                  ))}
                </div>
              </RadioGroup>
            </div>

            <div>
              <Label className="mb-3 block">What would you like to provide feedback on?</Label>
              <RadioGroup value={category} onValueChange={setCategory}>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted transition-colors">
                    <RadioGroupItem value="courses" id="courses" />
                    <Label htmlFor="courses" className="flex-1 cursor-pointer">Course Content</Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted transition-colors">
                    <RadioGroupItem value="platform" id="platform" />
                    <Label htmlFor="platform" className="flex-1 cursor-pointer">Platform Usability</Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted transition-colors">
                    <RadioGroupItem value="features" id="features" />
                    <Label htmlFor="features" className="flex-1 cursor-pointer">Features & Tools</Label>
                  </div>
                  <div className="flex items-center space-x-2 p-3 rounded-lg border hover:bg-muted transition-colors">
                    <RadioGroupItem value="other" id="other" />
                    <Label htmlFor="other" className="flex-1 cursor-pointer">Other</Label>
                  </div>
                </div>
              </RadioGroup>
            </div>

            <div>
              <Label htmlFor="feedback">Your Feedback</Label>
              <Textarea
                id="feedback"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Tell us what you think... (suggestions, issues, or compliments)"
                rows={6}
                className="mt-2"
              />
            </div>

            <Button onClick={handleSubmit} className="w-full">
              Submit Feedback
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StudentFeedback;
