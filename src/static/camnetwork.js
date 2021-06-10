async function getServer(endPoint, params)
{
   try {
      var query = endPoint
      if(params != null) {
         query = endPoint + "?" + new URLSearchParams(params).toString();
      }
      const response = await fetch(query)
      const json = await response.json();
      console.log(json);
      return json
    } catch (error) {
      console.log(error);
    }
}

function updateStatus(results) {
   for(const [ip, res] of Object.entries(results)) {
      element = document.getElementById("status-" + ip);
      if(element != null) {
         element.textContent = res[1];
      }
   }
}

async function setupButtonHandlers()
{
   document.querySelector("#update-button").addEventListener ("click", async function () {
      resp = await getServer("update_camera_network");
      if(resp.result) {
        location.reload();
      }
      console.log(resp);
   });
   document.querySelector("#all-capture-still-button").addEventListener ("click", async function () {
    resp = await getServer("all_capture_still_image");
    if(!resp.result) {
      updateStatus(resp.results);
    }
   });
   document.querySelector("#all-record-video-button").addEventListener ("click", async function () {
    resp = await getServer("all_record_video");
    if(resp.result) {
      updateStatus(resp.results);
    }
   });
   document.querySelector("#all-record-video-button").addEventListener ("click", async function () {
      resp = await getServer("all_stop_video");
      if(resp.result) {
         updateStatus(resp.results);
      }
   });
}

document.addEventListener("DOMContentLoaded", function() { 
    setupButtonHandlers();
 });