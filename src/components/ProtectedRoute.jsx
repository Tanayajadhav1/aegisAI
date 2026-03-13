import { Navigate } from "react-router-dom"
import { auth } from "../firebase/firebaseConfig"

export default function ProtectedRoute({children}){

const user = auth.currentUser

if(!user){

return <Navigate to="/login"/>

}

return children

}