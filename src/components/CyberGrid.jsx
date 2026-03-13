export default function CyberGrid(){

return(

<div className="absolute inset-0 -z-20">

<div
className="w-full h-full opacity-20"
style={{
backgroundImage: `
linear-gradient(rgba(0,255,255,0.2) 1px, transparent 1px),
linear-gradient(90deg, rgba(0,255,255,0.2) 1px, transparent 1px)
`,
backgroundSize: "60px 60px"
}}
/>

</div>

)

}