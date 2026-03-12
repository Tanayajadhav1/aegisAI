import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

export default function CyberBackground() {

 const particlesInit = async (main) => {
   await loadFull(main);
 };

 return (
   <Particles
     id="tsparticles"
     init={particlesInit}
     style={{ width: "100%", height: "100%" }}
     options={{
       background:{color:"transparent"},
       particles:{
         number:{value:80},
         color:{value:"#00FFFF"},
         links:{
           enable:true,
           color:"#00FFFF",
           distance:150
         },
         move:{enable:true,speed:1},
         size:{value:2}
       }
     }}
   />
 );
}