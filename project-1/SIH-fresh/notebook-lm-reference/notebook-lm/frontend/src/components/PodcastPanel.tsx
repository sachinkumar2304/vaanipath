import React, { useState, useRef } from 'react';
import { Play, Pause, Download, Loader, Mic2 } from 'lucide-react';
import axios from 'axios';
import './PodcastPanel.css';

interface PodcastPanelProps {
  theme: 'light' | 'dark';
  documentId: string;
}

const PodcastPanel: React.FC<PodcastPanelProps> = ({ theme, documentId }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [podcastUrl, setPodcastUrl] = useState<string>('');
  const [transcript, setTranscript] = useState<string>('');
  const [duration, setDuration] = useState<number>(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleGeneratePodcast = async () => {
    if (!documentId) {
      alert('Please upload a document first!');
      return;
    }

    setIsGenerating(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/podcast/generate`, {
        document_id: documentId,
        duration: 180
      });

      setPodcastUrl(`${API_BASE_URL}${response.data.audio_url}`);
      setTranscript(response.data.transcript);
      setDuration(response.data.duration);
    } catch (error) {
      console.error('Podcast generation error:', error);
      alert('Failed to generate podcast. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleDownload = () => {
    if (podcastUrl) {
      const link = document.createElement('a');
      link.href = podcastUrl;
      link.download = `podcast_${documentId}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`podcast-panel ${theme}`}>
      <div className="panel-header">
        <h2 className="panel-title">Podcast Generator</h2>
      </div>

      <div className="podcast-content">
        {!podcastUrl ? (
          <div className="generate-section">
            <div className="podcast-icon">
              <Mic2 size={64} />
            </div>
            <p className="podcast-description">
              Generate an engaging podcast conversation about your document with AI hosts Alex and Jordan
            </p>
            <button
              className="generate-button"
              onClick={handleGeneratePodcast}
              disabled={!documentId || isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader className="spin" size={20} />
                  Generating Podcast...
                </>
              ) : (
                <>
                  <Mic2 size={20} />
                  Generate Podcast
                </>
              )}
            </button>
            {!documentId && (
              <p className="warning-text">Upload a document first to generate a podcast</p>
            )}
          </div>
        ) : (
          <div className="player-section">
            <div className="audio-player">
              <audio
                ref={audioRef}
                src={podcastUrl}
                onEnded={() => setIsPlaying(false)}
              />

              <div className="player-controls">
                <button className="play-button" onClick={togglePlayPause}>
                  {isPlaying ? <Pause size={32} /> : <Play size={32} />}
                </button>
                <div className="player-info">
                  <span className="duration">{formatDuration(duration)}</span>
                </div>
                <button className="download-button" onClick={handleDownload}>
                  <Download size={24} />
                </button>
              </div>
            </div>

            <div className="transcript-section">
              <h3 className="transcript-title">Transcript</h3>
              <div className="transcript-content">
                {transcript.split('\n\n').map((line, index) => {
                  const [speaker, ...textParts] = line.split(': ');
                  const text = textParts.join(': ');
                  return (
                    <div key={index} className="transcript-line">
                      <span className="speaker">{speaker}:</span>
                      <span className="text">{text}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <button
              className="regenerate-button"
              onClick={handleGeneratePodcast}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader className="spin" size={20} />
                  Regenerating...
                </>
              ) : (
                'Regenerate Podcast'
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PodcastPanel;
