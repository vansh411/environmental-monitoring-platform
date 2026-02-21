import React, { useState } from "react";
import ImageUploader from "./Components/ImageUploader";
import PredictionResult from "./Components/PredictionResult";

function App() {
  const [prediction, setPrediction] = useState(null);

  return (
    <div style={{ padding: 20 }}>
      <h1 style={{ textAlign: "center" }}>EuroSAT Land Cover Classifier</h1>

      <ImageUploader onPrediction={setPrediction} />
      <PredictionResult result={prediction} />
    </div>
  );
}

export default App;