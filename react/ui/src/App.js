import React, { Component, useRef, useState } from 'react';
import { HiUpload } from 'react-icons/hi';
import { TiDelete } from 'react-icons/ti';
import './App.css';
import { FileDrop } from 'react-file-drop';

function App () {
  const fileInputRef = useRef(null);
  const onTargetClick = () => {
    if (!haveFile) {
      fileInputRef.current.click();
    }
  }
  const [haveFile, setHaveFile] = useState(false);
  const [uploadText, setUploadText] =  useState("Drag and drop a file to be scanned. Click to browse.");
  const [file, setFile] = useState(null);
  const [filename, setFileName] = useState("unknown.mp4");

  var handleFileUpload = (files) => {
    setFile(files[0]);
    setFileName(files[0].name);
    setUploadText("Ready to process file: " + files[0].name);
    setHaveFile(true);
  }

  var removeFile = () => {
    setHaveFile(false);
    setFile(null);
    setFileName("unknown.mp4");
    setUploadText("Drag and drop a file to be scanned. Click to browse.");
  }

  var onFileInputChange = (event) => {
    const { files } = event.target;
    handleFileUpload(files);
  }

  function getUploadIcon() {
    if (!haveFile) {
      return <HiUpload className='upload'/>
    } else {
      return <button className="removeButton" onClick={removeFile}><span className="filename">{filename}</span> <TiDelete id="deleteIcon"/></button>
    }
  }

  return (
    <div className="App">
      <header className="banner">
        <h1 id='title'>Media Moderator</h1>
        <h4 id='subtitle'>View content with confidence</h4>
        <div className="fileDrop">
          <FileDrop
            onTargetClick={onTargetClick}
            onFrameDragEnter={(event) => console.log('onFrameDragEnter', event)}
            onFrameDragLeave={(event) => console.log('onFrameDragLeave', event)}
            onFrameDrop={(event) => console.log('onFrameDrop', event)}
            onDragOver={(event) => console.log('onDragOver', event)}
            onDragLeave={(event) => console.log('onDragLeave', event)}
            onDrop={(files, event) => {
              console.log('onDrop!', files, event);
              console.log(files);
              handleFileUpload(files);
            }}>
            {getUploadIcon()}
            <p id="fileDropInstruction">{uploadText}</p>
            <input
              onChange={onFileInputChange}
              ref={fileInputRef}
              type="file"
              className="hidden"
            />
          </FileDrop>
        </div>
      </header>
    </div>
  );
}


export default App;
