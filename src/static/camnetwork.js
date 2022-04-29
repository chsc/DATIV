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

async function updateStatus() {
   const resp = await getServer("get_hosts");
   //const cameraPort = await getServer("get_camera_port")
   //console.log(resp)
   for(const [ip, host] of Object.entries(resp)) {
      updateStatusText(ip, "Updating state...");
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
      const query = makeRequest(ip, cameraPort, request);
      fetch(query).then(response => response.json()).then(data => {
         updateStatusText(ip, data.status_text);
      }).catch((error) => {
         updateStatusText(ip, "Unable to reach host!");
      });
   }
}

async function setDate() {
   const now = Date.now();
   const today = new Date(now);
   const s = today.toISOString();
   console.log(s)
   const resp = await getServer("get_hosts");
   for(const [ip, host] of Object.entries(resp)) {
      updateStatusText(ip, "Sending: Setting time and date...");
      const urls = makeRequest(ip, cameraPort, "set_date");
      var url = new URL(urls);
      url.search = new URLSearchParams({'value': (s)}).toString();
      fetch(url).then(response => response.json()).then(data => {
         updateStatusText(ip, data.status_text);
      }).catch((error) => {
            updateStatusText(ip, "Unable to reach host!");
      });
   }
}

async function deleteAllRecordings() {
   const resp = await getServer("get_hosts");
   for(const [ip, host] of Object.entries(resp)) {
      updateStatusText(ip, "Sending: Delete all recordings...");
      const urls = makeRequest(ip, cameraPort, "delete_all_recordings");
      var url = new URL(urls);
      fetch(url).then(response => response.json()).then(data => {
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
   
   document.querySelector("#sync-time-button").addEventListener ("click", async function () {
      setDate();
   });
   document.querySelector("#update-state-button").addEventListener ("click", async function () {
      updateStatus();
   });
   document.querySelector("#delete-all-recordings-button").addEventListener ("click", async function () {
      if(confirm('Do you really want to delete all recordings?')) {
         deleteAllRecordings();
      }
   });
   
   document.querySelector("#all-capture-still-image-button").addEventListener ("click", async function () {
      await setupAllButton("capture_still_image", "Sending: Capture still image ...");
   });
   
   document.querySelector("#all-record-video-button").addEventListener ("click", async function () {
      await setupAllButton("record_video", "Sending: Start recording ...");
   });
   document.querySelector("#all-stop-record-video-button").addEventListener ("click", async function () {
      await setupAllButton("stop_record_video", "Sending: Stop recording ...");
   });
   
   document.querySelector("#all-capture-image-sequence-button").addEventListener ("click", async function () {
      await setupAllButton("capture_image_sequence", "Sending: Start image sequence ...");
   });
   document.querySelector("#all-stop-capture-image-sequence-button").addEventListener ("click", async function () {
      await setupAllButton("stop_capture_image_sequence", "Sending: Stop image sequence ...");
   });
   
   document.querySelector("#all-start-detection-button").addEventListener ("click", async function () {
      await setupAllButton("detect_objects", "Sending: Start object detection ...");
   });
   document.querySelector("#all-stop-detection-button").addEventListener ("click", async function () {
      await setupAllButton("stop_detect_objects", "Sending: Stop object detection ...");
   });
  
   setupButtons("capture-still-image", "capture_still_image");
   setupButtons("record-video", "record_video");
   setupButtons("stop-record-video", "stop_record_video");
   setupButtons("capture-image-sequence", "capture_image_sequence");
   setupButtons("stop-capture-image-sequence", "stop_capture_image_sequence");
   setupButtons("start-detection", "detect_objects");
   setupButtons("stop-detection", "stop_detect_objects");
}

document.addEventListener("DOMContentLoaded", function() {
    setupButtonHandlers();
    updateStatus();
});
