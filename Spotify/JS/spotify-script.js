let songs;
let currfolder;
let loopEnabled=false;
let autoplayEnabled = true;
const back5=document.getElementById("back-5");
const forw5=document.getElementById("forw-5");
const autoplayButton = document.getElementById("autoplay");
const autoplayEnabledSvg = document.getElementById("autoplay-enabled");
const autoplayDisabledSvg = document.getElementById("autoplay-disabled");
const loopbtn=document.getElementById("loop");
const loopEnabledsvg=document.getElementById("LoopEnabled");
const loopDisabledsvg=document.getElementById("LoopDisabled");
const shuffleButton = document.getElementById('shuffleButton');

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
function shuffleArray(array) {
    for (let i = array.length - 1; i >= 0; i--) {
        const j = Math.floor(Math.random() * (i));
        [array[i], array[j]] = [array[j], array[i]];
    }
}
async function getsongs(folder){
    currfolder=folder;
    // console.log(folder+"h77");
    let a=await fetch(`http://192.168.172.142:3000/${folder}/`)
    // let d1=await fetch('https://saavn.dev/api/search/songs?query=Adiyogi');
    // let response1= await d1.json();
    // console.log(response1);
    let response = await a.text();
    console.log(response);
    let div=document.createElement("div");
    div.innerHTML=response;
     songs=[];
    let as=div.getElementsByTagName("a")
   for (let index = 0; index < as.length; index++) {
    const element = as[index];
    if(element.href.endsWith(".mp3")){
        songs.push(element.href.split(`/${folder}/`)[1]);
    }
    
   }
  
   let songUL=document.querySelector(".songList").getElementsByTagName("ul")[0]
   songUL.innerHTML=""

    shuffleArray(songs);
//    for(let i=0;i<songs.length;i++){
//    songs[i]= songs[i].replace(".mp3","");
//    }
   for (const song of songs) {
    console.log(songs)
       songUL.innerHTML=songUL.innerHTML+`<li> 
      
                           <img class="invert" src="img/music.svg" alt="">
                         <div class="info">
                           <div> ${song.replaceAll("%20"," ")}</div>
                           <div>Artist</div>
                         </div>
                         <div class="playnow">
                           <span>Play now</span>
                         <img class="invert" src="img/play.svg" alt="">
                       </div></li>`;
   }
   Array.from(document.querySelector(".songList").getElementsByTagName("li")).forEach(e => {
       e.addEventListener("click", element => {
           console.log(e.querySelector(".info").firstElementChild.innerHTML)
           playMusic(e.querySelector(".info").firstElementChild.innerHTML.trim())

       })
   })

   return songs
}

let df1=true;
shuffleButton.addEventListener("click",()=>{
    console.log("hey hi 779")
    shuffleArray(songs);
    let songUL=document.querySelector(".songList").getElementsByTagName("ul")[0]
    songUL.innerHTML=""

    for (const song of songs) {
        songUL.innerHTML=songUL.innerHTML+`<li> 
       
                            <img class="invert" src="img/music.svg" alt="">
                          <div class="info">
                            <div> ${song.replaceAll("%20","")}</div>
                            <div>Artist</div>
                          </div>
                          <div class="playnow">
                            <span>Play now</span>
                          <img class="invert" src="img/play.svg" alt="">
                        </div></li>`;
    }
    Array.from(document.querySelector(".songList").getElementsByTagName("li")).forEach(e => {
        e.addEventListener("click", element => {
            console.log(e.querySelector(".info").firstElementChild.innerHTML)
            playMusic(e.querySelector(".info").firstElementChild.innerHTML.trim())
 
        })
    })

})

