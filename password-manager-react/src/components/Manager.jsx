import React from 'react'
import { useRef, useState, useEffect } from 'react'
import { ToastContainer,toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css';
import { v4 as uuidv4 } from 'uuid';
const Manager = () => {
    const ref = useRef()
    const passref = useRef()
    const [form, setform] = useState({ site: "", username: "", password: "" })
    const [passArray, setpassArray] = useState([])
    useEffect(() => {
        let passwords = localStorage.getItem("passwords");
        if (passwords) {
            setpassArray(JSON.parse(passwords))
        }
    }, [])
    const copytext=(text) => {
        toast('Copied to clipboard!', {
            position: "top-right",
            autoClose: 5000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
            theme: "light",
        });  
      navigator.clipboard.writeText(text)
    }
    const editpassword=(id) => {
      setform(passArray.filter(i=>i.id===id)[0])
      setpassArray(passArray.filter(item=>item.id!==id))
      toast('PASSWORD EDITED SUCCESSFULY', {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "light",
    });  
     }
    const savepassword = () => {
      if(form.site.length>3 && form.username.length>3 && form.password.length>3){

        setpassArray([...passArray, {...form,id:uuidv4()}])
        localStorage.setItem("passwords", JSON.stringify([...passArray, {...form,id:uuidv4()}]))
        console.log([...passArray, form])
        setform({site:"",username:"",password:""})
        toast('PASSWORD SAVED SUCCESSFULY!!!', {
            position: "top-right",
            autoClose: 5000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
            theme: "light",
        });  
    }
    else{
        toast('ERROR: PASSWORD NOT SAVED!!!')
    }
    }
    const deletepassword=(id) => {
        let c=confirm("Do you really want to delete this password ?")
        if(c){

            setpassArray(passArray.filter(item=>item.id!==id))
            localStorage.setItem("passwords",JSON.stringify(passArray.filter(item=>item.id!==id)))    
            toast('PASSWORD DELETED', {
                position: "top-right",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
                theme: "light",
            });  
        }
}
    
    const handlechange = (e) => {
        setform({ ...form, [e.target.name]: e.target.value })
    }


    const showpassword = () => {
        passref.current.type = 'text'
        if (ref.current.src.includes("eyecross.png")) {
            ref.current.src = "eye.png";
            passref.current.type = 'password'
        }
        else {
            ref.current.src = "eyecross.png";
            passref.current.type = 'text'
        }
    }

    return (
        <>
             <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="light"
            />
            <div className="absolute inset-0 -z-10 h-full w-full bg-white bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:6rem_4rem]"><div className="absolute bottom-0 left-0 right-0 top-0 bg-[radial-gradient(circle_500px_at_50%_200px,#C9EBFF,transparent)]">
                jddjjdjd
            </div></div>
            <div className="p-2 md:p-0 md:mycontainer ">
                <h1 className='text-4xl font-bold text-center'>  <span className='text-green-500'> &lt; </span>
                    Pass
                    <span className='text-green-500'>OP/ &gt; </span></h1>
                <p className='text-green-900 text-lg text-center'>Your own password manager</p>
                <div className="flex flex-col  p-4 text-black gap-5 items-center">
                    <input value={form.site} onChange={handlechange} placeholder='Enter website URL' className='rounded-full border border-green-500 w-full  p-4 py-1' type="text" name="site" id="" required />
                    <div className="flex md:flex-row w-full justify-between gap-8">
                        <input value={form.username} onChange={handlechange} placeholder='Enter Username' className='rounded-full border border-green-500 w-full p-4 py-1' type="text" name="username" id="" required />
                        <div className="relative">

                            <input ref={passref} value={form.password} onChange={handlechange} placeholder='Enter Password' className='rounded-full border border-green-500 w-full p-4 py-1' type="password" name="password" id="" required />
                            <span className='absolute right-0 top-[2px] cursor-pointer' onClick={showpassword}>
                                <img ref={ref} className='p-1' width={30} src="eye.png" alt="" />
                            </span>
                        </div>
                    </div>
                    <button onClick={savepassword} className='flex justify-center items-center gap-2 bg-green-500 rounded-full px-2 py-2 w-fit 
                    hover:bg-green-300'>
                        <lord-icon
                            // style={{ "width": "25px", "height": "25px", "paddingTop": "3px", "paddingLeft": "3px" }}
                            src="https://cdn.lordicon.com/jgnvfzqg.json"
                            trigger="hover" >
                        </lord-icon>
                        Add password </button>
                </div>
                <div className="passwords">
                    <h2 className='font-bold text-2xl py-4'>Your passwords:</h2>
                    {passArray.length === 0 && <div>NO PASSWORDS TO SHOW</div>}
                    {passArray.length !== 0 && <table className="table-auto w-full rounded-md overflow-hidden mb-5 max-w-[100vw]
                    text-ellipsis">
                        <thead className=' bg-green-800 text-white'>
                            <tr>
                                <th className='py-2'>SITE</th>
                                <th className='py-2'>USERNAME</th>
                                <th className='py-2'>PASSWORDS</th>
                                <th className='py-2'>ACTIONS</th>
                            </tr>
                        </thead>
                        <tbody className='bg-green-100'>
                            {passArray.map((item, index) => {
                                return <tr key={index}>
                                    <td className='border border-white py-2 text-center w-32'>
                                        <div className="flex items-center justify-center"> 
                                        <a href={item.site} target='_blank'>{item.site}</a>
                                      <div className='size-7 cursor-pointer' onClick={()=>copytext(item.site)} >
                                        <lord-icon
                                            style={{ "width": "25px", "height": "25px", "paddingTop": "3px", "paddingLeft": "3px" }}
                                            src="https://cdn.lordicon.com/iykgtsbt.json"
                                            trigger="hover" >
                                        </lord-icon>
                                                </div> 
                                                </div> 
                                    </td>
                                    <td className='border border-white py-2 text-center  '>
                                   <div className="flex items-center justify-center">
                                       <span> {item.username}</span>
                                    <div className='size-7 cursor-pointer'  onClick={()=>copytext(item.username)}>
                                        <lord-icon
                                            style={{ "width": "25px", "height": "25px", "paddingTop": "3px", "paddingLeft": "3px" }}
                                            src="https://cdn.lordicon.com/iykgtsbt.json"
                                            trigger="hover" >
                                        </lord-icon>
                                                </div> 
                                                </div> 
                                    </td>
                                    <td className='  border border-white py-2 text-center '>
                                      <div className="flex items-center justify-end">
                                       <span>{'*'.repeat(item.password.length)}  </span>
                                    <div className='size-7 cursor-pointer'  onClick={()=>copytext(item.password)}>
                                        <lord-icon
                                            style={{ "width": "25px", "height": "25px", "paddingTop": "3px", "paddingLeft": "3px" }}
                                            src="https://cdn.lordicon.com/iykgtsbt.json"
                                            trigger="hover" >
                                        </lord-icon>
                                                </div> 
                                                </div> 
                                    </td>
                                    <td className='justify-center py-2 border border-white text-center'>
                                      <span className='cursor-pointer mx-1' onClick={()=>{editpassword(item.id)}}>
                                      <lord-icon
                                                src="https://cdn.lordicon.com/gwlusjdu.json"
                                                trigger="hover"
                                                style={{"width":"25px", "height":"25px"}}>
                                            </lord-icon>
                                      </span>
                                      <span className='cursor-pointer mx-1' onClick={()=>{deletepassword(item.id)}} >
                                      <lord-icon
                                                src="https://cdn.lordicon.com/skkahier.json"
                                                trigger="hover"
                                                style={{"width":"25px", "height":"25px"}}>
                                            </lord-icon>
                                      </span>
                                    </td>
                                </tr>
                            })}
                        </tbody>
                    </table>}
                </div>
            </div>
        </>
    )
}

export default Manager