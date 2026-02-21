import React, { useState } from "react";
import axios from "axios";

const ImageUploader = ({ onPrediction }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setSelectedImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const handlePredict = async () => {
    if (!selectedImage) return;

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      setLoading(true);

      const response = await axios.post(
        "http://localhost:8000/predict", // your backend endpoint
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      onPrediction(response.data);
    } catch (err) {
      console.error("Prediction error:", err);
      alert("Error predicting image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>EuroSAT Land Cover Classification</h2>

      <input type="file" accept="image/*" onChange={handleImageChange} />

      {preview && (
        <img
          src={preview}
          alt="preview"
          style={{ width: 250, marginTop: 20, borderRadius: 8 }}
        />
      )}

      <button onClick={handlePredict} style={styles.button}>
        {loading ? "Predicting..." : "Predict"}
      </button>
    </div>
  );
};

const styles = {
  container: {
    textAlign: "center",
    padding: 20,
  },
  button: {
    marginTop: 20,
    padding: "10px 20px",
    fontSize: 16,
    cursor: "pointer",
  },
};

export default ImageUploader;