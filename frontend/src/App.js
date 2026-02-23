import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import FrontPage from "./Components/FrontPage";
import ImageUploader from "./Components/ImageUploader";

// ─── Route map ─────────────────────────────────────────────────────────────────
// /            → FrontPage  (landing)
// /classifier  → ImageUploader (land cover classifier)
// anything else → redirect to /

function ClassifierPage() {
  const [prediction, setPrediction] = useState(null);
  return (
    <ImageUploader
      onPrediction={setPrediction}
      prediction={prediction}
    />
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<FrontPage />} />
        <Route path="/classifier" element={<ClassifierPage />} />
        {/* Catch-all: redirect unknown URLs back to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
