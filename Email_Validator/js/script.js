
submitBtn.addEventListener("click",async(e)=>{
    e.preventDefault();

    let email=document.getElementById("username").value
   let key="ema_live_eqhLBn5JiPs4rWzkmYLoZ6rxHSxpGtPcbpaqV8Fc"
   resultCont.innerHTML = `<img width="123" src="img/loading.svg" alt="">`

    let url = `https://api.emailvalidation.io/v1/info?apikey=${key}&email=${email}`
    try {
        let res = await fetch(url);
        if (!res.ok) {
            throw new Error('Network response was not ok');
        }
        let result = await res.json();
        let str = ``;
        for (let key of Object.keys(result)) {
            if (result[key] !== "" && result[key] !== " ") { 
                str += `<div>${key}: ${result[key]}</div>`;
            }
        }
        resultCont.innerHTML = str;
    } catch (error) {
        resultCont.innerHTML = `<img src="img/no-internet-connection.svg" width="100px" height="100px">
       <h1> NO INTERNET CONNECTION</h1><h2>PLEASE CHECK YOUR CONNECTION</h2>`;
    }
})
let result={
    
        "tag": "",
        "free": true,
        "role": false,
        "user": "prasanna.000019",
        "email": "prasanna.000019@gmail.com",
        "score": 0.64,
        "state": "deliverable",
        "domain": "gmail.com",
        "reason": "valid_mailbox",
        "mx_found": true,
        "catch_all": null,
        "disposable": false,
        "smtp_check": true,
        "did_you_mean": "",
        "format_valid": true
      
    }
 