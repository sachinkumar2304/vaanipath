import { useState, useRef, useEffect, useCallback } from 'react';
import {
  Play, Pause, Volume2, VolumeX, Maximize, Minimize,
  Settings, Subtitles, PictureInPicture, Bookmark,
  SkipForward, SkipBack, Maximize2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { VideoTranscript } from '@/components/VideoTranscript';
import { VideoPlayerProps, ChapterMarker } from '@/types/video';
import { motion, AnimatePresence } from 'framer-motion';

export const VideoPlayer = ({
  videoUrl,
  posterUrl,
  title,
  chapters = [],
  transcript = [],
  captions = [],
  audioTracks = [],
  analytics,
  className = '',
  autoPlay = false,
  startTime = 0,
}: VideoPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const controlsTimeoutRef = useRef<NodeJS.Timeout>();

  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(startTime);
  const [duration, setDuration] = useState(0);
  const [buffered, setBuffered] = useState(0);

  // UI state
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isPiP, setIsPiP] = useState(false);
  const [showMiniPlayer, setShowMiniPlayer] = useState(false);

  // Caption/Audio state
  const [selectedCaption, setSelectedCaption] = useState<string>('off');
  const [selectedAudio, setSelectedAudio] = useState<string>(audioTracks[0]?.language || 'default');

  // Chapter state
  const [currentChapter, setCurrentChapter] = useState<ChapterMarker | null>(null);
  const [hoveredChapter, setHoveredChapter] = useState<ChapterMarker | null>(null);

  // Format time helper
  const formatTime = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  // Playback controls
  const togglePlay = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
      analytics?.onPause?.(currentTime);
    } else {
      video.play();
      analytics?.onPlay?.(currentTime);
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying, currentTime, analytics]);

  const handleSeek = useCallback((value: number[]) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = value[0];
    const oldTime = currentTime;
    video.currentTime = newTime;
    setCurrentTime(newTime);
    analytics?.onSeek?.(oldTime, newTime);
  }, [currentTime, analytics]);

  const skip = useCallback((seconds: number) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
    video.currentTime = newTime;
    setCurrentTime(newTime);
  }, [currentTime, duration]);

  const handleVolumeChange = useCallback((value: number[]) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = value[0];
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
    analytics?.onVolumeChange?.(newVolume);
  }, [analytics]);

  const toggleMute = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !isMuted;
    setIsMuted(!isMuted);
  }, [isMuted]);

  const changePlaybackRate = useCallback((rate: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.playbackRate = rate;
    setPlaybackRate(rate);
    analytics?.onSpeedChange?.(rate);
  }, [analytics]);

  const toggleFullscreen = useCallback(async () => {
    const container = containerRef.current;
    if (!container) return;

    try {
      if (!document.fullscreenElement) {
        await container.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (error) {
      console.error('Fullscreen error:', error);
    }
  }, []);

  const togglePiP = useCallback(async () => {
    const video = videoRef.current;
    if (!video) return;

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
        setIsPiP(false);
      } else {
        await video.requestPictureInPicture();
        setIsPiP(true);
      }
    } catch (error) {
      console.error('PiP error:', error);
    }
  }, []);

  const handleBookmark = useCallback(() => {
    analytics?.onBookmark?.(currentTime);
  }, [currentTime, analytics]);

  const jumpToTimestamp = useCallback((time: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = time;
    setCurrentTime(time);
    analytics?.onTranscriptClick?.(time);
  }, [analytics]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ignore if typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case ' ':
        case 'k':
          e.preventDefault();
          togglePlay();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          skip(-5);
          break;
        case 'ArrowRight':
          e.preventDefault();
          skip(5);
          break;
        case 'j':
          e.preventDefault();
          skip(-10);
          break;
        case 'l':
          e.preventDefault();
          skip(10);
          break;
        case 'ArrowUp':
          e.preventDefault();
          handleVolumeChange([Math.min(1, volume + 0.1)]);
          break;
        case 'ArrowDown':
          e.preventDefault();
          handleVolumeChange([Math.max(0, volume - 0.1)]);
          break;
        case 'm':
          e.preventDefault();
          toggleMute();
          break;
        case 'f':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 'p':
          e.preventDefault();
          togglePiP();
          break;
        case '+':
        case '=':
          e.preventDefault();
          changePlaybackRate(Math.min(2, playbackRate + 0.25));
          break;
        case '-':
          e.preventDefault();
          changePlaybackRate(Math.max(0.5, playbackRate - 0.25));
          break;
        case 'b':
          e.preventDefault();
          handleBookmark();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [togglePlay, skip, handleVolumeChange, volume, toggleMute, toggleFullscreen, togglePiP, changePlaybackRate, playbackRate, handleBookmark]);

  // Video event listeners
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);

      // Update current chapter
      const chapter = chapters.find(
        c => video.currentTime >= c.time &&
          (chapters[chapters.indexOf(c) + 1]?.time ?? Infinity) > video.currentTime
      );
      if (chapter && chapter !== currentChapter) {
        setCurrentChapter(chapter);
        analytics?.onChapterChange?.(chapter);
      }
    };

    const handleDurationChange = () => setDuration(video.duration);
    const handleProgress = () => {
      if (video.buffered.length > 0) {
        setBuffered(video.buffered.end(video.buffered.length - 1));
      }
    };
    const handleEnded = () => {
      setIsPlaying(false);
      analytics?.onComplete?.();
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('progress', handleProgress);
    video.addEventListener('ended', handleEnded);

    // Set start time
    if (startTime > 0) {
      video.currentTime = startTime;
    }

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('progress', handleProgress);
      video.removeEventListener('ended', handleEnded);
    };
  }, [startTime, chapters, currentChapter, analytics]);

  // Auto-hide controls
  const resetControlsTimeout = useCallback(() => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    if (isPlaying) {
      controlsTimeoutRef.current = setTimeout(() => {
        setShowControls(false);
      }, 3000);
    }
  }, [isPlaying]);

  useEffect(() => {
    return () => {
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current);
      }
    };
  }, []);

  // Handle subtitle track switching
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // Wait for tracks to load
    const updateTracks = () => {
      Array.from(video.textTracks).forEach((track) => {
        if (selectedCaption === 'off') {
          track.mode = 'hidden';
        } else {
          // Match by language
          track.mode = track.language === selectedCaption ? 'showing' : 'hidden';
        }
      });
    };

    updateTracks();

    // Also listen for track changes (in case they load late)
    video.addEventListener('loadedmetadata', updateTracks);
    return () => video.removeEventListener('loadedmetadata', updateTracks);
  }, [selectedCaption]);

  // Sticky mini-player on scroll
  useEffect(() => {
    const handleScroll = () => {
      const container = containerRef.current;
      if (!container) return;

      const rect = container.getBoundingClientRect();
      const shouldShowMini = rect.bottom < 0 && isPlaying;
      setShowMiniPlayer(shouldShowMini);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isPlaying]);

  const playbackRates = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];

  return (
    <>
      {/* Main Video Player */}
      <div
        ref={containerRef}
        className={`relative glass-card rounded-2xl overflow-hidden shadow-2xl ${className}`}
        onMouseMove={resetControlsTimeout}
        onMouseLeave={() => isPlaying && setShowControls(false)}
      >
        {/* Video Element */}
        <video
          ref={videoRef}
          className="w-full aspect-video bg-black"
          poster={posterUrl}
          preload="metadata"
          playsInline
          onClick={togglePlay}
        >
          <source src={videoUrl} type="video/mp4" />
          {captions.map((caption) => (
            <track
              key={caption.language}
              kind="subtitles"
              src={caption.src}
              srcLang={caption.language}
              label={caption.label}
              default={caption.default}
            />
          ))}
          Your browser does not support the video tag.
        </video>

        {/* Controls Overlay */}
        <AnimatePresence>
          {showControls && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none"
            >
              {/* Top Bar - Title */}
              <div className="absolute top-0 left-0 right-0 p-6 bg-gradient-to-b from-black/60 to-transparent pointer-events-auto">
                {title && (
                  <h2 className="text-white text-xl font-bold drop-shadow-lg">{title}</h2>
                )}
              </div>

              {/* Center - Play Button */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-auto">
                <Button
                  variant="ghost"
                  size="lg"
                  onClick={togglePlay}
                  className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-md hover:bg-white/30 transition-all"
                  aria-label={isPlaying ? 'Pause' : 'Play'}
                >
                  {isPlaying ? (
                    <Pause className="h-10 w-10 text-white" />
                  ) : (
                    <Play className="h-10 w-10 text-white ml-1" />
                  )}
                </Button>
              </div>

              {/* Bottom Controls */}
              <div className="absolute bottom-0 left-0 right-0 p-4 pointer-events-auto">
                {/* Progress Bar with Chapter Markers */}
                <div className="mb-4 relative group">
                  <Slider
                    value={[currentTime]}
                    max={duration || 100}
                    step={0.1}
                    onValueChange={handleSeek}
                    className="cursor-pointer"
                    aria-label="Video progress"
                  />

                  {/* Buffered Progress */}
                  <div
                    className="absolute top-1/2 -translate-y-1/2 h-1 bg-white/30 rounded-full pointer-events-none"
                    style={{ width: `${(buffered / duration) * 100}%` }}
                  />

                  {/* Chapter Markers */}
                  {chapters.map((chapter, index) => (
                    <div
                      key={index}
                      className="absolute top-1/2 -translate-y-1/2 w-2 h-2 bg-primary rounded-full cursor-pointer hover:scale-150 transition-transform"
                      style={{ left: `${(chapter.time / duration) * 100}%` }}
                      onClick={() => jumpToTimestamp(chapter.time)}
                      onMouseEnter={() => setHoveredChapter(chapter)}
                      onMouseLeave={() => setHoveredChapter(null)}
                      role="button"
                      tabIndex={0}
                      aria-label={`Jump to ${chapter.title}`}
                    />
                  ))}

                  {/* Chapter Tooltip */}
                  {hoveredChapter && (
                    <div
                      className="absolute bottom-full mb-2 px-3 py-2 bg-black/90 text-white text-sm rounded-lg whitespace-nowrap"
                      style={{ left: `${(hoveredChapter.time / duration) * 100}%`, transform: 'translateX(-50%)' }}
                    >
                      {hoveredChapter.title}
                    </div>
                  )}
                </div>

                {/* Control Buttons */}
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {/* Play/Pause */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={togglePlay}
                      className="text-white hover:bg-white/20"
                      aria-label={isPlaying ? 'Pause' : 'Play'}
                    >
                      {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
                    </Button>

                    {/* Skip Backward */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => skip(-10)}
                      className="text-white hover:bg-white/20"
                      aria-label="Skip backward 10 seconds"
                    >
                      <SkipBack className="h-5 w-5" />
                    </Button>

                    {/* Skip Forward */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => skip(10)}
                      className="text-white hover:bg-white/20"
                      aria-label="Skip forward 10 seconds"
                    >
                      <SkipForward className="h-5 w-5" />
                    </Button>

                    {/* Volume */}
                    <div className="flex items-center gap-2 group/volume">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={toggleMute}
                        className="text-white hover:bg-white/20"
                        aria-label={isMuted ? 'Unmute' : 'Mute'}
                      >
                        {isMuted || volume === 0 ? (
                          <VolumeX className="h-5 w-5" />
                        ) : (
                          <Volume2 className="h-5 w-5" />
                        )}
                      </Button>
                      <div className="w-0 group-hover/volume:w-24 transition-all overflow-hidden">
                        <Slider
                          value={[isMuted ? 0 : volume]}
                          max={1}
                          step={0.01}
                          onValueChange={handleVolumeChange}
                          className="w-24"
                          aria-label="Volume"
                        />
                      </div>
                    </div>

                    {/* Time Display */}
                    <span className="text-white text-sm font-mono">
                      {formatTime(currentTime)} / {formatTime(duration)}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Bookmark */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleBookmark}
                      className="text-white hover:bg-white/20"
                      aria-label="Bookmark current time"
                      title="Bookmark (B)"
                    >
                      <Bookmark className="h-5 w-5" />
                    </Button>

                    {/* Captions */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-white hover:bg-white/20"
                          aria-label="Captions"
                        >
                          <Subtitles className="h-5 w-5" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuLabel>Subtitles</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => setSelectedCaption('off')}>
                          Off
                        </DropdownMenuItem>
                        {captions.map((caption) => (
                          <DropdownMenuItem
                            key={caption.language}
                            onClick={() => setSelectedCaption(caption.language)}
                          >
                            {caption.label}
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>

                    {/* Settings (Speed) */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-white hover:bg-white/20"
                          aria-label="Settings"
                        >
                          <Settings className="h-5 w-5" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuLabel>Playback Speed</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        {playbackRates.map((rate) => (
                          <DropdownMenuItem
                            key={rate}
                            onClick={() => changePlaybackRate(rate)}
                          >
                            {rate}x {rate === playbackRate && '✓'}
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>

                    {/* Picture-in-Picture */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={togglePiP}
                      className="text-white hover:bg-white/20"
                      aria-label="Picture in Picture"
                      title="Picture in Picture (P)"
                    >
                      <PictureInPicture className="h-5 w-5" />
                    </Button>

                    {/* Fullscreen */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleFullscreen}
                      className="text-white hover:bg-white/20"
                      aria-label="Fullscreen"
                      title="Fullscreen (F)"
                    >
                      {isFullscreen ? (
                        <Minimize className="h-5 w-5" />
                      ) : (
                        <Maximize className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Transcript Panel */}
      {transcript.length > 0 && (
        <div className="mt-6">
          <VideoTranscript
            transcript={transcript}
            currentTime={currentTime}
            onTimestampClick={jumpToTimestamp}
          />
        </div>
      )}

      {/* Sticky Mini Player */}
      <AnimatePresence>
        {showMiniPlayer && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.8 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="fixed bottom-4 right-4 z-50 w-80 glass-card rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="relative">
              <video
                src={videoUrl}
                className="w-full aspect-video bg-black"
                muted
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-3">
                <div className="flex items-center justify-between w-full">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={togglePlay}
                    className="text-white hover:bg-white/20"
                  >
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </Button>
                  <span className="text-white text-xs font-mono">
                    {formatTime(currentTime)}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setShowMiniPlayer(false);
                      containerRef.current?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="text-white hover:bg-white/20"
                  >
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
