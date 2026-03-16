import Sidebar from "../components/Sidebar"
import Header from "../components/Header"
import MetricCard from "../components/MetricCard"
import RiskChart from "../components/RiskChart"
import ViolationTable from "../components/ViolationTable"
import AlertPanel from "../components/AlertPanel"

import { useEffect, useState } from "react"
import { auth, db } from "../firebase/firebaseConfig"
import { doc, getDoc, collection, onSnapshot } from "firebase/firestore"
import { onAuthStateChanged } from "firebase/auth"

export default function Dashboard(){

const [companyId,setCompanyId] = useState("")
const [violations,setViolations] = useState([])

useEffect(()=>{

const unsubscribeAuth = onAuthStateChanged(auth, async (user)=>{

if(!user) return

// Load company ID
const docRef = doc(db,"companies",user.uid)
const snap = await getDoc(docRef)

if(snap.exists()){
setCompanyId(snap.data().company_id)
}

// Listen to violations
const unsubscribeViolations = onSnapshot(
collection(db,"violations"),
(snapshot)=>{

const data = snapshot.docs.map(doc=>({
id:doc.id,
...doc.data()
}))

setViolations(data)

})

})

return ()=>unsubscribeAuth()

},[])

const highRisk = violations.filter(v=>v.severity==="HIGH").length

return(

<div className="flex">

<Sidebar/>

<div className="flex-1 p-10">

<Header/>

<div className="mb-6 text-cyan-400 text-lg font-semibold">
Company ID: {companyId || "Loading..."}
</div>

<div className="grid grid-cols-4 gap-6 mb-10">

<MetricCard
title="Prompts Monitored"
value={violations.length}
color="text-cyan-400"
/>

<MetricCard
title="Violations"
value={violations.length}
color="text-yellow-400"
/>

<MetricCard
title="High Risk Alerts"
value={highRisk}
color="text-red-400"
/>

<MetricCard
title="Active Users"
value="1"
color="text-green-400"
/>

</div>

<div className="grid grid-cols-2 gap-6 mb-10">

<RiskChart violations={violations}/>

<AlertPanel violations={violations}/>

</div>

<ViolationTable violations={violations}/>

</div>

</div>

)

}