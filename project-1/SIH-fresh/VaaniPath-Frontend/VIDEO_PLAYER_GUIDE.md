# Premium Video Player - Usage Guide

## Quick Start

The enhanced `VideoPlayer` component is now production-ready with comprehensive features for your learning platform.

### Basic Usage

```tsx
import { VideoPlayer } from '@/components/VideoPlayer';

<VideoPlayer
  videoUrl="https://example.com/video.mp4"
  posterUrl="https://example.com/poster.jpg"
  title="Introduction to React"
/>
```

### Full-Featured Example

```tsx
import { VideoPlayer } from '@/components/VideoPlayer';
import { ChapterMarker, TranscriptEntry, CaptionTrack } from '@/types/video';

const chapters: ChapterMarker[] = [
  { time: 0, title: "Introduction", description: "Course overview" },
  { time: 120, title: "Setup", description: "Environment setup" },
  { time: 300, title: "Core Concepts", description: "Main learning content" },
];

const transcript: TranscriptEntry[] = [
  { startTime: 0, endTime: 10, text: "Welcome to this course...", speaker: "Instructor" },
  { startTime: 10, endTime: 25, text: "Today we'll learn about...", speaker: "Instructor" },
];

const captions: CaptionTrack[] = [
  { label: "English", language: "en", src: "/captions/en.vtt", default: true },
  { label: "Hindi", language: "hi", src: "/captions/hi.vtt" },
  { label: "Tamil", language: "ta", src: "/captions/ta.vtt" },
];

<VideoPlayer
  videoUrl="/videos/course-1.mp4"
  posterUrl="/posters/course-1.jpg"
  title="React Fundamentals"
  chapters={chapters}
  transcript={transcript}
  captions={captions}
  analytics={{
    onPlay: (time) => console.log('Play at', time),
    onPause: (time) => console.log('Pause at', time),
    onSeek: (from, to) => console.log('Seek from', from, 'to', to),
    onComplete: () => console.log('Video completed'),
    onBookmark: (time, note) => {
      // Save bookmark to backend
      fetch('/api/bookmarks', {
        method: 'POST',
        body: JSON.stringify({ videoId: 'course-1', timestamp: time, note })
      });
    },
    onChapterChange: (chapter) => console.log('Chapter:', chapter.title),
  }}
  startTime={0}
  autoPlay={false}
/>
```

## Features

### Keyboard Shortcuts
- **Space / K**: Play/Pause
- **Arrow Left**: Skip backward 5 seconds
- **Arrow Right**: Skip forward 5 seconds
- **J**: Skip backward 10 seconds
- **L**: Skip forward 10 seconds
- **Arrow Up**: Increase volume
- **Arrow Down**: Decrease volume
- **M**: Toggle mute
- **F**: Toggle fullscreen
- **P**: Toggle picture-in-picture
- **+/=**: Increase playback speed
- **-**: Decrease playback speed
- **B**: Bookmark current timestamp

### Accessibility
- Full keyboard navigation
- ARIA labels on all controls
- Focus-visible states
- WCAG AA contrast
- Screen reader support
- Reduced motion support

### Advanced Features
1. **Transcript Panel**: Clickable timestamps, auto-scroll, search, copy
2. **Chapter Markers**: Visual markers on progress bar with tooltips
3. **Sticky Mini-Player**: Auto-appears on scroll when video is playing
4. **Picture-in-Picture**: Native browser PiP support
5. **Analytics Hooks**: Track all user interactions
6. **Multi-Language**: Caption and audio track selection
7. **Playback Speed**: 0.5x to 2x with keyboard shortcuts
8. **Bookmarks**: Save timestamps with optional notes

## Integration with CourseDetail

Update your `CourseDetail.tsx` to use the enhanced player:

```tsx
import { VideoPlayer } from '@/components/VideoPlayer';

// In your component:
<VideoPlayer
  videoUrl={currentVideo.video_url}
  posterUrl={currentVideo.thumbnail_url}
  title={currentVideo.title}
  chapters={courseChapters}
  transcript={videoTranscript}
  captions={availableCaptions}
  analytics={{
    onComplete: handleVideoComplete,
    onBookmark: handleBookmark,
    onSeek: (from, to) => updateProgress(to),
  }}
/>
```

## Creating VTT Caption Files

Caption files should be in WebVTT format:

```vtt
WEBVTT

00:00:00.000 --> 00:00:05.000
Welcome to this course on React fundamentals.

00:00:05.000 --> 00:00:10.000
Today we'll learn about components and state.
```

Place VTT files in `/public/captions/` and reference them in the `captions` prop.

## Performance Notes

- Video uses `preload="metadata"` for lazy loading
- Controls auto-hide after 3 seconds of inactivity
- Sticky mini-player only appears when scrolled past main player
- All animations respect `prefers-reduced-motion`
- Uses `transform` and `opacity` for smooth 60fps animations

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 14+)
- Picture-in-Picture: Chrome 70+, Safari 13.1+

## Troubleshooting

**Video not playing?**
- Check video URL and CORS headers
- Ensure video format is MP4/H.264

**Captions not showing?**
- Verify VTT file format
- Check file paths are correct
- Ensure proper CORS headers for VTT files

**PiP not working?**
- Feature requires HTTPS
- Not supported on all browsers (check browser compatibility)
