import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Mic, Languages, Play, Pause, Download, Loader2 } from 'lucide-react';

const PodcastPage = () => {
  const { isTeacher } = useAuth();
  const { toast } = useToast();
  const [text, setText] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  const handleGenerate = async () => {
    // TODO: Generate podcast using backend AI engine
    // POST /api/ai/generate-podcast
    // Body: { text, language }

    if (!text) {
      toast({
        title: "Error",
        description: "Please enter some text",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);

    // Simulate API call
    setTimeout(() => {
      setAudioUrl('https://example.com/podcast.mp3');
      setIsGenerating(false);
      toast({
        title: "Podcast Generated!",
        description: "Your podcast is ready to listen",
      });
    }, 3000);
  };

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
    // TODO: Implement actual audio playback
  };

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
      <div className="container px-4 py-8 max-w-3xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
            <Mic className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">AI Podcast Generator</h1>
          <p className="text-muted-foreground">Convert your text to engaging podcasts in your native language</p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Create Your Podcast</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="text">Enter Your Content</Label>
              <Textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type or paste the text you want to convert into a podcast..."
                rows={8}
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-2">
                {text.length} characters
              </p>
            </div>

            <div>
              <Label>Select Language</Label>
              <div className="flex items-center gap-2 mt-2">
                <Languages className="h-5 w-5 text-muted-foreground" />
                <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="english">English</SelectItem>
                    <SelectItem value="hindi">हिंदी (Hindi)</SelectItem>
                    <SelectItem value="tamil">தமிழ் (Tamil)</SelectItem>
                    <SelectItem value="telugu">తెలుగు (Telugu)</SelectItem>
                    <SelectItem value="marathi">मराठी (Marathi)</SelectItem>
                    <SelectItem value="bengali">বাংলা (Bengali)</SelectItem>
                    <SelectItem value="kannada">ಕನ್ನಡ (Kannada)</SelectItem>
                    <SelectItem value="gujarati">ગુજરાતી (Gujarati)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !text}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Podcast...
                </>
              ) : (
                <>
                  <Mic className="h-4 w-4 mr-2" />
                  Generate Podcast
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {audioUrl && (
          <Card>
            <CardHeader>
              <CardTitle>Your Podcast</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-center gap-4 p-8 bg-gradient-secondary rounded-lg">
                <Button
                  size="lg"
                  variant="outline"
                  onClick={togglePlayback}
                  className="rounded-full w-16 h-16"
                >
                  {isPlaying ? (
                    <Pause className="h-6 w-6" />
                  ) : (
                    <Play className="h-6 w-6 ml-1" />
                  )}
                </Button>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
                <Button variant="outline" className="flex-1">
                  Share
                </Button>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">
                  <strong>Language:</strong> {selectedLanguage.charAt(0).toUpperCase() + selectedLanguage.slice(1)}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  <strong>Duration:</strong> ~{Math.ceil(text.length / 150)} minutes
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PodcastPage;
