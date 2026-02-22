import React, { useState } from "react";
import FrontPage from "./Components/FrontPage";
import ImageUploader from "./Components/ImageUploader";

// ─── View constants ────────────────────────────────────────────────────────────
// Add new views here as your app grows (e.g. VIEWS.DASHBOARD, VIEWS.SETTINGS)
const VIEWS = {
  HOME: "home",
  CLASSIFIER: "classifier",
};

function App() {
  const [view, setView] = useState(VIEWS.HOME);
  const [prediction, setPrediction] = useState(null);

  const goToClassifier = () => {
    setPrediction(null); // clear stale result each time
    setView(VIEWS.CLASSIFIER);
  };

  const goHome = () => setView(VIEWS.HOME);

  if (view === VIEWS.HOME) {
    // Both "Open Land Cover Classifier" and "Launch Classifier" buttons
    // in FrontPage call onLaunchApp — they both map here
    return <FrontPage onLaunchApp={goToClassifier} />;
  }

  if (view === VIEWS.CLASSIFIER) {
    // PredictionResult is now embedded inside the redesigned ImageUploader
    return (
      <ImageUploader
        onPrediction={setPrediction}
        prediction={prediction}
        onGoHome={goHome}
      />
    );
  }

  return null;
}

export default App;
