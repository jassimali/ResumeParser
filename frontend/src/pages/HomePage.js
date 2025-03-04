import React, { useState } from "react";
import { Typography, Button, Box, Container, Paper, TextField } from "@mui/material";
import axios from "axios";

const HomePage = () => {
  const [file, setFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [extractedText, setExtractedText] = useState(""); // Stores raw text from PDFMiner
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setParsedData(null); // Reset parsed data when a new file is selected
    setExtractedText(""); // Reset extracted text
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data.error) {
        setError(response.data.error);
        setParsedData(null);
        setExtractedText("");
      } else {
        setParsedData(response.data);
        setExtractedText(response.data.extracted_text || "No text extracted.");
        setError(null);
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setError("An error occurred while uploading the file.");
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center", padding: "2rem", backgroundColor: "#f5f5f5" }}>
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ padding: "2rem", textAlign: "center" }}>
          <Typography variant="h4" gutterBottom>
            Resume Parser
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "1rem" }}>
            Upload your resume and extract details instantly.
          </Typography>

          <input type="file" onChange={handleFileChange} accept="application/pdf" style={{ marginBottom: "1rem" }} />
          {file && <Typography variant="body2" color="textSecondary">Selected File: {file.name}</Typography>}

          <Button variant="contained" onClick={handleUpload} sx={{ marginTop: "1rem", backgroundColor: "#007BFF", color: "#fff" }}>
            Upload Resume
          </Button>

          {error && (
            <Typography variant="body2" color="error" sx={{ marginTop: "1rem" }}>
              {error}
            </Typography>
          )}

          {/* Extracted Raw Text Display */}
          {extractedText && (
            <Paper sx={{ marginTop: "2rem", padding: "1.5rem", backgroundColor: "#fff", maxHeight: "300px", overflowY: "auto" }}>
              <Typography variant="h6">Extracted Raw Text:</Typography>
              <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                {extractedText}
              </Typography>
            </Paper>
          )}

          {/* Parsed Resume Data Display */}
          {parsedData && (
            <Paper sx={{ marginTop: "2rem", padding: "1.5rem", backgroundColor: "#fff" }}>
              <Typography variant="h5" gutterBottom>
                Parsed Resume Data:
              </Typography>
              <TextField label="Name" value={parsedData.name || "Not Found"} fullWidth margin="normal" disabled />
              <TextField label="Email" value={parsedData.email || "Not Found"} fullWidth margin="normal" disabled />
              <TextField label="Phone" value={parsedData.phone || "Not Found"} fullWidth margin="normal" disabled />
              <TextField label="GitHub" value={parsedData.github || "Not Found"} fullWidth margin="normal" disabled />
              <TextField label="LinkedIn" value={parsedData.linkedin || "Not Found"} fullWidth margin="normal" disabled />
              <TextField label="Skills" value={parsedData.skills ? parsedData.skills.join(", ") : "Not Found"} fullWidth margin="normal" disabled />
            </Paper>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default HomePage;