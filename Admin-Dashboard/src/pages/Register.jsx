import { useState } from "react"
import { useNavigate } from "react-router-dom"

import { auth } from "../firebase/firebaseConfig"
import { createUserWithEmailAndPassword } from "firebase/auth"

export default function Register(){

const navigate = useNavigate()

const [email,setEmail] = useState("")
const [password,setPassword] = useState("")

async function handleRegister(e){

e.preventDefault()

try{

await createUserWithEmailAndPassword(auth,email,password)

alert("Admin Registered Successfully")

navigate("/login")

}
catch(error){

alert(error.message)

}

}

return(

<div className="min-h-screen flex items-center justify-center bg-slate-950">

<div className="bg-slate-900 border border-cyan-500/30 p-10 rounded-xl w-96">

<h2 className="text-3xl font-bold text-cyan-400 mb-6 text-center">
Admin Registration
</h2>

<form onSubmit={handleRegister} className="space-y-4">

<input
type="email"
placeholder="Admin Email"
value={email}
onChange={(e)=>setEmail(e.target.value)}
className="w-full p-3 rounded bg-slate-800 border border-slate-700 text-white"
/>

<input
type="password"
placeholder="Password"
value={password}
onChange={(e)=>setPassword(e.target.value)}
className="w-full p-3 rounded bg-slate-800 border border-slate-700 text-white"
/>

<button
className="w-full bg-cyan-500 hover:bg-cyan-600 py-3 rounded font-bold"
>
Register
</button>

</form>

</div>

</div>

)

}