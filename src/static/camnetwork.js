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

async function setupButtonHandlers()
{
   document.querySelector("#update-button").addEventListener ("click", async function () {
      resp = await getServer("update_camera_network");
      if(resp.result) {
        location.reload();
      }
   });
   document.querySelector("#all-capture-still-button").addEventListener ("click", async function () {
    resp = await getServer("all_capture_still_image");
    if(resp.result) {
      
    }
   });
   document.querySelector("#all-record-video-button").addEventListener ("click", async function () {
    resp = await getServer("all_record_video");
    if(resp.result) {
      
    }
   });
}

document.addEventListener("DOMContentLoaded", function() { 
    setupButtonHandlers();
 });