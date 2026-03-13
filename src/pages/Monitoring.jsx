import Sidebar from "../components/Sidebar"
import AttackFeed from "../components/AttackFeed"

const sessions = [
{
user:"emp21",
tool:"ChatGPT",
action:"Generated marketing email",
time:"10:32",
status:"Safe"
},
{
user:"emp15",
tool:"Gemini",
action:"Uploaded internal sales data",
time:"10:34",
status:"Medium Risk"
},
{
user:"emp02",
tool:"ChatGPT",
action:"Attempted to share API key",
time:"10:36",
status:"Blocked"
},
{
user:"emp07",
tool:"Claude",
action:"Asked for code debugging",
time:"10:40",
status:"Safe"
}
]

export default function Monitoring(){

return(

<div className="flex">

<Sidebar/>

<div className="flex-1 p-10">

<h2 className="text-3xl text-cyan-400 mb-8">
AI Prompt Monitoring
</h2>

<div className="grid grid-cols-2 gap-8">

{/* ATTACK FEED */}

<AttackFeed/>

{/* ACTIVE SESSIONS */}

<div className="bg-slate-900 border border-cyan-500/20 p-6 rounded-xl">

<h3 className="text-lg text-gray-300 mb-4">
Active AI Sessions
</h3>

<table className="w-full text-left text-sm">

<thead className="text-gray-400 border-b border-slate-700">
<tr>
<th className="py-2">User</th>
<th>Tool</th>
<th>Action</th>
<th>Time</th>
<th>Status</th>
</tr>
</thead>

<tbody>

{sessions.map((s,i)=>(

<tr key={i} className="border-b border-slate-800">

<td className="py-2">{s.user}</td>
<td>{s.tool}</td>
<td>{s.action}</td>
<td>{s.time}</td>

<td className={
s.status==="Safe"
? "text-green-400"
: s.status==="Medium Risk"
? "text-yellow-400"
: "text-red-400"
}>
{s.status}
</td>

</tr>

))}

</tbody>

</table>

</div>

</div>

</div>

</div>

)

} 