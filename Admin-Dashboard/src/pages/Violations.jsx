import { useEffect, useState } from "react"
import { collection, onSnapshot } from "firebase/firestore"
import { db } from "../firebase/firebaseConfig"
import Sidebar from "../components/Sidebar"

export default function Violations(){

const [violations,setViolations] = useState([])

useEffect(()=>{

const unsubscribe = onSnapshot(collection(db,"violations"),(snapshot)=>{

const data = snapshot.docs.map(doc=>({
id:doc.id,
...doc.data()
}))

setViolations(data)

})

return ()=>unsubscribe()

},[])

return(

<div className="flex min-h-screen bg-slate-950">

<Sidebar/>

<div className="flex-1 p-10">

<h2 className="text-3xl text-red-400 mb-8 font-bold">
Policy Violations
</h2>

{violations.length === 0 && (
<p className="text-gray-400">
No violations detected yet.
</p>
)}

<div className="grid gap-6">

{violations.map((v)=>(

<div key={v.id} className="bg-slate-900 border border-red-500/30 p-6 rounded-xl shadow">

<p className="text-gray-400 text-sm">
{v.time?.toDate?.()?.toLocaleString?.() || "No time"}
</p>

<h3 className="text-white text-lg mt-2 break-words">
{v.prompt}
</h3>

<p className="text-red-400 font-bold mt-3">
Severity: {v.severity}
</p>

<p className="text-yellow-400 mt-1">
Risk Score: {v.risk_score}
</p>

<p className="text-purple-400 mt-1">
Prompt Injection: {v.prompt_injection ? "Yes" : "No"}
</p>

<p className="text-cyan-400 mt-1">
ML Prediction: {v.ml_prediction}
</p>

{v.keywords?.length > 0 && (

<div className="mt-3">

<p className="text-gray-400 text-sm">
Keywords Detected
</p>

<div className="flex flex-wrap gap-2 mt-1">

{v.keywords.map((k,i)=>(
<span key={i} className="bg-red-600/20 text-red-400 px-2 py-1 rounded text-xs">
{k}
</span>
))}

</div>

</div>

)}

{v.regex_matches?.length > 0 && (

<div className="mt-3">

<p className="text-gray-400 text-sm">
Regex Matches
</p>

<div className="flex flex-wrap gap-2 mt-1">

{v.regex_matches.map((r,i)=>(

<span
key={i}
className="bg-yellow-600/20 text-yellow-400 px-2 py-1 rounded text-xs"
>

{r.type}: {Array.isArray(r.matches) ? r.matches.join(", ") : r.matches}

</span>

))}

</div>

</div>

)}

<p className="text-gray-400 mt-3 text-sm">
Platform: {v.platform}
</p>

<p className="text-gray-400 text-sm">
User: {v.user}
</p>

</div>

))}

</div>

</div>

</div>

)

}