import React, { useContext, useState } from 'react'
import './Sidebar.css'
import {assets} from '../../assets/assets.js'
import { context } from '../../context/context.jsx'
// import e from 'express'

const Sidebar = () => {
    const [extended, setextended] = useState(true)
    const {onsent,previousprompt,setrecentprompt,newchat}=useContext(context)
    const loadprompt=async(prompt)=>{
        setrecentprompt(prompt)
        await onsent(prompt)
    }
  return (
    <div className='sidebar'>
      <div className="top">
         <img onClick={()=>setextended(prev=>!prev)} className='menu' src={assets.menu_icon} alt="" />
        <div onClick={()=>newchat()} className="new-chat">
          <img src={assets.plus_icon} alt="" />  
       {  extended? <p>New Chat</p>:null }
        </div>
       {extended?
        <div className="recent">
            <p className='recent-title'>Recent</p>
            {previousprompt.map((item,index)=>{
               return (
                <div onClick={()=>loadprompt(item)} className="recent-entry">
                <img src={assets.message_icon} alt="" />
                <p>{item.slice(0,18)}...</p>
            </div>
               )
            })}
          
        </div>:null
        }
      </div>
<div className="bottom">
  <div className="bottom-item recent-entry">
     <img src={assets.question_icon} alt="" />
     {extended?<p>Help</p>:null}
  </div>
  <div className="bottom-item recent-entry">
     <img src={assets.history_icon} alt="" />
    {extended?<p>Activity</p>:null}
  </div>
  <div className="bottom-item recent-entry">
     <img src={assets.setting_icon} alt="" />
     {extended?<p>Settings</p>:null}
  </div>
</div>
    </div>
  )
}

export default Sidebar