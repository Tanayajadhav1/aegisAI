const data = [
{
time:"10:32",
user:"emp21",
tool:"ChatGPT",
risk:"High"
},
{
time:"10:40",
user:"emp08",
tool:"Gemini",
risk:"Medium"
}
]

export default function ViolationTable(){

return(

<div className="bg-slate-800/60 border border-cyan-500/20 p-6 rounded-xl">

<h3 className="text-lg mb-4 text-gray-300">
Recent Violations
</h3>

<table className="w-full text-left">

<thead className="text-gray-400">
<tr>
<th>Time</th>
<th>User</th>
<th>AI Tool</th>
<th>Risk</th>
</tr>
</thead>

<tbody>

{data.map((row,i)=>(

<tr key={i} className="border-t border-slate-700">

<td className="py-3">{row.time}</td>
<td>{row.user}</td>
<td>{row.tool}</td>
<td className="text-red-400">{row.risk}</td>

</tr>

))}

</tbody>

</table>

</div>

)

}