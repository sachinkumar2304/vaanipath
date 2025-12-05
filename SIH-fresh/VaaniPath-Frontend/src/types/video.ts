// Video Player Type Definitions

export interface ChapterMarker {
    time: number;
    title: string;
    description?: string;
}

export interface TranscriptEntry {
    startTime: number;
    endTime: number;
    text: string;
    speaker?: string;
}

export interface CaptionTrack {
    label: string;
    language: string;
    src: string;
    default?: boolean;
}

export interface AudioTrack {
    label: string;
    language: string;
    src: string;
    default?: boolean;
}

export interface Bookmark {
    timestamp: number;
    note?: string;
    createdAt: Date;
}

export interface VideoAnalytics {
    onPlay?: (currentTime: number) => void;
    onPause?: (currentTime: number) => void;
    onSeek?: (from: number, to: number) => void;
    onComplete?: () => void;
    onSpeedChange?: (speed: number) => void;
    onVolumeChange?: (volume: number) => void;
    onBookmark?: (timestamp: number, note?: string) => void;
    onChapterChange?: (chapter: ChapterMarker) => void;
    onTranscriptClick?: (timestamp: number) => void;
}

export interface VideoPlayerProps {
    videoUrl: string;
    posterUrl?: string;
    title?: string;
    chapters?: ChapterMarker[];
    transcript?: TranscriptEntry[];
    captions?: CaptionTrack[];
    audioTracks?: AudioTrack[];
    analytics?: VideoAnalytics;
    className?: string;
    autoPlay?: boolean;
    startTime?: number;
}
