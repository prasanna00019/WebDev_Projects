import { GoogleGenerativeAI } from "@google/generative-ai";
    
let btn=document.getElementById("a1");
let output=document.getElementById("o1")
        // Fetch your API_KEY
        const API_KEY = "AIzaSyDT7bvq6tWlQsf9-3-uwGxWYCO9VHGAGQI";
        // Reminder: This should only be for local testing
  
        // Access your API key (see "Set up your API key" above)
        const genAI = new GoogleGenerativeAI(API_KEY);
  
        btn.addEventListener("click",async()=>{
  console.log("clicked")
  output.innerHTML="";
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash"});
    let user_text=document.getElementById("t1").value;
    const prompt = user_text;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    // const t11=response.json();
    // console.log(t11);
    console.log(response)
    console.log(result)
    output.innerHTML=text;
    // console.log(text);

  
 })