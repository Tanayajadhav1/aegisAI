export default function AlertPanel(){

return(

<div className="bg-slate-800/60 border border-red-500/40 p-6 rounded-xl">

<h3 className="text-red-400 text-lg mb-4">
Live Security Alerts
</h3>

<ul className="space-y-2 text-gray-300">

<li>⚠ Attempt to send API key to ChatGPT</li>
<li>⚠ Confidential file detected in prompt</li>
<li>⚠ Password pattern detected</li>

</ul>

</div>

)

}