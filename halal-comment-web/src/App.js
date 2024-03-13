import './App.css';
import * as tf from '@tensorflow/tfjs';
import React, { useState } from 'react';
import logo2 from './ketupat.png'


function App() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState(null);

  async function handlePredict() {
    setResult(null);
    try {
    const model = await tf.loadLayersModel('http://localhost:3000/tfjs_model_2/model.json');
    const word_indexjson = await fetch('http://localhost:3000/tfjs_model_2/word_index.json');
    let word2index = await word_indexjson.json();
    
    const newInputText = inputText.split(' ');
    if (!Array.isArray(newInputText)) {
      console.error("InputText is not an array");
      return;
    }
    
    if (typeof word2index !== 'object' || word2index === null) {
      console.error("word2index is not defined correctly");
      return;
    }
    console.log(newInputText);
    const sequence = newInputText.map(word => {
      let indexed = word2index[word];
      
      if (indexed === undefined){
        return 1;
      }
      return indexed;
    });
    console.log(sequence);
    const paddedInputText = padSequence(sequence, 100);
    console.log(paddedInputText);
    const inputTensor = tf.tensor2d([paddedInputText], [1, 100]);

    const prediction = model.predict(inputTensor);

    const predictionArray = prediction.arraySync();
    let status = predictionArray[0][0] > predictionArray[0][1];
    let says = "Astagfirullah";
    if (status){
      says = "MasyaAllah"
    }
    setResult(says);
    } catch (error) {
      console.error('Failed to load model:', error);
    }

    function padSequence(sequences, maxLen, padding = 'pre', truncating = 'post', pad_value = 0) {
      let paddedSeq = [...sequences]; // Create a copy of the sequence

      if (paddedSeq.length > maxLen) { // Truncate
          if (truncating === 'pre') {
              paddedSeq = paddedSeq.slice(paddedSeq.length - maxLen);
          } else {
              paddedSeq = paddedSeq.slice(0, maxLen);
          }
      }

      if (paddedSeq.length < maxLen) { // Pad
          const padLength = maxLen - paddedSeq.length;
          const pad = new Array(padLength).fill(pad_value);
          if (padding === 'pre') {
              paddedSeq = pad.concat(paddedSeq);
          } else {
              paddedSeq = paddedSeq.concat(pad);
          }
      }
      return paddedSeq;
  }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1 className='tittle'>Halal Comment</h1>
        <img src={logo2} className="App-logo" alt="logo" />
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <input
          className='input-chat'
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type Here ..."
            style={{
              margin: 20,
              padding: 10,
              borderRadius: 20,
              border: '2px solid #ccc',
              width: 'calc(200%)',
              fontSize: '14px',
            }}
          />
          <button onClick={handlePredict}>Comment</button>
          {result && (
            <div>
              <h3 style={{margin: 10}}>System says:</h3>
              <p>{result}</p>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;