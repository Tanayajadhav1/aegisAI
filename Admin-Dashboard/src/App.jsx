import { BrowserRouter, Routes, Route } from "react-router-dom"

import SplashScreen from "./pages/SplashScreen"
import Login from "./pages/Login"
import Register from "./pages/Register"

import Dashboard from "./pages/Dashboard"
import Monitoring from "./pages/Monitoring"
import Violations from "./pages/Violations"
import Policies from "./pages/Policies"

import ProtectedRoute from "./components/ProtectedRoute"

function App() {

return (

<BrowserRouter>

<Routes>

{/* Public Routes */}

<Route path="/" element={<SplashScreen/>}/>
<Route path="/login" element={<Login/>}/>
<Route path="/register" element={<Register/>}/>

{/* Protected Admin Routes */}

<Route
path="/dashboard"
element={
<ProtectedRoute>
<Dashboard/>
</ProtectedRoute>
}
/>

<Route
path="/monitoring"
element={
<ProtectedRoute>
<Monitoring/>
</ProtectedRoute>
}
/>

<Route
path="/violations"
element={
<ProtectedRoute>
<Violations/>
</ProtectedRoute>
}
/>

<Route
path="/policies"
element={
<ProtectedRoute>
<Policies/>
</ProtectedRoute>
}
/>

</Routes>

</BrowserRouter>

)

}

export default App