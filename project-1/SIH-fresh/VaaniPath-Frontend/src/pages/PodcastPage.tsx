import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Mic, Languages, Play, Pause, Download, Loader2, Radio } from 'lucide-react';
import api from '@/services/api';

const PodcastPage = () => {
  const { isTeacher } = useAuth();
  const { toast } = useToast();
  const [text, setText] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  const handleGenerate = async () => {
    if (!text) {
      toast({
        title: "Error",
        description: "Please enter some text",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);

    try {
      const response = await api.post('/ai/generate-podcast', {
        text,
        language: selectedLanguage,
      });

      setAudioUrl(response.data.audio_url);
      toast({
        title: "Podcast Generated!",
        description: "Your podcast is ready to listen",
      });
    } catch (error: any) {
      toast({
        title: "Generation Failed",
        description: error.response?.data?.detail || "Failed to generate podcast",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const downloadPodcast = async () => {
    if (!audioUrl) return;

    try {
      // Fetch the audio file
      const response = await fetch(audioUrl);
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `podcast_${Date.now()}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Downloaded!",
        description: "Podcast saved successfully",
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Could not download the podcast",
        variant: "destructive",
      });
    }
  };

  // Audio Visualizer
  useEffect(() => {
    if (!audioRef.current || !canvasRef.current || !audioUrl) return;

    const audio = audioRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let audioContext: AudioContext;
    let analyser: AnalyserNode;
    let source: MediaElementAudioSourceNode;

    try {
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyser = audioContext.createAnalyser();
      source = audioContext.createMediaElementSource(audio);

      source.connect(analyser);
      analyser.connect(audioContext.destination);
      analyser.fftSize = 256;
    } catch (error) {
      console.error("Audio context error:", error);
      return;
    }

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!isPlaying) return;
      animationRef.current = requestAnimationFrame(draw);

      analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = 'rgb(15, 23, 42)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * canvas.height * 0.8;

        const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
        gradient.addColorStop(0, '#8b5cf6');
        gradient.addColorStop(0.5, '#ec4899');
        gradient.addColorStop(1, '#f97316');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

        x += barWidth + 1;
      }
    };

    if (isPlaying) {
      draw();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, audioUrl]);

  return (
    <div className="min-h-screen bg-background">
      <Header isAuthenticated userType={isTeacher ? "teacher" : "student"} />
      <div className="container px-4 py-8 max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mb-4">
            <Radio className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            AI Podcast Generator
          </h1>
          <p className="text-muted-foreground">Convert your text to engaging podcasts in your native language</p>
        </div>

        <Card className="mb-6 border-purple-200 dark:border-purple-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="h-5 w-5 text-purple-600" />
              Create Your Podcast
            </CardTitle>
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
                className="mt-2 resize-none"
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
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
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
          <Card className="border-purple-200 dark:border-purple-900 overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
              <CardTitle className="flex items-center gap-2">
                <Radio className="h-5 w-5 text-purple-600" />
                Your Podcast
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              {/* Audio Visualizer */}
              <div className="relative rounded-lg overflow-hidden bg-slate-900 shadow-2xl">
                <canvas
                  ref={canvasRef}
                  width={800}
                  height={200}
                  className="w-full h-[200px]"
                />

                {/* Play Button Overlay */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <Button
                    size="lg"
                    onClick={togglePlayback}
                    className="rounded-full w-20 h-20 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-2xl hover:scale-110 transition-transform"
                  >
                    {isPlaying ? (
                      <Pause className="h-8 w-8" />
                    ) : (
                      <Play className="h-8 w-8 ml-1" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Hidden Audio Element */}
              <audio
                ref={audioRef}
                src={audioUrl}
                crossOrigin="anonymous"
                onEnded={() => setIsPlaying(false)}
                onError={(e) => {
                  console.error("Audio error:", e);
                  toast({
                    title: "Playback Error",
                    description: "Could not play the audio",
                    variant: "destructive",
                  });
                }}
                className="hidden"
              />

              {/* Controls */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1 border-purple-200 hover:bg-purple-50 dark:border-purple-900 dark:hover:bg-purple-950/20"
                  onClick={downloadPodcast}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>

              {/* Info */}
              <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  <strong>Language:</strong> {selectedLanguage.charAt(0).toUpperCase() + selectedLanguage.slice(1)}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  <strong>Status:</strong> {isPlaying ? '🎙️ Playing' : '⏸️ Paused'}
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
