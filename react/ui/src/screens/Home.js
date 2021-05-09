import React, { useRef, useState } from 'react';
import './../styles/App.css';
// import axios from 'axios';
import UploadFilesService from '../services/upload-file.service'
import * as settings from '../util/settings';
import { HiUpload } from 'react-icons/hi';
import { TiDelete } from 'react-icons/ti';
import { FaPlay } from 'react-icons/fa';
import { FileDrop } from 'react-file-drop';
import Spinner from 'react-bootstrap/Spinner'

function Home () {
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
  const [response, setResponse] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [awaitingResponse, setAwaitingResponse] = useState(false);
  const [progress, setProgress] = useState(0);

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
    setResponse(null);
  }

  var onUploadProgress = () => {

  }

  var uploadFile = () => {
    setUploading(true);
    console.log(file);
    setAwaitingResponse(true);
    UploadFilesService.upload(file, (event) => {
      setProgress((100 * event.loaded) / event.total);
      console.log(progress);
    }).then(
      res => {
        console.log(res.data)
        setResponse(res);
        setAwaitingResponse(false);
      }).catch(
        error => {
          alert(error);
          setUploading(false);
        }

      );

    
    // let form = new FormData();
    // form.append('file', file);

    // let headers = { 'Content-Type' : 'multipart/form-data'};
    // let url = settings.API_SERVER + '/api/predict/';
    // let method = 'post';
    // let config = { headers, method, url, data: form};


    // axios.post

    // axios(config).then(
    //   res => {
    //     console.log(res.data)
    //     setResponse(res);
    //   }).catch(
    //     error => {alert(error)}
    //   );
  }

  var predictionBorderStyle = (confidence) => {
    if (confidence >= 90) {
      return { border: '3px solid #379152' };
    } else if (confidence < 90 && confidence >= 70) {
      return { border: '3px solid yellow' };
    } else {
      return { border: '3px solid #db4650' };
    }
  }

  async function processURL () {
  //   return;
  //  const url = document.getElementById('url').value;
  //  if (validateYTUrl(url)) {
  //    /* Process YouTube URL */
  //    const videoId = url.split("?")[1].match(/v=([^&]+)/)[1];
  //    return fetch(VIDEO_URL + videoId)
  //      .then(res => res.text())
  //      .then(res => {
  //        return qsToJson(res);
  //      });
  //  }
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
        <button className="btn" id="removeBtn" onClick={removeFile}><span className="filename">{filename}</span><TiDelete className="btnIcon"/></button>
        <button className="btn" id="run" onClick={uploadFile}>RUN<FaPlay className="btnIcon"/></button>
      </div>
    }
  }

  function getURLInput() {
    if (!haveFile && !uploading && !awaitingResponse) {
      return <div className="inlineButtons">
        <input className="input" id="url" type="url" placeholder="Paste a URL (ex: https://youtube.com/...)" onClick={console.log("click")}></input>
        <button className="btn" id="run" onClick={processURL}>RUN<FaPlay className="btnIcon"/></button>

      </div>
    }
  }

  function getContentArea() {
    return getLoadingIndicator();
    if (response == null && !uploading) {
      return getFileDropper();
    } else if (uploading) {
      return getLoadingIndicator();
    } else {
      return getPredictionView();
    }
  }

  function getLoadingIndicator() {
    return <Spinner animation="border"/>
  }

  function getPredictionView() {
    console.log(file);
    var confidence = Number(response.data['Confidence']);
    return <div className="imagePrediction">
      <img className="imgSource" style={predictionBorderStyle(confidence)} alt='source' src={URL.createObjectURL(file)}/>
      <div className="predictionColumn">
        <h4 className="predictionData">Predicted Classification: {response.data['Predicted Classification']}</h4>
        <h4 className="predictionData">Confidence: {confidence}%</h4>
        <button className='btn' id='clear' onClick={removeFile}>CLEAR<TiDelete className="btnIcon"/></button>
      </div>
    </div>
  }

  function getFileDropper() {
      return <div className="fileDrop">
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
  }

  return (
    <div className="Home">
      <header className="banner">
        <h1 id='title'>Media Moderator</h1>
        <h4 id='subtitle'>Upload an mp4 to be scrubbed</h4>
        {getURLInput()}
        {getContentArea()}
      </header>
    </div>
  );
}


export default Home;
