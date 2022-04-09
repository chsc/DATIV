var cameraPort = 80;

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
      return null;
    }
}

function makeRequest(ip, port, reqstr)
{
   if(port == 80) {
      return "http://" + ip + "/" + reqstr;
   } else {
      return "http://" + ip + ":" + port + "/" + reqstr;
   }
}

async function setupButtons(idprefix, requeststr)
{
   var capture = document.querySelectorAll("[id^='" + idprefix + "']");
   capture.forEach(node => {
      node.addEventListener("click", async function() {
         var ip = node.getAttribute("data-ip");
         span = document.getElementById("status-" + ip);
         const query = makeRequest(ip, cameraPort, requeststr);
         resp = await getServer(query);
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
      })
   });
}

async function setupInitialStatusText() {
   const resp = await getServer("get_hosts");
   //const cameraPort = await getServer("get_camera_port")
   //console.log(resp)
   for(const [ip, host] of Object.entries(resp)) {
      updateStatusText(ip, "Updating status...");
      const query = makeRequest(ip, cameraPort, "recording_state");
      console.log(query)
      fetch(query).then(response => response.json()).then(data => {
         updateStatusText(ip, data.status_text);
      }).catch((error) => {
         updateStatusText(ip, "Unable to reach host!");
      });
   }
}

function updateStatusText(ip, text) {
   element = document.getElementById("status-" + ip);
   if(element != null) {
      element.textContent = text;
   }
}

async function setupAllButton(request, btext) {
   resp = await getServer("get_hosts");
   for(const [ip, host] of Object.entries(resp)) {
      updateStatusText(ip, btext);
      const query = "http://" + ip + ":5000/" + request;
      fetch(query).then(response => response.json()).then(data => {
         updateStatusText(ip, data.status_text);
      }).catch((error) => {
            updateStatusText(ip, "Unable to reach host!");
      });
   }
}

async function setupButtonHandlers()
{
   cameraPort = await getServer("get_camera_port");
   console.log(cameraPort)
   
   document.querySelector("#all-capture-still-image-button").addEventListener ("click", async function () {
      await setupAllButton("capture_still_image", "Capturing ...");
   });
   document.querySelector("#all-record-video-button").addEventListener ("click", async function () {
      await setupAllButton("record_video", "Start recording ...");
   });
   document.querySelector("#all-stop-record-video-button").addEventListener ("click", async function () {
      await setupAllButton("stop_record_video", "Stop recording ...");
   });
   document.querySelector("#all-record-image-sequence-button").addEventListener ("click", async function () {
      await setupAllButton("record_image_sequnce", "Start sequence ...");
   });
   document.querySelector("#all-stop-record-image-sequence-button").addEventListener ("click", async function () {
      await setupAllButton("stop_record_image_sequnce", "Stup sequence ...");
   });
  
   setupButtons("capture-still-image", "capture_still_image");
   setupButtons("record-video", "record_video");
   setupButtons("stop-record-video", "stop_record_video");
   setupButtons("start-detection", "start_detection");
   setupButtons("stop-detection", "stop_detection");
}

document.addEventListener("DOMContentLoaded", function() {
    setupButtonHandlers();
    setupInitialStatusText();
});
