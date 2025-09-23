import React, { useState, useEffect, useRef } from 'react';
import './App.css'; // Make sure this CSS file exists
import { FaPlay, FaPause, FaDownload } from 'react-icons/fa'; // Install react-icons: npm install react-icons

function App() {
  const [prompt, setPrompt] = useState('');
  const [generatedTracks, setGeneratedTracks] = useState([]);
  const [statusMessage, setStatusMessage] = useState('Enter a prompt and click Generate!');
  const [isLoading, setIsLoading] = useState(false);
  const [currentPlaying, setCurrentPlaying] = useState(null); // Track which audio is playing
  const ws = useRef(null); // Use useRef for WebSocket instance

  // --- WebSocket Connection ---
  useEffect(() => {
    // Open WebSocket connection
    ws.current = new WebSocket('ws://localhost:8000/api/v1/ws'); // Connect to your FastAPI WebSocket endpoint

    ws.current.onopen = () => {
      console.log('WebSocket connection established.');
      setStatusMessage('Connected to MusicGen service.');
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('Received message:', message);

      switch (message.type) {
        case 'connected':
          setStatusMessage(message.data.message);
          break;
        case 'status':
          setStatusMessage(message.data.message);
          setIsLoading(true);
          break;
        case 'complete':
          setStatusMessage(message.data.message);
          setGeneratedTracks(prevTracks => [
            {
              id: Date.now(), // Unique ID for React list key
              prompt: message.data.prompt,
              url: `http://localhost:8000${message.data.url}`, // Prepend FastAPI base URL
              duration: message.data.duration,
              isPlaying: false,
            },
            ...prevTracks, // Add new track to the top
          ]);
          setIsLoading(false);
          setPrompt(''); // Clear prompt after generation
          break;
        case 'error':
          setStatusMessage(`Error: ${message.data.message}`);
          setIsLoading(false);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    };

    ws.current.onclose = () => {
      console.log('WebSocket connection closed.');
      setStatusMessage('Disconnected from MusicGen service. Please refresh.');
            setIsLoading(false);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatusMessage('WebSocket error occurred. Check console.');
      setIsLoading(false);
    };

    // Clean up WebSocket connection on component unmount
    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close();
      }
    };
  }, []); // Empty dependency array means this runs once on mount

  // --- Handlers ---
  const handleGenerate = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      if (prompt.trim()) {
        setIsLoading(true);
        setStatusMessage('Sending prompt to server...');
        ws.current.send(JSON.stringify({ type: 'generate', prompt: prompt }));
      } else {
        setStatusMessage('Please enter a prompt!');
      }
    } else {
      setStatusMessage('WebSocket not connected. Please refresh the page.');
    }
  };

  const togglePlay = (trackId, url) => {
    setGeneratedTracks(prevTracks =>
      prevTracks.map(track => {
        if (track.id === trackId) {
          return { ...track, isPlaying: !track.isPlaying };
        } else if (track.isPlaying) {
          // Pause other playing tracks
          return { ...track, isPlaying: false };
        }
        return track;
      })
    );

    const audio = document.getElementById(`audio-${trackId}`);
    if (audio) {
      if (audio.paused) {
        // Pause any currently playing audio before playing the new one
        if (currentPlaying && currentPlaying !== audio) {
          currentPlaying.pause();
          // Update state for the previously playing track to reflect pause
          setGeneratedTracks(prevTracks =>
            prevTracks.map(t => (t.id === parseInt(currentPlaying.id.replace('audio-', ''))) ? { ...t, isPlaying: false } : t)
          );
        }
        audio.play();
        setCurrentPlaying(audio);
      } else {
        audio.pause();
        setCurrentPlaying(null);
      }
    }
  };

  const handleAudioEnded = (trackId) => {
    setGeneratedTracks(prevTracks =>
      prevTracks.map(track =>
        track.id === trackId ? { ...track, isPlaying: false } : track
      )
    );
    if (currentPlaying && parseInt(currentPlaying.id.replace('audio-', '')) === trackId) {
      setCurrentPlaying(null);
    }
  };


  return (
    <div className="App">
      <div className="video-background">
        <video autoPlay loop muted>
          <source src="/videos/mixkit-audio-cassette-playing-with-neon-lights.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      <div className="content-overlay">
        <h1 className="app-title">MusicGen AI</h1>
        <div className="text-panel">
          <input
            type="text"
            className="text-input"
            placeholder="e.g., 'lo-fi hip hop', 'epic orchestral', 'upbeat synthwave'"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isLoading) {
                handleGenerate();
              }
            }}
            disabled={isLoading}
          />
          <button onClick={handleGenerate} className="generate-button" disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate Music'}
          </button>
          <div className="status-bar">
            {statusMessage}
          </div>
        </div>

        <div className="generated-music-list">
          <h2>Generated Tracks</h2>
          {generatedTracks.length === 0 && !isLoading && (
                        <p className="no-tracks-message">No tracks generated yet. Try one!</p>
          )}
          {generatedTracks.map((track) => (
            <div key={track.id} className="music-track-item">
              <p className="track-prompt">{track.prompt}</p>
              <div className="audio-controls">
                <button
                  className="play-pause-button"
                  onClick={() => togglePlay(track.id, track.url)}
                >
                  {track.isPlaying ? <FaPause /> : <FaPlay />}
                </button>
                <audio
                  id={`audio-${track.id}`}
                  src={track.url}
                  onEnded={() => handleAudioEnded(track.id)}
                  onPlay={() => {
                    // Ensure state is correctly updated if played by native controls
                    setGeneratedTracks(prevTracks =>
                      prevTracks.map(t => (t.id === track.id) ? { ...t, isPlaying: true } : { ...t, isPlaying: false })
                    );
                    setCurrentPlaying(document.getElementById(`audio-${track.id}`));
                  }}
                  onPause={() => {
                     // Ensure state is correctly updated if paused by native controls
                    setGeneratedTracks(prevTracks =>
                      prevTracks.map(t => (t.id === track.id) ? { ...t, isPlaying: false } : t)
                    );
                    if (currentPlaying && parseInt(currentPlaying.id.replace('audio-', '')) === track.id) {
                      setCurrentPlaying(null);
                    }
                  }}
                ></audio>
                <a href={track.url} download={`${track.prompt.substring(0, 30)}.wav`} className="download-button">
                  <FaDownload />
                </a>
              </div>
              <span className="track-duration">({track.duration})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
