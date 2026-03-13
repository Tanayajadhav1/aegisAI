import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import CyberBackground from "../components/CyberBackground"
import CyberGrid from "../components/CyberGrid"
import FirewallScanner from "../components/FirewallScanner"
import { Typewriter } from "react-simple-typewriter"

export default function SplashScreen(){

const navigate = useNavigate()

return(

<div className="relative min-h-screen w-screen overflow-hidden grid place-items-center">

<CyberGrid/>
<CyberBackground/>
<FirewallScanner/>

{/* MAIN CONTENT */}
<div className="relative z-10 w-full max-w-4xl text-center px-6">

<motion.h1
initial={{opacity:0,y:-60}}
animate={{opacity:1,y:0}}
transition={{duration:1}}
className="text-6xl md:text-7xl font-bold text-cyan-400 tracking-widest"
>
AEGIS AI FIREWALL
</motion.h1>

<p className="mt-6 text-xl md:text-2xl text-gray-300">

<Typewriter
words={[
"Real-Time AI Prompt Monitoring",
"Sensitive Data Leak Prevention",
"Enterprise AI Governance"
]}
loop
cursor
cursorStyle="_"
typeSpeed={70}
deleteSpeed={50}
/>

</p>

{/* FEATURES */}
<div className="grid md:grid-cols-2 grid-cols-1 gap-8 mt-16">

<motion.div
initial={{opacity:0,y:40}}
animate={{opacity:1,y:0}}
transition={{delay:0.3}}
className="bg-slate-800/60 backdrop-blur-xl border border-cyan-500/40 p-6 rounded-xl shadow-lg shadow-cyan-500/20 hover:scale-105 transition-all duration-300"
>
Real-time AI prompt monitoring
</motion.div>

<motion.div
initial={{opacity:0,y:40}}
animate={{opacity:1,y:0}}
transition={{delay:0.5}}
className="bg-slate-800/60 backdrop-blur-xl border border-cyan-500/40 p-6 rounded-xl shadow-lg shadow-cyan-500/20 hover:scale-105 transition-all duration-300"
>
Sensitive data detection
</motion.div>

<motion.div
initial={{opacity:0,y:40}}
animate={{opacity:1,y:0}}
transition={{delay:0.7}}
className="bg-slate-800/60 backdrop-blur-xl border border-cyan-500/40 p-6 rounded-xl shadow-lg shadow-cyan-500/20 hover:scale-105 transition-all duration-300"
>
Enterprise policy enforcement
</motion.div>

<motion.div
initial={{opacity:0,y:40}}
animate={{opacity:1,y:0}}
transition={{delay:0.9}}
className="bg-slate-800/60 backdrop-blur-xl border border-cyan-500/40 p-6 rounded-xl shadow-lg shadow-cyan-500/20 hover:scale-105 transition-all duration-300"
>
Security analytics dashboard
</motion.div>

</div>

<button
onClick={()=>navigate("/login")}
className="mt-16 px-12 py-4 bg-cyan-500 hover:bg-cyan-600 rounded-lg text-lg font-bold shadow-lg shadow-cyan-500/40 transition-all duration-300 hover:scale-105"
>
Get Started
</button>

</div>

</div>

)

}