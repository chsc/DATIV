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

async function setupButtons(idprefix, requeststr)
{
   var capture = document.querySelectorAll("[id^='" + idprefix + "']");
   console.log(capture)
   capture.forEach(node=>{
      //console.log(node);
      node.addEventListener("click", async function() {
      var ip = node.getAttribute("data-ip");
      span = document.getElementById("status-" + ip);
      resp = await getServer("http://" + ip + ":5000/" + requeststr);
      if(resp != null && resp.result) {
         console.log(resp);
         if(span != null) {
            span.textContent = resp.status_text;
         }
      } else {
         if(span != null) {
            span.textContent = "Request '" + requeststr + "' failed!";
         }
      }
   })});
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
   document.querySelector("#all-stop-video-button").addEventListener ("click", async function () {
      resp = await getServer("all_stop_video");
      if(resp.result) {
         updateStatus(resp.results);
      }
   });
   document.querySelector("#all-start-detection-button").addEventListener ("click", async function () {
      resp = await getServer("all_start_detection");
      if(resp.result) {
         updateStatus(resp.results);
      }
   });
   document.querySelector("#all-stop-detection-button").addEventListener ("click", async function () {
      resp = await getServer("all_stop_detection");
      if(resp.result) {
         updateStatus(resp.results);
      }
   });
  
   setupButtons("capture-still", "capture_still_image");
   setupButtons("record-video", "record_video");
   setupButtons("stop-video", "stop");
   setupButtons("start-detection", "start_detection");
   setupButtons("stop-detection", "stop_detection");
}

document.addEventListener("DOMContentLoaded", function() { 
    setupButtonHandlers();
 });