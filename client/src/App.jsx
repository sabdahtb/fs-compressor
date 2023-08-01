import axios from "axios";
import { useDropzone } from "react-dropzone";
import { useCallback, useState } from "react";

import "./App.css";

function App() {
  const [selected, setSelected] = useState(undefined);
  const [response, setResponse] = useState(undefined);
  const [uploadedImages, setUploadedImages] = useState([]);

  function clearAll() {
    setSelected(undefined);
    setResponse(undefined);
    setUploadedImages([]);
  }

  async function compres() {
    const formData = new FormData();
    formData.append("image", selected);

    try {
      // Make the POST request using Axios
      const response = await axios.post(
        "http://127.0.0.1:5000/compress",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Handle the response here, if needed
      setResponse(response.data[0]);
    } catch (error) {
      // Handle any errors that occurred during the request
      console.error("Error:", error);
    }
  }

  function getFileNameWithoutExtension(fileName) {
    const lastIndex = fileName.lastIndexOf(".");
    if (lastIndex === -1) {
      // File has no extension
      return fileName;
    } else {
      // Extract the file name without extension
      return fileName.slice(0, lastIndex);
    }
  }

  function downloadClick() {
    const nameOfFile = selected.name || "image.png";

    const contentType = selected.type || "";
    const base64Data = response.compressed_image_base64;
    const fileName = `${getFileNameWithoutExtension(
      nameOfFile
    )}_compressed.png`;

    const linkSource = `data:${contentType};base64,${base64Data}`;
    const downloadLink = document.createElement("a");
    downloadLink.href = linkSource;
    downloadLink.download = fileName;
    downloadLink.click();
  }

  const onDrop = useCallback((acceptedFiles) => {
    // Append the newly uploaded images to the existing images in the state
    setUploadedImages((prevUploadedImages) => [
      ...prevUploadedImages,
      ...acceptedFiles,
    ]);
  }, []);

  const removeImage = (index) => {
    // Remove the image from the state based on its index
    setUploadedImages((prevUploadedImages) =>
      prevUploadedImages.filter((_, i) => i !== index)
    );
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    noDrag: true,
  });

  return (
    <>
      <div className="top-section">
        <div {...getRootProps()} className={"dropzone"}>
          <input {...getInputProps()} />
          <p>open</p>
        </div>
        {uploadedImages && (
          <button onClick={clearAll} className="clear">
            Clear All
          </button>
        )}
      </div>

      <div className="image-list">
        {uploadedImages.map((file, index) => (
          <div key={index} className="image-item">
            <img
              onClick={() => setSelected(file)}
              src={URL.createObjectURL(file)}
              alt={`Uploaded ${index + 1}`}
            />
            <button onClick={() => removeImage(index)}>x</button>
          </div>
        ))}
      </div>

      <div className="compress-container">
        {selected && (
          <div className="result">
            <img src={URL.createObjectURL(selected)} alt={`Selected`} />
            <p>{`original size : ${selected.size} bytes`}</p>
          </div>
        )}

        {response && selected.size === response.original_size && (
          <div className="result relative">
            <img
              src={`data:image/png;base64, ${response.compressed_image_base64}`}
              alt="result"
            />
            <p>{`compressed size : ${response.compressed_size} bytes`}</p>
            <button className="download-btn" onClick={downloadClick}>
              download
            </button>
          </div>
        )}
      </div>

      <div className="btn-section">
        {selected && (
          <button className="btn-compress" onClick={compres}>
            Compress
          </button>
        )}
      </div>
    </>
  );
}

export default App;
