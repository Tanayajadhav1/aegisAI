import { signOut } from "firebase/auth"
import { auth } from "../firebase/firebaseConfig"
import { useNavigate } from "react-router-dom"

export default function Header(){

const navigate = useNavigate()

function logout(){

signOut(auth)

navigate("/login")

}

return(

<div className="flex justify-between items-center mb-8">

<h2 className="text-3xl font-bold text-cyan-400">
Admin Dashboard
</h2>


<div className="text-gray-400">
System Status: <span className="text-green-400">Active</span>
</div>

<button
onClick={logout}
className="bg-red-500 px-4 py-2 rounded"
>
Logout
</button>

</div>

)

}