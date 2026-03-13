import { useState } from "react"
import { useNavigate } from "react-router-dom"

import { signInWithEmailAndPassword } from "firebase/auth"
import { auth } from "../firebase/firebaseConfig"

export default function Login(){

const navigate = useNavigate()

const [email,setEmail] = useState("")
const [password,setPassword] = useState("")

async function handleLogin(e){

e.preventDefault()

try{

await signInWithEmailAndPassword(auth,email,password)

navigate("/dashboard")

}
catch(error){

alert("Invalid credentials")

}

}

return(

<div className="min-h-screen flex items-center justify-center bg-slate-950">

<div className="bg-slate-900 border border-cyan-500/30 p-10 rounded-xl w-96">

<h2 className="text-3xl font-bold text-cyan-400 mb-6 text-center">
Admin Login
</h2>

<form onSubmit={handleLogin} className="space-y-4">

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
Login
</button>

</form>

{/* REGISTER LINK */}

<p className="text-gray-400 text-sm mt-5 text-center">
Don't have an account?{" "}
<span
onClick={()=>navigate("/register")}
className="text-cyan-400 cursor-pointer hover:underline"
>
Register
</span>
</p>

</div>

</div>

)

}