import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Sparkles, CheckCircle2, BookOpen, Clock } from 'lucide-react';

interface RoadmapStep {
  id: string;
  title: string;
  description: string;
  duration: string;
  resources: string[];
  completed: boolean;
}

const AIRoadmap = () => {
  const { isTeacher } = useAuth();
  const [skill, setSkill] = useState('');
  const [showRoadmap, setShowRoadmap] = useState(false);

  // TODO: Generate roadmap using AI
  // POST /api/ai/generate-roadmap
  // Body: { skill, userId }
  const roadmap: RoadmapStep[] = [
    {
      id: '1',
      title: 'Learn Python Basics',
      description: 'Master Python fundamentals including variables, data types, loops, and functions',
      duration: '2-3 weeks',
      resources: ['Python.org Tutorial', 'Codecademy Python Course'],
      completed: false
    },
    {
      id: '2',
      title: 'Understand Data Structures',
      description: 'Learn about lists, dictionaries, sets, and tuples in Python',
      duration: '1-2 weeks',
      resources: ['Data Structures in Python', 'LeetCode Easy Problems'],
      completed: false
    },
    {
      id: '3',
      title: 'Learn Web Frameworks',
      description: 'Get started with Flask or Django for web development',
      duration: '3-4 weeks',
      resources: ['Flask Documentation', 'Django for Beginners'],
      completed: false
    },
    {
      id: '4',
      title: 'Build Projects',
      description: 'Create real-world projects to apply your knowledge',
      duration: '4-6 weeks',
      resources: ['GitHub Project Ideas', 'Portfolio Building Guide'],
      completed: false
    },
    {
      id: '5',
      title: 'Advanced Topics',
      description: 'Explore async programming, testing, and deployment',
      duration: '2-3 weeks',
      resources: ['Advanced Python Course', 'DevOps Basics'],
      completed: false
    }
  ];

  const handleGenerateRoadmap = () => {
    if (!skill) return;
    // TODO: Call AI backend to generate personalized roadmap
    setShowRoadmap(true);
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
          <CardContent className="p-6">
            <div className="flex gap-4">
              <Input
                placeholder="Enter the skill you want to learn (e.g., Python Development, Data Science)"
                value={skill}
                onChange={(e) => setSkill(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleGenerateRoadmap} disabled={!skill}>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Roadmap
              </Button>
            </div>
          </CardContent>
        </Card>

        {showRoadmap && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Your Learning Path: {skill}</h2>
              <Badge className="text-sm">Estimated: 12-18 weeks</Badge>
            </div>

            <div className="relative">
              {roadmap.map((step, index) => (
                <div key={step.id} className="relative pb-8">
                  {index < roadmap.length - 1 && (
                    <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-border" />
                  )}

                  <Card className="relative">
                    <CardHeader>
                      <div className="flex items-start gap-4">
                        <div className={`flex items-center justify-center w-8 h-8 rounded-full ${step.completed ? 'bg-success' : 'bg-primary'
                          } text-primary-foreground flex-shrink-0`}>
                          {step.completed ? (
                            <CheckCircle2 className="h-5 w-5" />
                          ) : (
                            <span className="text-sm font-bold">{index + 1}</span>
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <CardTitle className="text-xl">{step.title}</CardTitle>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <Clock className="h-4 w-4" />
                              {step.duration}
                            </div>
                          </div>
                          <p className="text-muted-foreground mb-4">{step.description}</p>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm font-medium">
                              <BookOpen className="h-4 w-4" />
                              Recommended Resources:
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {step.resources.map((resource, idx) => (
                                <Badge key={idx} variant="outline">{resource}</Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                  </Card>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIRoadmap;
