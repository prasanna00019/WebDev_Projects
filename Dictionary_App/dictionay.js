console.log("DICTIONARY APP, I AM DAMN EXCITED !!!")
const audioPlayer = document.getElementById('audioPlayer');
const audioSource = document.getElementById('audioSource');
const playBtn = document.getElementById('playBtn');
let audioUrl='';
// function playAudioFromUrl(url) {
   
//     audioSource.src = url; // Set the source of the audio element
//     audioPlayer.load(); // Load the new source
//     audioPlayer.play(); // Play the audio}

// }
function playAudioFromUrl(url) {
    if (!url) {
        console.log("No audio URL provided.");
        return;
    }
    const audio = new Audio(url);
    audio.play().catch(error => console.log("Error playing audio:", error));
}

let sound=[]
submitBtn.addEventListener("click",async (e)=>{
    ant.innerHTML=""
    syn.innerHTML=""
    // word2.innerHTML="PRONOUNCIATION"

    e.preventDefault();resultCont.innerHTML="";
    let word=document.getElementById("username").value
    // console.log(word);
    word1.innerHTML="WORD:"+word.toUpperCase();
    let url=`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`
    resultCont.innerHTML = `<img width="123" src="loading.svg" alt="">`
    let res=await fetch(url)
    let result=await res.json();
    resultCont.innerHTML=""
    if (result.title === "No Definitions Found") {
        resultCont.innerHTML = `<p style="font-size:17px;font-weight:bold">Meaning not found. Try spelling the word correctly or It seems you have given a invalid word</p>`;
        return;
    }
    console.log(result);
    // console.log(result)
   // Assuming 'data' contains your JSON array
result.forEach(item => {
    // Check if 'phonetics' array exists and is not empty
    if (item.phonetics && item.phonetics.length > 0) {
        // Iterate through 'phonetics' array
        item.phonetics.forEach(phonetic => {
            // Check if 'audio' property exists
            if (phonetic.audio) {
             
                sound.push(phonetic.audio)
                 // Output the audio URL
                // You can perform further actions with the audio URL here
            }
        }); 
    }
});
let str34;
let synonyms = [];
let antonyms = [];
result.forEach(item => {
    if (item.phonetics && item.phonetics.length > 0) {
        item.phonetics.forEach(phonetic => {
            console.log("hgg")
             str34=phonetic.text.replaceAll("/","");
            console.log(str34);
            console.log(`Phonetic Text: ${phonetic.text}`);
            // console.log(`Phonetic Audio: ${phonetic.audio}`);
        });
    }
    if (item.meanings && item.meanings.length > 0) {
        item.meanings.forEach(meaning => {
            meaning.definitions.forEach(definition => {
                if (definition.synonyms && definition.synonyms.length > 0) {
                    synonyms = synonyms.concat(definition.synonyms);
                }
                if (definition.antonyms && definition.antonyms.length > 0) {
                    antonyms = antonyms.concat(definition.antonyms);
                }
            });
        });
    }
});
ant=document.getElementById("ant");
syn=document.getElementById("syn");
console.log("Synonyms:", synonyms);
console.log("Antonyms:", antonyms);
for (let index = 0; index < antonyms.length; index++) {
    ant.innerHTML+=`${antonyms[index] }`+" "
}
for (let index = 0; index < synonyms.length; index++) {
    syn.innerHTML+=`${synonyms[index]}`+" "
}

word1.innerHTML+=`  (${str34})`
audioUrl = sound[0]; // Store the first audio URL

console.log(sound.length)
console.log(sound[0]);
if(sound.length>0){
    word2.innerHTML="PRONOUNCIATION:"

}
if(sound.length==0){
    word2.innerHTML="PRONOUNCIATION NOT AVAILAIBLE" 
    //    console.log("No audio URL provided.");
        // audioSource.src = ''; // Clear the source
        // audioPlayer.load(); // Unload the current source
        // return;
    
} 
//  else{
// // playAudioFromUrl(audioUrl);
// }
sound=[];
// if(sound[0]==""){
//     console.log(" empty")
// }
// console.log(sound[0]);
// Assuming 'result' is your array of objects with 'meanings' and 'definitions'
console.log("jk")
let c1=1;
result.forEach(item => {
    item.meanings.forEach(meaning => {
        
        meaning.definitions.forEach((definition, index) => {
            // Print each definition within a list item
            resultCont.innerHTML+=`<span>${c1} ${definition.definition}<br></span>`;c1++;
            // console.log(`${c1} ${definition.definition+ definition.index}`);c1++;
        });
        
        // console.log('</ol>');
    });
});
    
})
// const audioUrl = sound[0];
console.log(audioUrl);  
playBtn.addEventListener("click", () => {
    console.log("hello")
    playAudioFromUrl(audioUrl );
});

// Example usage with your specific URL
console.log(sound[0]);
