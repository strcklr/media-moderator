import React, { Component } from 'react';
import { HiUpload } from 'react-icons/hi';
import { TiDelete } from 'react-icons/ti';
import './App.css';
import { FileDrop } from 'react-file-drop';

class App extends Component {
  state = {
    haveFile: false,
    uploadText: "Drag and drop a file to be scanned. Click to browse.",
    file: "unkkj;lkjasdl;kfja;lsdkfja;lsdkjown.mp4",
  }

  removeFile = () => {
    this.setState({
      haveFile: false,
      uploadText: "Drag and drop a file to be scanned. Click to browse.",
      file: "unknown.mp4"
    });
  }

  getUploadIcon() {
    if (!this.state.haveFile) {
      return <HiUpload className='upload'/>
    } else {
      return <button className="removeButton" onClick={this.removeFile}><span className="filename">{this.state.file}</span> <TiDelete id="deleteIcon"/></button>
    }
  }

  render() {
    return (
      <div className="App">
        <header className="banner">
          <h1 id='title'>Media Moderator</h1>
          <h4 id='subtitle'>View content with confidence</h4>
          <div className="fileDrop">
            <FileDrop
              onFrameDragEnter={(event) => console.log('onFrameDragEnter', event)}
              onFrameDragLeave={(event) => console.log('onFrameDragLeave', event)}
              onFrameDrop={(event) => console.log('onFrameDrop', event)}
              onDragOver={(event) => console.log('onDragOver', event)}
              onDragLeave={(event) => console.log('onDragLeave', event)}
              onDrop={(files, event) => {
                console.log('onDrop!', files, event);
                console.log(files);
                const filename = files[0].name;
                this.setState({
                  file: filename,
                  haveFile: true,
                  uploadText: "Ready to process file: " + filename
                })

              }}>
              {this.getUploadIcon()}
              <p id="fileDropInstruction">{this.state.uploadText}</p>
            </FileDrop>
          </div>
        </header>
      </div>
    );
  }
}


export default App;
