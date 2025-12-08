import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Trash2, Save, ArrowLeft, GripVertical } from 'lucide-react';
import { toast } from 'sonner';
import { createCompetition, addQuestions } from '../services/communityApi';
import { QuestionCreate } from '../types';

export default function CompetitionCreatePage() {
    const { communityId } = useParams();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);

    // Competition State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [startTime, setStartTime] = useState('');
    const [endTime, setEndTime] = useState('');
    const [difficulty, setDifficulty] = useState<'normal' | 'hard'>('normal');
    const [points, setPoints] = useState(50); // Default for normal

    // Update points when difficulty changes
    const handleDifficultyChange = (val: 'normal' | 'hard') => {
        setDifficulty(val);
        setPoints(val === 'hard' ? 100 : 50);
    };

    // Questions State
    const [questions, setQuestions] = useState<any[]>([
        {
            id: '1',
            text: '',
            options: [
                { id: 'A', text: '' },
                { id: 'B', text: '' },
                { id: 'C', text: '' },
                { id: 'D', text: '' }
            ],
            correctAnswer: 'A',
            points: 10
        }
    ]);

    const handleAddQuestion = () => {
        setQuestions([
            ...questions,
            {
                id: Date.now().toString(),
                text: '',
                options: [
                    { id: 'A', text: '' },
                    { id: 'B', text: '' },
                    { id: 'C', text: '' },
                    { id: 'D', text: '' }
                ],
                correctAnswer: 'A',
                points: 10
            }
        ]);
    };

    const handleRemoveQuestion = (index: number) => {
        if (questions.length === 1) {
            toast.error("At least one question is required");
            return;
        }
        const newQuestions = [...questions];
        newQuestions.splice(index, 1);
        setQuestions(newQuestions);
    };

    const handleQuestionChange = (index: number, field: string, value: any) => {
        const newQuestions = [...questions];
        if (field === 'text') newQuestions[index].text = value;
        if (field === 'correctAnswer') newQuestions[index].correctAnswer = value;
        if (field === 'points') newQuestions[index].points = parseInt(value);
        setQuestions(newQuestions);
    };

    const handleOptionChange = (qIndex: number, oIndex: number, value: string) => {
        const newQuestions = [...questions];
        newQuestions[qIndex].options[oIndex].text = value;
        setQuestions(newQuestions);
    };

    const handleSubmit = async () => {
        if (!communityId) return;
        if (!title || !startTime || !endTime) {
            toast.error("Please fill in all required fields");
            return;
        }

        // Validate Questions
        for (const q of questions) {
            if (!q.text) {
                toast.error("All questions must have text");
                return;
            }
            for (const opt of q.options) {
                if (!opt.text) {
                    toast.error("All options must be filled");
                    return;
                }
            }
        }

        setIsLoading(true);
        try {
            // 1. Create Competition
            const compData = {
                community_id: communityId,
                title,
                description,
                start_time: new Date(startTime).toISOString(),
                end_time: new Date(endTime).toISOString(),
                difficulty,
                points_first: points,
                points_second: Math.round(points * 0.75),
                points_third: Math.round(points * 0.5),
                points_top10: Math.round(points * 0.25)
            };

            const competition = await createCompetition(compData);

            // 2. Add Questions
            const questionsData: QuestionCreate[] = questions.map((q, idx) => ({
                competition_id: competition.id,
                question_text: q.text,
                options: q.options,
                correct_answer: q.correctAnswer,
                points: q.points,
                question_order: idx + 1
            }));

            await addQuestions(competition.id, questionsData);

            toast.success("Competition created successfully!");
            navigate(`/community/${communityId}`);
        } catch (error) {
            console.error(error);
            toast.error("Failed to create competition");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen relative bg-background text-foreground">
            <PremiumBackground />
            <Header isAuthenticated userType="teacher" /> 
            
            <main className="container px-4 py-8 relative z-10 max-w-4xl mx-auto">
                <Button variant="ghost" className="mb-6 pl-0 hover:bg-transparent hover:text-primary" onClick={() => navigate(-1)}>
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back
                </Button>

                <div className="space-y-8">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent mb-2">
                            Create Competition
                        </h1>
                        <p className="text-muted-foreground">Setup a new contest for your community members.</p>
                    </div>

                    <Card className="bg-card/40 backdrop-blur border-white/10">
                        <CardHeader>
                            <CardTitle>Basic Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Title</Label>
                                <Input placeholder="Weekly Quiz Challenge" value={title} onChange={(e) => setTitle(e.target.value)} />
                            </div>
                            <div className="space-y-2">
                                <Label>Description</Label>
                                <Textarea placeholder="Test your knowledge..." value={description} onChange={(e) => setDescription(e.target.value)} />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Start Time</Label>
                                    <Input type="datetime-local" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label>End Time</Label>
                                    <Input type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
                                </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Difficulty Mode</Label>
                                    <Select value={difficulty} onValueChange={(val: 'normal' | 'hard') => handleDifficultyChange(val)}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="normal">Normal (Instant Score, 50 pts)</SelectItem>
                                            <SelectItem value="hard">Hard (Score Hidden, 100 pts)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <p className="text-xs text-muted-foreground">
                                        {difficulty === 'normal' 
                                            ? "Participants see their score immediately." 
                                            : "Participants only see their score after the contest ends."
                                        }
                                    </p>
                                </div>
                                <div className="space-y-2">
                                    <Label>Winning Points (1st Place)</Label>
                                    <Input type="number" value={points} onChange={(e) => setPoints(parseInt(e.target.value))} />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-bold">Questions ({questions.length})</h2>
                            <Button onClick={handleAddQuestion} variant="outline" size="sm">
                                <Plus className="mr-2 h-4 w-4" /> Add Question
                            </Button>
                        </div>

                        {questions.map((q, index) => (
                            <Card key={q.id} className="bg-card/40 backdrop-blur border-white/10 relative group">
                                <CardContent className="p-6 space-y-4">
                                    <div className="absolute right-4 top-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive hover:bg-destructive/10" onClick={() => handleRemoveQuestion(index)}>
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>

                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="bg-primary/10 text-primary px-2 py-1 rounded text-xs font-bold">Q{index + 1}</span>
                                        <GripVertical className="h-4 w-4 text-muted-foreground cursor-move" />
                                    </div>

                                    <div className="space-y-2">
                                        <Input 
                                            placeholder="Question Text" 
                                            value={q.text} 
                                            onChange={(e) => handleQuestionChange(index, 'text', e.target.value)} 
                                            className="font-medium"
                                        />
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {q.options.map((opt: any, oIndex: number) => (
                                            <div key={opt.id} className="flex items-center gap-2">
                                                <span className="font-mono text-muted-foreground text-sm w-4">{opt.id}.</span>
                                                <Input 
                                                    placeholder={`Option ${opt.id}`} 
                                                    value={opt.text}
                                                    onChange={(e) => handleOptionChange(index, oIndex, e.target.value)} 
                                                />
                                            </div>
                                        ))}
                                    </div>

                                    <div className="flex flex-col md:flex-row gap-4 pt-4 border-t border-white/5">
                                        <div className="flex-1 space-y-2">
                                            <Label>Correct Answer</Label>
                                            <Select value={q.correctAnswer} onValueChange={(val) => handleQuestionChange(index, 'correctAnswer', val)}>
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {q.options.map((opt: any) => (
                                                        <SelectItem key={opt.id} value={opt.id}>Option {opt.id}</SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div className="w-32 space-y-2">
                                            <Label>Points</Label>
                                            <Input type="number" value={q.points} onChange={(e) => handleQuestionChange(index, 'points', e.target.value)} />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>

                    <div className="flex justify-end gap-4 pt-4">
                        <Button variant="ghost" onClick={() => navigate(-1)}>Cancel</Button>
                        <Button size="lg" onClick={handleSubmit} disabled={isLoading} className="bg-gradient-to-r from-primary to-purple-600">
                            {isLoading ? 'Creating...' : (
                                <>
                                    <Save className="mr-2 h-4 w-4" /> Save Competition
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            </main>
        </div>
    );
}
