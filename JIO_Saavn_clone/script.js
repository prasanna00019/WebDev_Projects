a11 = document.getElementById("a11");
let isPlaying = false;
let songs_arr;
let songs_info;
let song_artist;
const back5=document.getElementById("back-5");
const forw5=document.getElementById("forw-5");
let loopEnabled=false;
const loopbtn=document.getElementById("loop")
const loopable=document.getElementById("loopable");
const loopdisable=document.getElementById("loopdisable")
let playButton = document.getElementById('play-button');

let songs_img;
let currentAudio=new Audio();
document.addEventListener("DOMContentLoaded", () => {
    const logoElement = document.querySelector('.logoimg');
    if (logoElement) {
        logoElement.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
});

const songTimeElement = document.querySelector('.songtime');
document.querySelector(".hamburger").addEventListener("click",()=>{
    document.querySelector(".a10").style.left="0";
 })
 document.querySelector(".close").addEventListener("click",()=>{
    document.querySelector(".a10").style.left="-120%";
 })
function secondsToMinutesSeconds(seconds) {
    if (isNaN(seconds) || seconds < 0) {
        return "00:00";
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);

    const formattedMinutes = String(minutes).padStart(2, '0');
    const formattedSeconds = String(remainingSeconds).padStart(2, '0');

    return `${formattedMinutes}:${formattedSeconds}`;
}
function setupLoop(audio) {
    audio.addEventListener("ended", () => {
        if (loopEnabled) {
            let index = songs_arr.indexOf(audio.src);
            currentAudio = new Audio(songs_arr[index]);
            currentAudio.play();
            document.querySelector(".songtime").innerHTML = "00:00/00:00"
            currentAudio.addEventListener("timeupdate", () => {
                document.querySelector(".songtime").innerHTML = `
                ${secondsToMinutesSeconds(currentAudio.currentTime)}/
                ${secondsToMinutesSeconds(currentAudio.duration)}`
                document.querySelector(".circle").style.left = (currentAudio.currentTime / currentAudio.duration) * 100 + "%";
            })
            document.querySelector(".seekbar").addEventListener("click", e => {
                let percent = (e.offsetX / e.target.getBoundingClientRect().width) * 100;
                document.querySelector(".circle").style.left = percent * 100 + "%";
                currentAudio.currentTime = ((currentAudio.duration) * percent) / 100;
            })
            setupLoop(currentAudio);  // Ensure loop setup for the new audio
        }
        else{
           playButton.src='img/play-button.png'
        }
    });
}
async function getsongs() {
    currentAudio.pause()
    playButton.src='img/play-button.png'
     songs_arr=[]; songs_info=[];song_artist=[]; songs_img=[];
    a11.innerHTML = "";
    const input_query = document.getElementById("inp").value;
    try {
        a11.innerHTML=`<img class="load"  src="img/load3.svg ">`;
        let response = await fetch(`https://saavn.dev/api/search/songs?query=${input_query}`);
        let responseData = await response.json();
       console.log(responseData);
       if(responseData.data.total==0){
        a11.innerHTML=`<img src="img/not-found.png">
        <br> NO SONG FOUND.`
       }
       else{
        a11.innerHTML='';
       }
        const results = responseData.data.results;
       
        results.forEach(song => {
            let songName = song.name.replaceAll("&quot", "").replace(";", ":").replace(";", "");
            let songUrl = song.downloadUrl[4].url;
            let label = song.label;
            let songImg = song.image[2].url;
            let language = song.language;
            let year = song.year;
            songs_arr.push(songUrl);
            songs_info.push(songName);
            song_artist.push(label);
            songs_img.push(songImg);

            // Create a new div for each song
            let songDiv = document.createElement('div');
            songDiv.classList.add('song');
            songDiv.setAttribute('data-songname', songName);
            songDiv.setAttribute('data-artist', label);
            songDiv.setAttribute('data-img',songImg);
            songDiv.innerHTML = `
                <img src="${songImg}" width="100" height="100" />
                <h2>${songName}</h2>
                <h3>${label}</h3>
                <h3>${language}</h3>
                <h3>${year}</h3>
                <audio src="${songUrl}" style="display:none" controls></audio>`;

            a11.appendChild(songDiv);
          
            songDiv.addEventListener('click', () => {

                const songName = songDiv.getAttribute('data-songname');
                const artist = songDiv.getAttribute('data-artist');
                const audio = songDiv.querySelector('audio');
                const img123=songDiv.getAttribute('data-img');
                console.log('image source',img123)
                console.log('Song Name:', songName);
                console.log('Artist:', artist);
                console.log('Audio Source:', audio.src);
                console.log("duration:",audio.duration)
                let play1=document.getElementById("play-1");
                play1.innerHTML=`  <img src=${img123} width="50px" height="50px" alt="">
            <div class="songinfo" style="display: flex;flex-direction: column;width:150px;text-overflow:ellipsis;padding-left: 10px;">
             <span style="text-overflow:ellipsis">${songName} </span>
             <span>${artist}</span>
             </div>`
            
             if (isPlaying) {
                currentAudio.pause();
                currentAudio.currentTime = 0;
                isPlaying = false; // Reset the isPlaying state
                playButton.src = 'img/play-button.png'; // Reset the play button image
            }
             
            currentAudio = new Audio(audio.src);
            document.querySelector(".songtime").innerHTML="00:00/00:00"
            currentAudio.addEventListener("timeupdate",()=>{
                // console.log(currentAudio.duration,currentAudio.currentTime)
                document.querySelector(".songtime").innerHTML=`
                ${secondsToMinutesSeconds(currentAudio.currentTime)}/
                ${secondsToMinutesSeconds(currentAudio.duration)}`
                document.querySelector(".circle").style.left=(currentAudio.currentTime/currentAudio.duration)*100+"%"; 
             })
             document.querySelector(".seekbar").addEventListener("click",e=>{
                let percent=(e.offsetX/e.target.getBoundingClientRect().width)*100;
               
                document.querySelector(".circle").style.left=percent*100+"%";
                currentAudio.currentTime =((currentAudio.duration) * percent)/100;
                
             })
             setupLoop(currentAudio);  // Set up the loop for the newly selected audio

            currentAudio.play()
        playButton.src = 'img/pause.svg';        
        isPlaying=true;
            });

           
           
        });
       

    } catch (error) {
        console.error('Error fetching songs:', error);
        a11.innerHTML=`<img src="no-internet-connection.svg">`
    }
    

// const playButton = document.getElementById('play-button');
const volumeRange = document.querySelector(".range").getElementsByTagName("input")[0];
    const volumeIcon = document.querySelector(".volume>img");

    volumeRange.addEventListener("change", (e) => {
        const volume = parseInt(e.target.value) / 100;
        currentAudio.volume = volume;
        
        if (volume === 0) {
            volumeIcon.src = "img/mute.svg";
        } else {
            volumeIcon.src = "img/volume.svg";
        }
    });



} //end of getsongs() function ....

let next =document.getElementById("next");
next.addEventListener("click",()=>{
    currentAudio.pause();
    console.log(songs_info);
    console.log(songs_img);
    console.log(song_artist);
    let ind;
    let index=songs_arr.indexOf(currentAudio.src);
    if(index==songs_img.length-1){ind=0;}
    else{ind=index+1;}
    currentAudio= new Audio(songs_arr[ind]);
   
    document.querySelector(".songtime").innerHTML="00:00/00:00"
    currentAudio.addEventListener("timeupdate",()=>{
        // console.log(currentAudio.duration,currentAudio.currentTime)
        document.querySelector(".songtime").innerHTML=`
        ${secondsToMinutesSeconds(currentAudio.currentTime)}/
        ${secondsToMinutesSeconds(currentAudio.duration)}`
        document.querySelector(".circle").style.left=(currentAudio.currentTime/currentAudio.duration)*100+"%"; 
     })
     document.querySelector(".seekbar").addEventListener("click",e=>{
        let percent=(e.offsetX/e.target.getBoundingClientRect().width)*100;
       
        document.querySelector(".circle").style.left=percent*100+"%";
        currentAudio.currentTime =((currentAudio.duration) * percent)/100;
        
     })
     let play1=document.getElementById("play-1");
                play1.innerHTML=`  <img src=${songs_img[ind]} width="50px" height="50px" alt="">
            <div class="songinfo" style="display: flex;flex-direction: column;width:150px;text-overflow:ellipsis;padding-left: 10px;">
             <span style="text-overflow:ellipsis">${songs_info[ind]} </span>
             <span>${song_artist[ind]}</span>
             </div>`
            
    currentAudio.play();
    setupLoop(currentAudio);  // Set up the loop for the next audio

})
let prev =document.getElementById("prev");
prev.addEventListener("click",()=>{
    currentAudio.pause();
    console.log(songs_info);
    console.log(songs_img);
    console.log(song_artist);
    let ind;
    let index=songs_arr.indexOf(currentAudio.src);
    if(index==0){ind=song_artist.length-1;}
    else{ind=index-1;}
    currentAudio= new Audio(songs_arr[ind]);
   
    document.querySelector(".songtime").innerHTML="00:00/00:00"
    currentAudio.addEventListener("timeupdate",()=>{
        // console.log(currentAudio.duration,currentAudio.currentTime)
        document.querySelector(".songtime").innerHTML=`
        ${secondsToMinutesSeconds(currentAudio.currentTime)}/
        ${secondsToMinutesSeconds(currentAudio.duration)}`
        document.querySelector(".circle").style.left=(currentAudio.currentTime/currentAudio.duration)*100+"%"; 
     })
     document.querySelector(".seekbar").addEventListener("click",e=>{
        let percent=(e.offsetX/e.target.getBoundingClientRect().width)*100;
       
        document.querySelector(".circle").style.left=percent*100+"%";
        currentAudio.currentTime =((currentAudio.duration) * percent)/100;
        
     })
     let play1=document.getElementById("play-1");
                play1.innerHTML=`  <img src=${songs_img[ind]} width="50px" height="50px" alt="">
            <div class="songinfo" style="display: flex;flex-direction: column;width:150px;text-overflow:ellipsis;padding-left: 10px;">
             <span style="text-overflow:ellipsis">${songs_info[ind]} </span>
             <span>${song_artist[ind]}</span>
             </div>`
            
    currentAudio.play();
    setupLoop(currentAudio);  // Set up the loop for the previous audio


})

document.querySelector(".volume>img").addEventListener("click", e=>{ 
    if(e.target.src.includes("img/volume.svg")){
        e.target.src = e.target.src.replace("img/volume.svg", "img/mute.svg")
        currentAudio.volume = 0;
        document.querySelector(".range").getElementsByTagName("input")[0].value = 0;
    }
    else{
        e.target.src = e.target.src.replace("img/mute.svg", "img/volume.svg")
        currentAudio.volume = .10;
        document.querySelector(".range").getElementsByTagName("input")[0].value = 10;
    }

})
back5.addEventListener("click",()=>{
    // console.log("hello");
    let percent=(currentAudio.currentTime-5)/100;
   currentAudio.currentTime=currentAudio.currentTime-5;
    document.querySelector(".circle").style.left=percent*100+"%";
    })

    forw5.addEventListener("click",()=>{
        // console.log("hello");
        let percent=(currentAudio.currentTime+5)/100;
       currentAudio.currentTime=currentAudio.currentTime+5;
        document.querySelector(".circle").style.left=percent*100+"%";
        })
    document.querySelector(".range").getElementsByTagName("input")[0].addEventListener("change",(e)=>{
    currentAudio.volume=parseInt(e.target.value)/100;
    
})

document.addEventListener("keydown",(e2)=>{

    switch (e2.code) {
        case 'Space':
             if(currentAudio.paused){
             currentAudio.play();
             playButton.src="img/pause.svg";
             }
             else{
             currentAudio.pause();
            playButton.src="img/play-button.png";
             }
             break;
        case 'ArrowRight':
             percent=(currentAudio.currentTime+5)/100;
   currentAudio.currentTime=currentAudio.currentTime+5;
    document.querySelector(".circle").style.left=percent*100+"%";
            break;
        case 'ArrowLeft':
             percent=(currentAudio.currentTime-5)/100;
            currentAudio.currentTime=currentAudio.currentTime-5;
             document.querySelector(".circle").style.left=percent*100+"%";
            break;

}
})

loopbtn.addEventListener("click",()=>{
    loopEnabled=!loopEnabled;
    if(loopEnabled && currentAudio.currentTime!=currentAudio.duration){
      loopable.style.display="block";
      loopdisable.style.display="none";

    }
    else if(loopEnabled &&  currentAudio.currentTime==currentAudio.duration){
            console.log("h")
            loopable.style.display="block";
            loopdisable.style.display="none";
            let index = songs_arr.indexOf(currentAudio.src);
            currentAudio = new Audio(songs_arr[index]);
            currentAudio.play();
            document.querySelector(".songtime").innerHTML="00:00/00:00"
            currentAudio.addEventListener("timeupdate",()=>{
                // console.log(currentAudio.duration,currentAudio.currentTime)
                document.querySelector(".songtime").innerHTML=`
                ${secondsToMinutesSeconds(currentAudio.currentTime)}/
                ${secondsToMinutesSeconds(currentAudio.duration)}`
                document.querySelector(".circle").style.left=(currentAudio.currentTime/currentAudio.duration)*100+"%"; 
             })
             document.querySelector(".seekbar").addEventListener("click",e=>{
                let percent=(e.offsetX/e.target.getBoundingClientRect().width)*100;
               
                document.querySelector(".circle").style.left=percent*100+"%";
                currentAudio.currentTime =((currentAudio.duration) * percent)/100;
                
             })
    }      
    else{
        loopable.style.display="none";
        loopdisable.style.display="block";
    }
})
playButton.addEventListener('click', () => {
    console.log("I am playbutton")
    if (currentAudio) {
        if (isPlaying) {
            currentAudio.pause();
            playButton.src = 'img/play-button.png'; // Change to play image
        } else {
            currentAudio.play();
            playButton.src = 'img/pause.svg'; // Change to pause image
        }
        isPlaying = !isPlaying; // Toggle the isPlaying state
    }
});