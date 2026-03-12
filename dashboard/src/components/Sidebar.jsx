import { Shield, Activity, AlertTriangle, Settings, Menu } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useState } from "react"

export default function Sidebar(){

const navigate = useNavigate()
const [collapsed,setCollapsed] = useState(false)

return(

<div className={`bg-slate-900 border-r border-cyan-500/20 h-screen p-4 transition-all duration-300 
${collapsed ? "w-20" : "w-64"}`}>

{/* HEADER */}

<div className="flex items-center justify-between mb-10">

{!collapsed && (
<h1 className="text-xl font-bold text-cyan-400">
AEGIS AI
</h1>
)}

<Menu
className="text-cyan-400 cursor-pointer"
onClick={()=>setCollapsed(!collapsed)}
/>

</div>

{/* NAVIGATION */}

<nav className="space-y-6 text-gray-300">

<div
onClick={()=>navigate("/dashboard")}
className="flex items-center gap-3 hover:text-cyan-400 cursor-pointer">

<Shield size={20}/>
{!collapsed && "Dashboard"}

</div>

<div
onClick={()=>navigate("/monitoring")}
className="flex items-center gap-3 hover:text-cyan-400 cursor-pointer">

<Activity size={20}/>
{!collapsed && "AI Monitoring"}

</div>

<div
onClick={()=>navigate("/violations")}
className="flex items-center gap-3 hover:text-cyan-400 cursor-pointer">

<AlertTriangle size={20}/>
{!collapsed && "Violations"}

</div>

<div
onClick={()=>navigate("/policies")}
className="flex items-center gap-3 hover:text-cyan-400 cursor-pointer">

<Settings size={20}/>
{!collapsed && "Policies"}

</div>

</nav>

</div>

)

}