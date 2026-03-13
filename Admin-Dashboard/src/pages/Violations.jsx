import Sidebar from "../components/Sidebar"

const violations = [
{
time:"10:31",
user:"emp02",
type:"API Key Leak",
severity:"High"
},
{
time:"11:02",
user:"emp14",
type:"Confidential Document",
severity:"Medium"
},
{
time:"11:25",
user:"emp07",
type:"Password Detection",
severity:"High"
}
]

export default function Violations(){

return(

<div className="flex">

<Sidebar/>

<div className="flex-1 p-10">

<h2 className="text-3xl text-red-400 mb-8">
Policy Violations
</h2>

<div className="grid gap-6">

{violations.map((v,i)=>(

<div key={i} className="bg-slate-900 border border-red-500/30 p-6 rounded-xl">

<p className="text-gray-400">{v.time}</p>

<h3 className="text-xl text-white mt-2">
{v.type}
</h3>

<p className="text-gray-300 mt-2">
User: {v.user}
</p>

<p className="text-red-400 font-bold mt-2">
Severity: {v.severity}
</p>

</div>

))}

</div>

</div>

</div>

)

}