import { useState } from 'react';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Gift, Star, Award, Zap } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Reward {
  id: string;
  title: string;
  description: string;
  cost: number;
  icon: any;
  available: boolean;
}

const StudentRewards = () => {
  const { toast } = useToast();
  // TODO: Fetch from backend
  // GET /api/students/:studentId/points
  const [totalPoints] = useState(850);

  // TODO: Fetch from backend
  // GET /api/rewards
  const rewards: Reward[] = [
    {
      id: '1',
      title: 'Premium Course Access',
      description: 'Unlock premium courses for 1 month',
      cost: 500,
      icon: Star,
      available: true
    },
    {
      id: '2',
      title: 'Certificate Boost',
      description: 'Get a premium certificate design',
      cost: 300,
      icon: Award,
      available: true
    },
    {
      id: '3',
      title: 'AI Tutor Sessions',
      description: '5 sessions with AI-powered tutor',
      cost: 400,
      icon: Zap,
      available: true
    },
    {
      id: '4',
      title: 'Course Discount',
      description: '50% off on any paid course',
      cost: 600,
      icon: Gift,
      available: true
    },
    {
      id: '5',
      title: 'Elite Badge',
      description: 'Show off your elite status',
      cost: 1000,
      icon: Trophy,
      available: false
    }
  ];

  const handleRedeem = (reward: Reward) => {
    // TODO: Redeem reward via backend
    // POST /api/rewards/:rewardId/redeem
    // Body: { studentId }
    
    if (totalPoints >= reward.cost) {
      toast({
        title: "Reward Redeemed!",
        description: `You've successfully redeemed ${reward.title}`,
      });
    } else {
      toast({
        title: "Insufficient Points",
        description: `You need ${reward.cost - totalPoints} more Kaushalya points`,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType="student" />
      <div className="container px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Rewards Store</h1>
          <p className="text-muted-foreground">Redeem your Kaushalya points for exciting rewards</p>
        </div>

        <Card className="mb-8 bg-gradient-primary">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-primary-foreground/80 text-sm">Your Balance</p>
                <h2 className="text-4xl font-bold text-primary-foreground">{totalPoints}</h2>
                <p className="text-primary-foreground/80">Kaushalya Points</p>
              </div>
              <Trophy className="h-16 w-16 text-primary-foreground/50" />
            </div>
            <Progress value={75} className="h-2 bg-primary-foreground/20" />
            <p className="text-xs text-primary-foreground/80 mt-2">150 points until next reward tier</p>
          </CardContent>
        </Card>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {rewards.map((reward) => {
            const Icon = reward.icon;
            const canAfford = totalPoints >= reward.cost;
            
            return (
              <Card key={reward.id} className={!reward.available ? 'opacity-50' : ''}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-lg bg-primary/10">
                      <Icon className="h-8 w-8 text-primary" />
                    </div>
                    <Badge variant={canAfford ? "default" : "secondary"}>
                      {reward.cost} points
                    </Badge>
                  </div>
                  <CardTitle className="mt-4">{reward.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">{reward.description}</p>
                  <Button
                    onClick={() => handleRedeem(reward)}
                    disabled={!reward.available || !canAfford}
                    className="w-full"
                  >
                    {!reward.available ? 'Coming Soon' : canAfford ? 'Redeem' : 'Not Enough Points'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default StudentRewards;
