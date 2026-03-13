import { useEffect, useState } from "react"

const logs = [
"User emp21 sending prompt to ChatGPT",
"Scanning prompt for sensitive data...",
"Prompt classified as SAFE",
"User emp02 sending prompt to Gemini",
"WARNING: Possible password detected",
"Blocking prompt transmission",
"ALERT: API Key pattern detected",
"Security policy triggered",
"Prompt blocked successfully",
"User emp15 sending prompt to ChatGPT"
]

export default function AttackFeed(){

const [feed,setFeed] = useState([])

useEffect(()=>{

let index = 0

const interval = setInterval(()=>{

setFeed(prev => [...prev, logs[index % logs.length]])

index++

},1500)

return ()=>clearInterval(interval)

},[])

return(

<div className="bg-black border border-green-500/40 p-6 rounded-xl h-80 overflow-hidden">

<h3 className="text-green-400 mb-4 font-mono">
LIVE AI SECURITY FEED
</h3>

<div className="text-green-300 font-mono text-sm space-y-1 overflow-y-auto h-64">

{feed.map((log,i)=>(
<p key={i}>{" > "}{log}</p>
))}

</div>

</div>

)

}