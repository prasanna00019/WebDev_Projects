const express = require('express');
const { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } = require('@google/generative-ai');
const dotenv = require('dotenv').config()

const app = express();
const port = process.env.PORT || 3000;
app.use(express.json());
const MODEL_NAME = "gemini-pro";
const API_KEY = "AIzaSyDT7bvq6tWlQsf9-3-uwGxWYCO9VHGAGQI";

async function runChat(userInput) {
 const genAI = new GoogleGenerativeAI(API_KEY);
 const model = genAI.getGenerativeModel({ model: MODEL_NAME });

 const generationConfig = {
  temperature: 0.9,
  topK: 1,
  topP: 1,
  maxOutputTokens: 2000,
 };

 const safetySettings = [
  {
   category: HarmCategory.HARM_CATEGORY_HARASSMENT,
   threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
  },
  // ... other safety settings
 ];

 const chatSession = model.startChat({
 generationConfig,
  safetySettings,
 });

 try {
  
  const result = await chatSession.sendMessage(userInput);
  const response = result.response;
  return response.text().replaceAll("*","").replaceAll("\n","<br>");
 } catch (error) {
  console.error('Error during chat interaction:', error);
  return 'Error: Something went wrong. Please try again.';  // Friendly error message for user
 }
}

app.get('/', (req, res) => {
 res.sendFile(__dirname + '/index2.html');
});
app.get('/loader.gif', (req, res) => {
 res.sendFile(__dirname + '/loader.gif'); // Assuming loader.gif is within index2.html
});
app.post('/chat', async (req, res) => {
 try {
  const userInput = req.body?.userInput;
  console.log('incoming /chat req', userInput);
  if (!userInput) {
   return res.status(400).json({ error: 'Invalid request body' });
  }

 const response = await runChat(userInput);
 res.json({ response });
 } catch (error) {
  console.error('Error in chat endpoint:', error);
  res.status(500).json({ error: 'Internal Server Error' });
 }
});

app.listen(port, () => {
 console.log(`Server listening on port ${port}`);
});