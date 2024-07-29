import React, { useContext } from 'react'
import './main.css'
import { assets } from '../../assets/assets'
import { context } from '../../context/context'
import { useState } from 'react'
import Sidebar from '../sidebar/Sidebar'
const Main = () => {
  
  const {onsent,recentprompt,showresult,loading,resultdata,setinput,input}=useContext(context)
  const [extended, setextended] = useState(true)
const display_side=()=>{
  {<Sidebar/>}
}
  return (
    <div className='main'>
      <div className="nav">
        <p className='nav-col'>Gemini
          <img onClick={()=>{ display_side()}}  src={assets.menu_icon} alt="" />
          
        </p>
        {extended?<Sidebar/>:null}
        <img src={assets.user_icon} alt="" />
      </div>
      <div className="main-container">
        {
          !showresult?
          <>
             <div className="greet">
            <p><span>Hello , Dev</span></p>
            <p>How can I help you today ?</p>
        </div>
        <div className="cards">
            <div onClick={()=>{setinput("Suggest some beatiful places on the upcoming trip to Russia")
              onsent("Suggest some beatiful places on the upcoming trip to Russia")
            }} className="card">
                <p>Suggest some beatiful places on the upcoming trip to Russia</p>
                <img src={assets.compass_icon} alt="" />
            </div>
            <div onClick={()=>{ setinput("Briefly summarize this concept:urban planning")
              onsent("Briefly summarize this concept:urban planning")}} className="card">
                <p>Briefly summarize this concept:urban planning</p>
                <img src={assets.bulb_icon} alt="" />
            </div>
            <div onClick={()=>{setinput("Brainstorming team bonding ideas")
              onsent("Brainstorming team bonding ideas")
            }} className="card">
                <p>Brainstorming team bonding ideas</p>
                <img src={assets.message_icon} alt="" />
            </div>
            <div onClick={()=>{setinput("List out all the Data structures")
                onsent("List out all the Data structures")
          }} className="card">
                <p>List out all the Data structures</p>
                <img src={assets.code_icon} alt="" />
            </div>
        </div>
          </>
        : <div className='result'>
          <div className="result-title">
            <img src={assets.user_icon} alt="" />
            <p>{recentprompt}</p>
          </div>
          <div className="result-data">
            <img src={assets.gemini_icon} alt="" />
            {loading
            ? <div className='loader'>
              <hr />
              <hr />
              <hr />
            </div>:
            <p dangerouslySetInnerHTML={{__html:resultdata}}></p>

            }
          </div>

        </div>
        }
       
        <div className="main-bottom">
            <div className="search-box">
                <input onChange={(e)=>setinput(e.target.value)} value={input} type="text" placeholder='Enter a prompt here' name="" id="" />
                <div>
                {/* <input type="file" id="imageInput" accept="image/*"> */}
                <img src={assets.gallery_icon} alt="" />
                {/* </input> */}
                    <img src={assets.mic_icon} alt="" />
                    {input?<img onClick={()=>{onsent()}} src={assets.send_icon} alt="" />:null}
                </div>
            </div>
            <p className='bottom-info'>
            Gemini may display inaccurate info, including about people, so double-check its responses. Your privacy & Gemini Apps
            </p>
        </div>
      </div>
    </div>
  )
}

export default Main