import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts"

const data = [
  { name: "Safe", value: 70 },
  { name: "Medium", value: 20 },
  { name: "High", value: 10 }
]

const COLORS = ["#22c55e", "#facc15", "#ef4444"]

export default function RiskChart(){

return(

<div className="bg-slate-800/60 border border-cyan-500/20 p-6 rounded-xl">

<h3 className="text-lg mb-4 text-gray-300">
Risk Distribution
</h3>

<div className="flex justify-center">

<PieChart width={350} height={250}>

<Pie
data={data}
dataKey="value"
nameKey="name"
cx="50%"
cy="50%"
outerRadius={80}
label
>

{data.map((entry,index)=>(
<Cell key={index} fill={COLORS[index]}/>
))}

</Pie>

<Tooltip/>

<Legend
verticalAlign="bottom"
iconType="circle"
wrapperStyle={{ color: "#d1d5db" }}
/>

</PieChart>

</div>

</div>

)

}