let currentsong= new Audio()
const playMusic=(track,pause=false)=>{
    // let audio = new Audio("/songs/"+track)
    currentsong.src=`/${currfolder}/`+track;
    if(!pause){
        currentsong.play();
         play.src="img/pause.svg"
    }
    currentsong.play()
    // audio.play();
    // document.querySelector(".icon12").innerHTML=`<img src="/${currfolder}/pathaan.jpg" class="invert" style="width:60px;height:65px" >`
    document.querySelector(".songinfo").innerHTML=decodeURI(track);
    document.querySelector(".songtime").innerHTML="00:00/00:00"
}
async function displayAlbums(){
    let a=await fetch(`http://192.168.172.142:3000/songs/`)
    let response = await a.text();
    let div=document.createElement("div");
    div.innerHTML=response;
    let anchors=div.getElementsByTagName("a");
    let cardcontainer=document.querySelector(".cardcontainer")
   let array= Array.from(anchors)
    for (let index = 0; index < array.length; index++) {
        const e = array[index];
    
    
        if(e.href.includes("/songs")){
            let folder=e.href.split("/").slice(-2)[0];
            console.log(folder);
            let a=await fetch(`http://192.168.172.142:3000/songs/${folder}/info.json`)
            let response = await a.json();
            console.log(response)
            cardcontainer.innerHTML=cardcontainer.innerHTML+`
            <div data-folder="${folder}"  class="card">
                        <div class="play">
                            <svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
                                <!-- Define the circle with green background -->
                                <circle cx="32" cy="32" r="30" fill="#1fdf64" />
                                
                                <!-- Define the black triangle inside the circle, rotated 90 degrees to the right -->
                                <polygon points="32,12 13,52 49,52" fill="black" transform="rotate(90 32 32)" />
                              </svg>     
                        </div>
                    <img src="/songs/${folder}/cover.jpg"
                     alt="">
                    <h2>${response.title}</h2>
                    <p>${response.description}</p>
                   
                    </div>`
        }
    }
    Array.from(document.getElementsByClassName("card")).forEach(e=>{
        e.addEventListener("click", async item=>{
            songs=await getsongs(`songs/${item.currentTarget.dataset.folder}`)
           playMusic(songs[0])
        })
    })
}
async function main(){
     await getsongs("songs/album-1");
    
   playMusic(songs[0],true)
   await displayAlbums()
    // return songs
    play.addEventListener("click",()=>{
        if(currentsong.paused){
            currentsong.play();
            play.src="img/pause.svg"
        }
        else{
            currentsong.pause();
            play.src="img/play.svg";
        }
    })
    currentsong.addEventListener("timeupdate",()=>{
        // console.log(currentsong.currentTime,currentsong.duration)
       document.querySelector(".songtime").innerHTML=`
       ${secondsToMinutesSeconds(currentsong.currentTime)}/
       ${secondsToMinutesSeconds(currentsong.duration)}`
       document.querySelector(".circle").style.left=(currentsong.currentTime/currentsong.duration)*100+"%"; 
    })
    currentsong.addEventListener("ended", () => {
        if(loopEnabled){
            let index = songs.indexOf(currentsong.src.split("/").slice(-1)[0]);
            playMusic(songs[index]);

        } 
    
       else if (autoplayEnabled && !loopEnabled) {

        let index = songs.indexOf(currentsong.src.split("/").slice(-1)[0]);
        if ((index + 1) < songs.length) {
            playMusic(songs[index + 1]);
        } else {
            playMusic(songs[0]);
        }
    }
    // if(loopEnabled){}
    
    else{
        play.src="img/play.svg";
    }
    });
 document.querySelector(".seekbar").addEventListener("click",e=>{
    let percent=(e.offsetX/e.target.getBoundingClientRect().width)*100;
   
    document.querySelector(".circle").style.left=percent*100+"%";
    currentsong.currentTime =((currentsong.duration) * percent)/100;
    
 })
 document.querySelector(".hamburger").addEventListener("click",()=>{
    document.querySelector(".left").style.left="0";
 })
 document.querySelector(".close").addEventListener("click",()=>{
    document.querySelector(".left").style.left="-120%";
 })
 previous.addEventListener("click", () => {
    currentsong.pause()
  
    console.log("Previous clicked")
    let index = songs.indexOf(currentsong.src.split("/").slice(-1)[0])
    if ((index - 1) >= 0) {
        playMusic(songs[index - 1])
    }
    else if((index-1)==-1){playMusic(songs[songs.length-1])}
})
// Add an event listener to next
next.addEventListener("click", () => {
    currentsong.pause()
    console.log("Next clicked")

    let index = songs.indexOf(currentsong.src.split("/").slice(-1)[0])
    if ((index + 1) < songs.length) {
        playMusic(songs[index + 1]);
    }
    if(index+1==songs.length){
        playMusic(songs[0]);
    }
})
back5.addEventListener("click",()=>{
    // console.log("hello");
    let percent=(currentsong.currentTime-5)/100;
   currentsong.currentTime=currentsong.currentTime-5;
    document.querySelector(".circle").style.left=percent*100+"%";
    })

    forw5.addEventListener("click",()=>{
        // console.log("hello");
        let percent=(currentsong.currentTime+5)/100;
       currentsong.currentTime=currentsong.currentTime+5;
        document.querySelector(".circle").style.left=percent*100+"%";
        })
    document.querySelector(".range").getElementsByTagName("input")[0].addEventListener("change",(e)=>{
    currentsong.volume=parseInt(e.target.value)/100;
    
})
document.addEventListener("keydown",(e2)=>{

        switch (e2.code) {
            case 'Space':
                 if(currentsong.paused){
                 currentsong.play();
                 play.src="img/pause.svg";
                 }
                 else{
                 currentsong.pause();
                play.src="img/play.svg";
                 }
                 break;
            case 'ArrowRight':
                 percent=(currentsong.currentTime+5)/100;
       currentsong.currentTime=currentsong.currentTime+5;
        document.querySelector(".circle").style.left=percent*100+"%";
                break;
            case 'ArrowLeft':
                 percent=(currentsong.currentTime-5)/100;
                currentsong.currentTime=currentsong.currentTime-5;
                 document.querySelector(".circle").style.left=percent*100+"%";
                break;

    }
})
const volumeRange = document.querySelector(".range").getElementsByTagName("input")[0];
    const volumeIcon = document.querySelector(".volume>img");

    volumeRange.addEventListener("change", (e) => {
        const volume = parseInt(e.target.value) / 100;
        currentsong.volume = volume;
        
        if (volume === 0) {
            volumeIcon.src = "img/mute.svg";
        } else {
            volumeIcon.src = "img/volume.svg";
        }
    });

document.querySelector(".volume>img").addEventListener("click", e=>{ 
    if(e.target.src.includes("img/volume.svg")){
        e.target.src = e.target.src.replace("img/volume.svg", "img/mute.svg")
        currentsong.volume = 0;
        document.querySelector(".range").getElementsByTagName("input")[0].value = 0;
    }
    else{
        e.target.src = e.target.src.replace("img/mute.svg", "img/volume.svg")
        currentsong.volume = .10;
        document.querySelector(".range").getElementsByTagName("input")[0].value = 10;
    }

})
autoplayButton.addEventListener("click", () => {
    autoplayEnabled = !autoplayEnabled;
    
    // Toggle SVG visibility
    if(autoplayEnabled && currentsong.currentTime!=currentsong.duration){
        autoplayEnabledSvg.style.display = "block";
        autoplayDisabledSvg.style.display = "none";
    }
   else if (autoplayEnabled && currentsong.currentTime==currentsong.duration) {
        
        let index = songs.indexOf(currentsong.src.split("/").slice(-1)[0]);
        if ((index + 1) < songs.length) {
            playMusic(songs[index + 1]);
        } else {
            playMusic(songs[0]);
        }

    } else {
        autoplayEnabledSvg.style.display = "none";
        autoplayDisabledSvg.style.display = "block";
    }
});

// Get all loop buttons
loopbtn.addEventListener("click",()=>{
    loopEnabled=!loopEnabled;
    if(loopEnabled && currentsong.currentTime!=currentsong.duration){
       loopEnabledsvg.style.display="block";
       loopDisabledsvg.style.display="none";

    }
    else if(loopEnabled &&  currentsong.currentTime==currentsong.duration){
            
            loopEnabledsvg.style.display="block";
            loopDisabledsvg.style.display="none";
            let index = songs.indexOf(currentsong.src.split("/").slice(-1)[0]);
            playMusic(songs[index]);
    }
    else{
        loopEnabledsvg.style.display="none";
        loopDisabledsvg.style.display="block";
    }
})

}

main()