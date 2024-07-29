
let text_output=document.getElementById("out");
let text_output_2=document.getElementById("out2");
let text_output_3=document.getElementById("out3")
async function a1(){
    text_output.innerHTML=''
    let inp=document.getElementById("inp").value;
    console.log(inp)
    let url=`https://bhagavadgitaapi.in/chapter/${inp}/`
    let response= await fetch(url)
    let res_json=await response.json();
    // console.log(res_json);
    text_output.innerHTML=`
    ${res_json.name}
    <br><br><br>${res_json.summary.hi} <br><br> ${res_json.summary.en}` 

}
async function a2(){
    text_output_2.innerHTML=''
    let url= `https://bhagavadgitaapi.in/chapters/`
    let response=await fetch(url);
    let res_json=await response.json();
    // console.log(res_json)
    // console.log(res_json.length)
    for(let i=0;i<res_json.length;i++){
        text_output_2.innerHTML+=`<div class="card">
        <span>CHAPTER:${res_json[i].chapter_number}</span>
       <span> NAME:${res_json[i].name}(${res_json[i].translation})</span>
       <p>SUMMARY: ${res_json[i].summary.en}</p>
       <p>${res_json[i].summary.hi}</p>
       </div>`
    }
}
async function a3(){
    text_output_3.innerHTML=''
    let ch=document.getElementById("chap").value
    let sl=document.getElementById("shlok").value
    let url=`https://bhagavadgitaapi.in/slok/${ch}/${sl}/`
    // let url=`https://bhagavadgitaapi.in/slok/16/1/`
    let response=await fetch(url)
    let res_json=await response.json()
    // console.log(res_json);
    text_output_3.innerHTML=`
    <h1>SHLOK:${res_json["slok"]}</h1>
    <h2>TRANSLITERATION:${res_json["transliteration"]}</h2>
    <div class="shloks">
    <h1>AUTHOR:"A.C. Bhaktivedanta Swami Prabhupada</h1>
   <article>${res_json["prabhu"]["ec"]}</article>
    <h1>AUTHOR:SWAMI SIVANANDA</h1>
    <article>${res_json["siva"]["ec"]}</article>
     <h1>AUTHOR:SWAMI  CHINMAYANANDA</h1>
    <article>${res_json["chinmay"]["hc"]}</article>
     <h1>AUTHOR:Swami Ramsukhdas</h1>
    <article>${res_json["rams"]["hc"]}</article>
    </div>
    `
    
}
