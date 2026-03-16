export default function ViolationTable({violations}){

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
<th>Platform</th>
<th>Risk</th>
</tr>
</thead>

<tbody>

{violations.map((row)=>{

const time = row.time?.toDate?.()?.toLocaleTimeString?.() || "N/A"

return(

<tr key={row.id} className="border-t border-slate-700">

<td className="py-3">{time}</td>

<td>{row.user || "unknown"}</td>

<td>{row.platform || "unknown"}</td>

<td className={
row.severity==="HIGH"
? "text-red-400"
: row.severity==="MEDIUM"
? "text-yellow-400"
: "text-green-400"
}>
{row.severity}
</td>

</tr>

)

})}

</tbody>

</table>

</div>

)

}