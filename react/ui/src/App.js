import React, { useRef, useState } from 'react';
import './App.css';
import ytdl from 'react-native-ytdl';
import { HiUpload } from 'react-icons/hi';
import { TiDelete } from 'react-icons/ti';
import { FaPlay } from 'react-icons/fa';
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

  const VIDEO_URL = "http://localhost:8082/get-video-info?video_id=";
  const validateYTUrl = url => /^(?:https?:\/\/)?(w{3})?\.?youtube\.com/.test(url);


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

  var processFile = () => {
    // TODO pass the file off to the model to be predicted
    console.log(file);
  }

  async function processURL () {
    // const server = require('child_process').fork('./start_server.sh');
    const url = document.getElementById('url').value;
    if (validateYTUrl(url)) {
      /* Process YouTube URL */
      const videoId = url.split("?")[1].match(/v=([^&]+)/)[1];
      return fetch(VIDEO_URL + videoId)
        .then(res => res.text())
        .then(res => {
          return qsToJson(res);
        });
    }
  }

  function qsToJson(queryString) {
    let res = {};
    let params = queryString.split("&");
    let keyValuePair, key, value;
    for (let i in params) {
      keyValuePair = params[i].split("=");
      key = keyValuePair[0];
      value = keyValuePair[1];
      res[key] = decodeURIComponent(value);
    }
    return res;
  }

  var onFileInputChange = (event) => {
    const { files } = event.target;
    handleFileUpload(files);
  }

  function getUploadIcon() {
    if (!haveFile) {
      return <HiUpload className='upload'/>
    } else {
      return <div className="inlineButtons">
        <button className="btn" id="removeBtn" onClick={removeFile}><span className="filename">{filename}</span> <TiDelete className="btnIcon"/></button>
        <button className="btn" id="run" onClick={processFile}>RUN<FaPlay className="btnIcon"/></button>
      </div>
    }
  }

  function getURLInput() {
    if (!haveFile) {
      return <div className="inlineButtons">
        <input className="input" id="url" type="url" placeholder="Paste a URL (ex: https://youtube.com/...)" onClick={console.log("click")}></input>
        <button className="btn" id="run" onClick={processURL}>RUN<FaPlay className="btnIcon"/></button>

      </div>
    }
  }

  return (
    <div className="App">
      <header className="banner">
        <h1 id='title'>Media Moderator</h1>
        <h4 id='subtitle'>Upload an mp4 to be scrubbed</h4>
        {getURLInput()}
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
