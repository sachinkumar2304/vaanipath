import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Sparkles, CheckCircle2, BookOpen, Clock, Loader2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import api from '@/services/api';
import { toast } from 'sonner';

interface RoadmapResource {
  name: string;
  link: string;
  time_estimate: string;
}

interface RoadmapStep {
  step: string;
  description: string;
  difficulty: string;
  resources: RoadmapResource[];
}

interface RoadmapResponse {
  output: {
    language: string;
    topic: string;
    description: string;
    total_duration: string;
    steps: RoadmapStep[];
    tips_and_tricks: { tip: string; description: string }[];
  }
}

const AIRoadmap = () => {
  const { isTeacher } = useAuth();
  const [currentSkills, setCurrentSkills] = useState('');
  const [goal, setGoal] = useState('');
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);
  const [roadmapData, setRoadmapData] = useState<RoadmapResponse['output'] | null>(null);

  const handleGenerateRoadmap = async () => {
    if (!currentSkills || !goal) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/ai/roadmap', {
        current_skills: currentSkills,
        goal: goal,
        language: language
      });

      setRoadmapData(response.data.output);
      toast.success("Roadmap generated successfully!");
    } catch (error) {
      console.error("Error generating roadmap:", error);
      toast.error("Failed to generate roadmap. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
      <div className="container px-4 py-8 max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
            <Sparkles className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">AI Learning Roadmap</h1>
          <p className="text-muted-foreground">Get a personalized learning path to achieve your goals</p>
        </div>

        <Card className="mb-8">
          <CardContent className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Current Skills</label>
                <Textarea
                  placeholder="e.g., Java, Python, Basic HTML"
                  value={currentSkills}
                  onChange={(e) => setCurrentSkills(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Career Goal</label>
                <Input
                  placeholder="e.g., SDE, Data Scientist"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Preferred Language</label>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="hindi">Hindi</SelectItem>
                  <SelectItem value="bhojpuri">Bhojpuri</SelectItem>
                  <SelectItem value="marwadi">Marwadi</SelectItem>
                  <SelectItem value="tamil">Tamil</SelectItem>
                  <SelectItem value="telugu">Telugu</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleGenerateRoadmap}
              disabled={loading || !currentSkills || !goal}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Your Path...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Roadmap
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {roadmapData && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold">{roadmapData.topic}</h2>
                <p className="text-muted-foreground mt-1">{roadmapData.description}</p>
              </div>
              <Badge className="text-sm h-fit whitespace-nowrap">
                Duration: {roadmapData.total_duration}
              </Badge>
            </div>

            <div className="relative">
              {roadmapData.steps.map((step, index) => (
                <div key={index} className="relative pb-8">
                  {index < roadmapData.steps.length - 1 && (
                    <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-border" />
                  )}

                  <Card className="relative">
                    <CardHeader>
                      <div className="flex items-start gap-4">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground flex-shrink-0">
                          <span className="text-sm font-bold">{index + 1}</span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <CardTitle className="text-xl">{step.step}</CardTitle>
                            <Badge variant={step.difficulty === 'Hard' || step.difficulty === 'मुश्किल' ? 'destructive' : 'secondary'}>
                              {step.difficulty}
                            </Badge>
                          </div>
                          <p className="text-muted-foreground mb-4">{step.description}</p>

                          {step.resources && step.resources.length > 0 && (
                            <div className="space-y-2">
                              <div className="flex items-center gap-2 text-sm font-medium">
                                <BookOpen className="h-4 w-4" />
                                Recommended Resources:
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {step.resources.map((resource, idx) => (
                                  <a
                                    key={idx}
                                    href={resource.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center justify-between p-2 rounded-md border hover:bg-accent transition-colors text-sm"
                                  >
                                    <span className="font-medium truncate mr-2">{resource.name}</span>
                                    <span className="text-xs text-muted-foreground whitespace-nowrap">{resource.time_estimate}</span>
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                  </Card>
                </div>
              ))}
            </div>

            {roadmapData.tips_and_tricks && (
              <Card className="bg-muted/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-yellow-500" />
                    Tips for Success
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {roadmapData.tips_and_tricks.map((tip, index) => (
                      <div key={index} className="flex gap-3">
                        <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0" />
                        <div>
                          <h4 className="font-semibold">{tip.tip}</h4>
                          <p className="text-sm text-muted-foreground">{tip.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIRoadmap;
