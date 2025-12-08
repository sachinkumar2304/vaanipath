import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Gift, Star, Award, Zap, History, ArrowRight } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Import API
// Import API
import { getGyanPoints, getGyanPointsHistory } from '@/features/community/services/communityApi';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Info, Sparkles, Mic, FileText, Lock } from 'lucide-react';

interface Reward {
  id: string;
  title: string;
  description: string;
  cost: number;
  icon: any;
  available: boolean;
  type?: 'podcast' | 'pdf' | 'other';
}

const StudentRewards = () => {
  const { toast } = useToast();
  const [totalPoints, setTotalPoints] = useState(0);
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
        try {
            const [pointsData, historyData] = await Promise.all([
                getGyanPoints(),
                getGyanPointsHistory()
            ]);
            setTotalPoints(pointsData.total_points);
            setHistory(historyData);
        } catch (error) {
            console.error("Failed to fetch rewards data", error);
        } finally {
            setIsLoading(false);
        }
    };
    fetchData();
  }, []);

  const rewards: Reward[] = [
    {
      id: 'pod-1',
      title: 'Podcast Creator Pack',
      description: 'Generate 5 premium AI podcasts from your notes.',
      cost: 200,
      icon: Mic,
      available: true,
      type: 'podcast'
    },
    {
      id: 'pdf-1',
      title: 'Text-to-PDF Unlock',
      description: 'Permanently unlock the advanced PDF export feature.',
      cost: 500,
      icon: FileText,
      available: true,
      type: 'pdf'
    },
    {
      id: '1',
      title: 'Premium Course Access',
      description: 'Unlock premium courses for 1 month',
      cost: 800,
      icon: Star,
      available: true,
      type: 'other'
    },
    {
      id: '2',
      title: 'Certificate Boost',
      description: 'Get a premium certificate design',
      cost: 300,
      icon: Award,
      available: true,
      type: 'other'
    },
    {
      id: '5',
      title: 'Elite Student Badge',
      description: 'Show off your elite status on your profile.',
      cost: 1000,
      icon: Trophy,
      available: false,
      type: 'other'
    }
  ];

  const handleRedeem = (reward: Reward) => {
    if (totalPoints >= reward.cost) {
      toast({
        title: "Reward Redeemed!",
        description: `You've successfully redeemed ${reward.title}. (Feature pending integration)`,
      });
    } else {
        const needed = reward.cost - totalPoints;
      toast({
        title: "Insufficient Points",
        description: `You need ${needed} more GyanPoints`,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="student" />
      <div className="container px-4 py-8 max-w-7xl mx-auto">
        
        {/* Hero Section */}
        <div className="mb-10 text-center space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                Rewards Store
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Turn your learning achievements into powerful tools. Earn GyanPoints and unlock premium features.
            </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column: Stats & History (4 cols) */}
            <div className="lg:col-span-4 space-y-6">
                {/* Balance Card */}
                <Card className="bg-gradient-to-br from-primary/90 to-purple-700 border-none shadow-xl text-white overflow-hidden relative">
                    {/* Background decorations */}
                    <div className="absolute top-0 right-0 p-8 opacity-10">
                        <Trophy className="w-32 h-32" />
                    </div>
                    
                    <CardContent className="p-8 relative z-10">
                        <div className="flex flex-col gap-1">
                            <span className="text-primary-foreground/80 font-medium">Available Balance</span>
                            <div className="flex items-baseline gap-2">
                                <span className="text-5xl font-bold tracking-tight">{totalPoints}</span>
                                <span className="text-lg opacity-80">GP</span>
                            </div>
                        </div>

                        <div className="mt-8 space-y-2">
                            <div className="flex justify-between text-sm opacity-90">
                                <span>Progress to Elite</span>
                                <span>{Math.min(100, (totalPoints/2000)*100).toFixed(0)}%</span>
                            </div>
                            <Progress value={(totalPoints / 2000) * 100} className="h-2 bg-black/20" indicatorClassName="bg-white" />
                            <p className="text-xs opacity-70 mt-1">Earn 2000 GP to unlock Elite status</p>
                        </div>
                    </CardContent>
                </Card>

                {/* How to Earn Accordion */}
                <Card className="border-primary/10 bg-card/50 backdrop-blur">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Info className="h-5 w-5 text-primary" /> How to Earn
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                         <Accordion type="single" collapsible className="w-full">
                            <AccordionItem value="item-1">
                                <AccordionTrigger>Startup Bonus</AccordionTrigger>
                                <AccordionContent className="text-muted-foreground">
                                    Get <span className="font-bold text-primary">100 GP</span> instantly when you sign up for VaaniPath.
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="item-2">
                                <AccordionTrigger>Course Quizzes</AccordionTrigger>
                                <AccordionContent className="text-muted-foreground">
                                    Score 60% or higher on video quizzes to earn <span className="font-bold text-primary">50 GP</span> per quiz.
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="item-3">
                                <AccordionTrigger>Contests</AccordionTrigger>
                                <AccordionContent className="text-muted-foreground">
                                    Win contests to earn big! <span className="font-bold text-primary">50-100 GP</span> for 1st place.
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="item-4">
                                <AccordionTrigger>Winning Streaks</AccordionTrigger>
                                <AccordionContent className="text-muted-foreground">
                                    Win consecutive contests in a community to unlock <span className="font-bold text-orange-500">Streak Bonuses</span> (Starting at 20 GP).
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>
                    </CardContent>
                </Card>

                {/* History */}
                <Card className="border-border/50">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                            <History className="h-5 w-5" /> History
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                         <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                            {history.length === 0 ? (
                                <p className="text-sm text-muted-foreground text-center py-4">No points history yet.</p>
                            ) : (
                                history.map((txn) => (
                                    <div key={txn.id} className="flex items-center justify-between border-b border-border/40 last:border-0 pb-3 last:pb-0">
                                        <div className="space-y-0.5">
                                            <p className="font-medium text-sm line-clamp-1" title={txn.description}>{txn.description}</p>
                                            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{txn.transaction_type.replace('_', ' ')}</p>
                                        </div>
                                        <span className={`text-sm font-bold whitespace-nowrap ${txn.points_change > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600'}`}>
                                            {txn.points_change > 0 ? '+' : ''}{txn.points_change}
                                        </span>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Right Column: Marketplace (8 cols) */}
            <div className="lg:col-span-8">
                 <Tabs defaultValue="all" className="w-full">
                    <div className="flex items-center justify-between mb-6">
                        <TabsList>
                            <TabsTrigger value="all">All Rewards</TabsTrigger>
                            <TabsTrigger value="tools">Tools & Features</TabsTrigger>
                            <TabsTrigger value="perks">Perks</TabsTrigger>
                        </TabsList>
                    </div>
                    
                    <TabsContent value="all" className="mt-0 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {rewards.map(reward => <RewardCard key={reward.id} reward={reward} userPoints={totalPoints} onRedeem={handleRedeem} />)}
                        </div>
                    </TabsContent>
                    
                    <TabsContent value="tools" className="mt-0">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                             {rewards.filter(r => ['podcast', 'pdf'].includes(r.type || '')).map(reward => 
                                <RewardCard key={reward.id} reward={reward} userPoints={totalPoints} onRedeem={handleRedeem} />
                             )}
                        </div>
                    </TabsContent>

                    <TabsContent value="perks" className="mt-0">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                             {rewards.filter(r => r.type === 'other').map(reward => 
                                <RewardCard key={reward.id} reward={reward} userPoints={totalPoints} onRedeem={handleRedeem} />
                             )}
                        </div>
                    </TabsContent>
                </Tabs>

                {/* Info Alert */}
                <div className="mt-8 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20 flex gap-4 items-start">
                    <Sparkles className="h-6 w-6 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div>
                        <h4 className="font-semibold text-blue-500 mb-1">Coming Soon: Real-world Vouchers</h4>
                        <p className="text-sm text-muted-foreground">
                            We are partnering with educational platforms to let you redeem GyanPoints for real-world discounts and certification vouchers. Stay tuned!
                        </p>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

// Helper Component for Reward Card
const RewardCard = ({ reward, userPoints, onRedeem }: { reward: Reward, userPoints: number, onRedeem: (r: Reward) => void }) => {
    const Icon = reward.icon;
    const canAfford = userPoints >= reward.cost;

    return (
        <Card className={`group relative overflow-hidden transition-all hover:shadow-lg hover:border-primary/50 ${!reward.available ? 'opacity-70' : ''}`}>
             {!reward.available && (
                <div className="absolute inset-0 bg-background/60 backdrop-blur-[1px] z-10 flex items-center justify-center">
                    <div className="bg-background/80 px-3 py-1 rounded-full border shadow-sm flex items-center gap-2">
                        <Lock className="w-3 h-3 text-muted-foreground" />
                        <span className="text-xs font-medium text-muted-foreground">Coming Soon</span>
                    </div>
                </div>
            )}
            
            <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                    <div className={`p-3 rounded-xl ${canAfford ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'}`}>
                        <Icon className="h-6 w-6" />
                    </div>
                    <Badge variant={canAfford ? "default" : "secondary"} className="font-mono">
                        {reward.cost} GP
                    </Badge>
                </div>
                
                <h3 className="font-bold text-lg mb-2 group-hover:text-primary transition-colors">{reward.title}</h3>
                <p className="text-sm text-muted-foreground mb-6 min-h-[40px]">{reward.description}</p>
                
                <Button 
                    className="w-full" 
                    variant={canAfford ? "default" : "outline"}
                    disabled={!reward.available || !canAfford}
                    onClick={() => onRedeem(reward)}
                >
                    {canAfford ? "Redeem Now" : "Earn More Points"}
                </Button>
            </CardContent>
        </Card>
    )
}

export default StudentRewards;
