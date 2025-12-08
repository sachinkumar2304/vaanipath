import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, CheckCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';
import { getCompetition, submitAnswer } from '../services/communityApi';
import api from '@/services/api'; 
import { Competition, Question } from '../types';

export default function CompetitionPlayPage() {
    const { competitionId } = useParams();
    const navigate = useNavigate();
    
    const [competition, setCompetition] = useState<Competition | null>(null);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [hasEnded, setHasEnded] = useState(false);

    // Fetch Competition & Questions
    useEffect(() => {
        const loadData = async () => {
            if (!competitionId) return;
            try {
                const comp = await getCompetition(competitionId);
                setCompetition(comp);

                if (comp.status !== 'active') {
                    toast.error("Competition is not active");
                    navigate(`/community/competition/${competitionId}`);
                    return;
                }

                // Fetch questions - this endpoint needs to be exposed for students
                // Assuming we use the generic questions endpoint but filtered?
                // Or maybe the competition object has it? No, usually separate.
                // We need a specific endpoint to get questions for student (without checking creator)
                // BUT current `add_questions` is mostly for creation. 
                // We need `GET /competitions/{id}/play` or similar.
                // Re-using existing check: we might need to add a "get questions for student" endpoint in backend.
                // If it's not there, I'll assume we can fetch it via `GET /competitions/{id}/questions` which I probably missed creating.
                // Checking backend `competitions.py`... I didn't see a GET questions endpoint!
                // Critical gap in plan/execution. I need to add GET questions endpoint.
                // For now, I will simulate it or try a specific route I might have missed.
                // Actually, let's create it in backend right after this file.
                
                const qResponse = await api.get(`/community/competitions/${competitionId}/questions`);
                setQuestions(qResponse.data);

            } catch (error) {
                console.error("Failed to load quiz", error);
                toast.error("Failed to load quiz");
            } finally {
                setIsLoading(false);
            }
        };
        loadData();
    }, [competitionId, navigate]);

    const handleAnswerSelect = (optionId: string) => {
        setSelectedAnswer(optionId);
    };

    const handleNext = async () => {
        if (!selectedAnswer || !competitionId) return;

        const currentQuestion = questions[currentQuestionIndex];
        setIsSubmitting(true);
        try {
            await submitAnswer(competitionId, {
                question_id: currentQuestion.id,
                selected_answer: selectedAnswer
            });

            if (currentQuestionIndex < questions.length - 1) {
                setCurrentQuestionIndex(prev => prev + 1);
                setSelectedAnswer(null);
            } else {
                toast.success("Quiz completed!");
                navigate(`/community/competition/${competitionId}`);
            }
        } catch (error) {
            console.error(error);
            toast.error("Failed to submit answer");
            // If failed because competition ended
            if (error.response?.data?.detail === "Competition has ended") {
                 setHasEnded(true);
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return (
             <div className="min-h-screen relative bg-background text-foreground flex items-center justify-center">
                 <PremiumBackground />
                 <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary border-b-2 border-purple-500"></div>
             </div>
        );
    }

    if (!competition || questions.length === 0) {
         return <div>Error loading quiz</div>;
    }

    const currentQuestion = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex) / questions.length) * 100;

    return (
        <div className="min-h-screen relative bg-background text-foreground flex flex-col">
            <PremiumBackground />
            
            {/* Header */}
            <div className="relative z-10 border-b border-border/40 bg-background/50 backdrop-blur-md p-4">
                <div className="container mx-auto max-w-4xl flex items-center justify-between">
                     <div className="flex items-center gap-4">
                        <Button variant="ghost" size="icon" onClick={() => navigate(`/community/competition/${competitionId}`)}>
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                        <div>
                            <h1 className="font-bold text-lg">{competition.title}</h1>
                            <p className="text-xs text-muted-foreground">Question {currentQuestionIndex + 1} of {questions.length}</p>
                        </div>
                     </div>
                     <div className="flex items-center gap-2 bg-primary/10 px-3 py-1.5 rounded-full text-primary font-mono text-sm">
                         <Clock className="h-4 w-4" />
                         <span>Active</span>
                     </div>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="relative z-10 h-1 bg-muted">
                <div className="h-full bg-primary transition-all duration-300" style={{ width: `${progress}%` }}></div>
            </div>

            {/* Main Question Area */}
            <main className="flex-1 relative z-10 flex items-center justify-center p-4">
                <div className="w-full max-w-2xl space-y-8">
                    
                    <div className="space-y-4">
                        <h2 className="text-2xl md:text-3xl font-bold leading-tight">
                            {currentQuestion.question_text}
                        </h2>
                    </div>

                    <div className="grid gap-4">
                        {currentQuestion.options.map((option: any) => (
                            <button
                                key={option.id}
                                onClick={() => handleAnswerSelect(option.id)}
                                className={`w-full p-4 rounded-xl border-2 text-left transition-all relative overflow-hidden group
                                    ${selectedAnswer === option.id 
                                        ? 'border-primary bg-primary/10' 
                                        : 'border-white/10 bg-card/40 hover:bg-card/60 hover:border-white/20'
                                    }
                                `}
                            >
                                <div className="flex items-center gap-4">
                                    <div className={`h-8 w-8 rounded-lg flex items-center justify-center font-bold text-sm border
                                         ${selectedAnswer === option.id 
                                            ? 'bg-primary text-primary-foreground border-primary' 
                                            : 'bg-muted border-white/10 text-muted-foreground'
                                        }
                                    `}>
                                        {option.id}
                                    </div>
                                    <span className="font-medium text-lg">{option.text}</span>
                                </div>
                                {selectedAnswer === option.id && (
                                    <CheckCircle className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-primary" />
                                )}
                            </button>
                        ))}
                    </div>

                    <div className="flex justify-end pt-8">
                        <Button 
                            size="lg" 
                            className="w-full md:w-auto min-w-[200px] text-lg h-12"
                            onClick={handleNext}
                            disabled={!selectedAnswer || isSubmitting}
                        >
                            {isSubmitting ? 'Submitting...' : 
                                (currentQuestionIndex === questions.length - 1 ? 'Finish Quiz' : 'Next Question')
                            }
                            {!isSubmitting && <ArrowRight className="ml-2 h-5 w-5" />}
                        </Button>
                    </div>

                </div>
            </main>
        </div>
    );
}
