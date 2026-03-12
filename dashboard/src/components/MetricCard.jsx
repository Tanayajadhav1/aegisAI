export default function MetricCard({title,value,color}){

return(

<div className="bg-slate-800/60 backdrop-blur border border-cyan-500/20 p-6 rounded-xl">

<p className="text-gray-400">{title}</p>

<h2 className={`text-3xl font-bold mt-2 ${color}`}>
{value}
</h2>

</div>

)

}