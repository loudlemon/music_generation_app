import React from 'react';
import './App.css'; // You might still have App.css, you can remove its content or delete the file if you only use index.css

function App() {
  return (
    <div className="App">
      <div className="video-background">
        <video autoPlay loop muted>
          <source src="/videos/mixkit-audio-cassette-playing-with-neon-lights.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
      <div className="text-panel">
        <input type="text" className="text-input" placeholder="e.g., 'lo-fi hip hop', 'epic orchestral', 'upbeat synthwave'" />
      </div>
    </div>
  );
}

export default App;
