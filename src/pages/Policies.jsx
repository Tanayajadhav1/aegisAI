import Sidebar from "../components/Sidebar"

const policies = [
"Block API Keys in prompts",
"Block passwords and authentication tokens",
"Detect confidential document uploads",
"Detect company financial data sharing"
]

export default function Policies(){

return(

<div className="flex">

<Sidebar/>

<div className="flex-1 p-10">

<h2 className="text-3xl text-cyan-400 mb-8">
Security Policies
</h2>

<div className="grid gap-6">

{policies.map((p,i)=>(

<div key={i}
className="bg-slate-900 border border-cyan-500/20 p-6 rounded-xl">

<p className="text-gray-300">
{p}
</p>

</div>

))}

</div>

</div>

</div>

)

}