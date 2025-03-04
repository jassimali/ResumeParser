import React, { useState } from "react";
import axios from "axios";
import { Button, Box, Typography } from "@mui/material";

const UploadResume = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);


    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(response.data.message);
    } catch (error) {
      console.error("Error uploading file:", error);
      setMessage("Failed to upload.");
    }
  };

  return (
    <Box textAlign="center" mt={5}>
      <Typography variant="h4">Upload Resume</Typography>
      <input type="file" onChange={handleFileChange} />
      <Button variant="contained" color="primary" onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload
      </Button>
      {message && <Typography variant="body1" mt={2}>{message}</Typography>}
    </Box>
  );
};

export default UploadResume;
