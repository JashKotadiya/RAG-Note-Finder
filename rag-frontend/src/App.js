import { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState(""); 
  const [answer, setAnswer] = useState(""); 
  const [source, setSource] = useState(""); 
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  const handleUpload = async() => {
    if (!file) return;
    // Form data is a special JS object which builds key value pairs, with file as the key and the file that you upload as the value
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload", formData, {
        // Headers are metadata about the reuqest and they tell what type of data is being sent, you have to tell the server that you are sending multipart form data
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadMessage(`Uploaded: ${response.data.filename}`);
    } catch (error) {
      console.error(error);
      setUploadMessage("Upload failed");
    }
  };

// async() => is a nameless function, it needs to be async for promise objects to be inside of it 
// If this function was not async() because JS is single threaded nothing else in the background would be able to run while this function is happening 
// Making this function async means only this function is paused but everything else is still running 
// async returns a promise
const handleSubmit = async() => {
  // if question is null, empty or undefined, stop the function, and prevent sending an empty question to the backend
  if (!question) {
    return;
  }
  setLoading(true); 
  try {
    // The axios method returns a JavaScript object which represents a value you do not have yet - a promise
    // Because going through Cohere and getting the response back takes a while JS does not want to pause everything while it waits 
    // So what we have to do is use the await keyword to tell JS to pause the operation of the function until the promise finishes so we get the actual response from the backend 
    // and not the promise object
    const response = await axios.post("http://127.0.0.1:8000/ask", { question });
    setAnswer(response.data.answer);
    setSource(response.data.source);

  } catch (error) { // We dont need to specefiy a specefic error class because JS is dynamcially typed, and this block always catches what the promise throws
    console.error(error);
    setAnswer("Error fetching answer");
    setSource("");
  }
  finally {
      setLoading(false);
    }
}; 

// On change runs everytime the user types in the textbox
        // Whenever the user interacts with the page, the browser creates an event object
        // The event object is passed to the e parameter, React automatically provides this to all the event handlers
        // e.target is the HTML element which triggered the event 
        // e.target.value is the text the user typed

return (
     <div style={styles.container}>
      <h1 style={styles.title}>📚 RAG Note Finder</h1>

      
      {/* File Upload */}
      <div style={styles.uploadContainer}>
  <input
    type="file"
    onChange={(e) => setFile(e.target.files[0])}
    style={styles.uploadInput}
  />
  <button
    onClick={handleUpload}
    style={styles.uploadButton}
    disabled={!file}
  >
    Upload File
  </button>
</div>
{uploadMessage && <p style={styles.uploadMessage}>{uploadMessage}</p>}

      <div style={styles.inputContainer}>
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={styles.input}
        />
        <button onClick={handleSubmit} style={styles.button} disabled={loading}>
          {loading ? "Searching..." : "Ask"}
        </button>
      </div>
      {/* For JS an empty string is false and any other string is True, so this code is checking if answer is some filled in string then render the answer, otherwise do not   */}
   {answer && (
        <div style={styles.resultContainer}>
          <h2 style={styles.resultTitle}>Answer:</h2>
          <p style={styles.resultText}>{answer}</p>
          <h3 style={styles.resultTitle}>Source:</h3>
          <p style={styles.resultText}>{source}</p>
        </div>
      )}
    </div>
  ) 
};


const styles = {
  container: {
    maxWidth: "700px",
    margin: "40px auto",
    padding: "20px",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    backgroundColor: "#f5f5f5",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
  },
  title: {
    textAlign: "center",
    color: "#333",
  },
  inputContainer: {
    display: "flex",
    marginTop: "20px",
    gap: "10px",
  },
  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "16px",
  },
  button: {
    padding: "12px 20px",
    border: "none",
    borderRadius: "8px",
    backgroundColor: "#007bff",
    color: "white",
    fontSize: "16px",
    cursor: "pointer",
    transition: "background-color 0.2s",
  },
  resultContainer: {
    marginTop: "30px",
    padding: "20px",
    backgroundColor: "white",
    borderRadius: "10px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
  resultTitle: {
    marginBottom: "5px",
    color: "#555",
  },
  resultText: {
    marginBottom: "15px",
    color: "#333",
  },
};

export default App;