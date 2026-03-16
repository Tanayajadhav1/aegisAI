document.getElementById("save").onclick = () => {

const companyId = document.getElementById("company").value

if(!companyId){
document.getElementById("status").innerText = "Please enter a company ID"
return
}

chrome.storage.local.set({company_id: companyId},()=>{

document.getElementById("status").innerText = "Firewall connected"

})

}