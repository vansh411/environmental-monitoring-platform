import React from "react";

const PredictionResult = ({ result }) => {
  if (!result) return null;

  return (
    <div style={styles.box}>
      <h3>Prediction Result</h3>

      <p><strong>Label:</strong> {result.predicted_label}</p>
      <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>

      <h4>All Probabilities</h4>
      <ul>
        {Object.entries(result.probabilities).map(([label, prob]) => (
          <li key={label}>
            {label}: {(prob * 100).toFixed(2)}%
          </li>
        ))}
      </ul>
    </div>
  );
};

const styles = {
  box: {
    marginTop: 30,
    padding: 20,
    border: "1px solid #ccc",
    borderRadius: 10,
    width: 350,
    margin: "20px auto",
    textAlign: "left",
  },
};

export default PredictionResult;