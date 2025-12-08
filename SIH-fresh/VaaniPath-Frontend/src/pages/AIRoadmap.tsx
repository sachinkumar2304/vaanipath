import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Sparkles, CheckCircle2, BookOpen, Clock, Loader2, ArrowRight, Target, Brain, Languages as LangIcon, ExternalLink, ChevronRight } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import api from '@/services/api';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';

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
    setRoadmapData(null); // Reset to trigger animation on new data
    try {
      const response = await api.post('/ai/roadmap', {
        current_skills: currentSkills,
        goal: goal,
        language: language
      });

      setRoadmapData(response.data.output);
      toast.success("Roadmap generated successfully!");
      // Smooth scroll to roadmap
      setTimeout(() => {
        document.getElementById('roadmap-result')?.scrollIntoView({ behavior: 'smooth' });
      }, 500);
    } catch (error) {
      console.error("Error generating roadmap:", error);
      toast.error("Failed to generate roadmap. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 100 }
    }
  };

  return (
    <div className="min-h-screen bg-dots-pattern bg-fixed">
      {/* Background Gradients */}
      <div className="fixed inset-0 bg-gradient-to-br from-background via-background to-purple-950/20 -z-10" />
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[100px] animate-blob" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[100px] animate-blob animation-delay-2000" />
      </div>

      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />

      <main className="container px-4 py-12 max-w-5xl mx-auto">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-12 text-center relative"
        >
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 backdrop-blur-sm border border-purple-500/20 mb-6 shadow-xl shadow-purple-500/10">
            <Sparkles className="h-8 w-8 text-purple-400" />
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 tracking-tight">
            AI Learning Architect
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
            Design your personalized path to mastery. Powered by advanced AI to bridge the gap between where you are and where you want to go.
          </p>
        </motion.div>

        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <Card className="mb-16 border-purple-500/20 bg-card/40 backdrop-blur-xl shadow-2xl relative overflow-hidden group">
            {/* Glow effect on hover */}
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-transparent to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

            <CardContent className="p-8 space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <label className="text-sm font-semibold flex items-center gap-2 text-foreground/80">
                    <Brain className="h-4 w-4 text-purple-400" /> Current Skills
                  </label>
                  <div className="relative">
                    <Textarea
                      placeholder="e.g., Java, Basic Python, HTML/CSS..."
                      value={currentSkills}
                      onChange={(e) => setCurrentSkills(e.target.value)}
                      className="min-h-[120px] bg-background/50 border-white/10 focus:border-purple-500/50 focus:ring-purple-500/20 transition-all resize-none text-base"
                    />
                    <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                      {currentSkills.length} chars
                    </div>
                  </div>
                </div>
                <div className="space-y-6">
                  <div className="space-y-3">
                    <label className="text-sm font-semibold flex items-center gap-2 text-foreground/80">
                      <Target className="h-4 w-4 text-blue-400" /> Career Goal
                    </label>
                    <Input
                      placeholder="e.g., Senior Full Stack Developer, Data Scientist..."
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                      className="h-12 bg-background/50 border-white/10 focus:border-blue-500/50 focus:ring-blue-500/20 transition-all text-base"
                    />
                  </div>
                  <div className="space-y-3">
                    <label className="text-sm font-semibold flex items-center gap-2 text-foreground/80">
                      <LangIcon className="h-4 w-4 text-pink-400" /> Learning Language
                    </label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger className="h-12 bg-background/50 border-white/10 focus:border-pink-500/50 focus:ring-pink-500/20">
                        <SelectValue placeholder="Select Language" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="english">English</SelectItem>
                        <SelectItem value="hindi">Hindi (हिंदी)</SelectItem>
                        <SelectItem value="bhojpuri">Bhojpuri (भोजपुरी)</SelectItem>
                        <SelectItem value="marwadi">Marwadi (मारवाड़ी)</SelectItem>
                        <SelectItem value="tamil">Tamil (தமிழ்)</SelectItem>
                        <SelectItem value="telugu">Telugu (తెలుగు)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleGenerateRoadmap}
                disabled={loading || !currentSkills || !goal}
                className="w-full h-14 text-lg font-medium bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 shadow-lg shadow-purple-500/25 transition-all hover:scale-[1.01] hover:shadow-purple-500/40 rounded-xl"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Constructing Your Neural Path...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Generate Optimized Roadmap
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        <AnimatePresence>
          {roadmapData && (
            <motion.div
              id="roadmap-result"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-12"
            >
              {/* Header Summary */}
              <motion.div variants={itemVariants} className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 p-6 rounded-2xl bg-secondary/30 backdrop-blur-md border border-white/5">
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">{roadmapData.topic}</h2>
                  <p className="text-muted-foreground text-lg leading-relaxed max-w-2xl">{roadmapData.description}</p>
                </div>
                <Badge variant="outline" className="px-4 py-2 text-base h-auto border-purple-500/30 bg-purple-500/10 text-purple-300">
                  <Clock className="h-4 w-4 mr-2" />
                  {roadmapData.total_duration}
                </Badge>
              </motion.div>

              {/* Timeline Steps */}
              <div className="relative pl-8 md:pl-0">
                {/* Vertical Line */}
                <div className="absolute left-[39px] md:left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 via-blue-500 to-transparent opacity-30 md:-translate-x-1/2" />

                {roadmapData.steps.map((step, index) => (
                  <motion.div
                    key={index}
                    variants={itemVariants}
                    className={`relative mb-12 flex flex-col md:flex-row items-start ${index % 2 === 0 ? 'md:flex-row-reverse' : ''}`}
                  >
                    {/* Dot */}
                    <div className="absolute left-0 md:left-1/2 w-20 h-20 flex items-center justify-center md:-translate-x-1/2 z-10">
                      <div className="w-8 h-8 rounded-full bg-background border-4 border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.5)] flex items-center justify-center z-20">
                        <div className="w-2 h-2 rounded-full bg-white" />
                      </div>
                    </div>

                    {/* Content Card */}
                    <div className={`w-full md:w-[calc(50%-40px)] ml-10 md:ml-0 ${index % 2 === 0 ? 'md:pr-0' : 'md:pl-0'}`}>
                      <Card className="overflow-hidden border-white/5 bg-card/60 backdrop-blur-md hover:bg-card/80 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/5 group border-t-2 border-t-transparent hover:border-t-purple-500/50">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex flex-col">
                              <div className="flex items-center gap-3 mb-2">
                                <span className="text-5xl font-black text-white/5 opacity-50 absolute right-4 top-4 select-none">
                                  {String(index + 1).padStart(2, '0')}
                                </span>
                                <Badge variant="outline" className={`
                                                ${['Hard', 'Difficult', 'Complex', 'मुश्किल', 'मुस्किल', 'कठिन'].some(d => step.difficulty.includes(d)) ? 'border-red-500/30 text-red-400 bg-red-500/10' :
                                    ['Medium', 'Intermediate', 'Moderate', 'मझोला', 'माध्यम'].some(d => step.difficulty.includes(d)) ? 'border-yellow-500/30 text-yellow-400 bg-yellow-500/10' :
                                      'border-green-500/30 text-green-400 bg-green-500/10'}
                                            `}>
                                  {step.difficulty}
                                </Badge>
                              </div>
                              <CardTitle className="text-xl font-bold leading-tight z-10">{step.step}</CardTitle>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <p className="text-muted-foreground leading-relaxed">
                            {step.description}
                          </p>

                          {step.resources && step.resources.length > 0 && (
                            <div className="pt-4 border-t border-white/5">
                              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2 text-primary/80">
                                <BookOpen className="h-4 w-4" /> Recommended Resources
                              </h4>
                              <div className="grid gap-2">
                                {step.resources.map((resource, idx) => (
                                  <a
                                    key={idx}
                                    href={resource.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group/link flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary hover:text-primary transition-all duration-300 border border-transparent hover:border-primary/20"
                                  >
                                    <div className="flex items-center gap-3 overflow-hidden">
                                      <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary flex-shrink-0 group-hover/link:scale-110 transition-transform">
                                        <ChevronRight className="h-4 w-4" />
                                      </div>
                                      <span className="font-medium truncate text-sm">{resource.name}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-xs text-muted-foreground flex-shrink-0">
                                      <span>{resource.time_estimate}</span>
                                      <ExternalLink className="h-3 w-3 opacity-0 group-hover/link:opacity-100 transition-opacity" />
                                    </div>
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Tips Section */}
              {roadmapData.tips_and_tricks && (
                <motion.div variants={itemVariants}>
                  <Card className="bg-gradient-to-br from-yellow-500/5 via-orange-500/5 to-transparent border-yellow-500/20">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-3 text-2xl text-yellow-500/90">
                        <Sparkles className="h-6 w-6" />
                        Mastery Secrets
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {roadmapData.tips_and_tricks.map((tip, index) => (
                          <motion.div
                            key={index}
                            whileHover={{ scale: 1.02 }}
                            className="flex gap-4 p-4 rounded-xl bg-background/40 border border-white/5 hover:bg-white/5 hover:border-yellow-500/20 transition-colors"
                          >
                            <div className="mt-1">
                              <CheckCircle2 className="h-5 w-5 text-green-500" />
                            </div>
                            <div>
                              <h4 className="font-bold text-foreground mb-1">{tip.tip}</h4>
                              <p className="text-sm text-muted-foreground leading-relaxed">{tip.description}</p>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <style>{`
        .bg-dots-pattern {
            background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 40px 40px;
        }
        @keyframes blob {
            0% { transform: translate(0px, 0px) scale(1); }
            33% { transform: translate(30px, -50px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.9); }
            100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
            animation: blob 7s infinite;
        }
        .animation-delay-2000 {
            animation-delay: 2s;
        }
      `}</style>
    </div>
  );
};

export default AIRoadmap;
