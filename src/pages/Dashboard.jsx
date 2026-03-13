import Sidebar from "../components/Sidebar"
import Header from "../components/Header"
import MetricCard from "../components/MetricCard"
import RiskChart from "../components/RiskChart"
import ViolationTable from "../components/ViolationTable"
import AlertPanel from "../components/AlertPanel"

export default function Dashboard(){

return(

<div className="flex">

<Sidebar/>

<div className="flex-1 p-10">

<Header/>

<div className="grid grid-cols-4 gap-6 mb-10">

<MetricCard title="Prompts Monitored" value="1254" color="text-cyan-400"/>

<MetricCard title="Violations" value="32" color="text-yellow-400"/>

<MetricCard title="High Risk Alerts" value="5" color="text-red-400"/>

<MetricCard title="Active Users" value="14" color="text-green-400"/>

</div>

<div className="grid grid-cols-2 gap-6 mb-10">

<RiskChart/>

<AlertPanel/>

</div>

<ViolationTable/>

</div>

</div>

)

}