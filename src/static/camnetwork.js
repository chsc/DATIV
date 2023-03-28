var cameraPort = 80;

async function getServer(endPoint, params) {
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

function makeRequest(ip, port, reqstr) {
   if(port == 80) {
      return "http://" + ip + "/" + reqstr;
   } else {
      return "http://" + ip + ":" + port + "/" + reqstr;
   }
}

function getNameDesc() {
   rname = document.querySelector("#record-name").value;
   rdescription = document.querySelector("#record-description").value;
   data = {
      "name" : rname,
      "description" : rdescription
   };
   return data;
}


async function broadcast(msg, request, params = null) {
   const resp = await getServer("get_hosts");
   for(const [ip, host] of Object.entries(resp)) {
      updateStatusText(ip, "Sending: " + msg + "...");
      const urls = makeRequest(ip, cameraPort, request);
      var url = new URL(urls);
      if(params != null) {
         url.search = new URLSearchParams(params).toString();
      }
      fetch(url).then(response => response.json()).then(data => {
         updateStatusText(ip, data.status_text);
      }).catch((error) => {
         updateStatusText(ip, error.toString());
      });
   }
}

function updateStatusText(ip, text) {
   element = document.getElementById("status-" + ip);
   if(element != null) {
      element.textContent = text;
   }
}

async function setupButtons(idprefix, requeststr, sendNameDesc = false) {
   var capture = document.querySelectorAll("[id^='" + idprefix + "']");
   capture.forEach(node => {
      node.addEventListener("click", async function() {
         var ip = node.getAttribute("data-ip");
         const urls = makeRequest(ip, cameraPort, requeststr);
         var url = new URL(urls);
         if(sendNameDesc) {
            url.search = new URLSearchParams(getNameDesc()).toString();
         }
         fetch(url).then(response => response.json()).then(data => {
            updateStatusText(ip, data.status_text);
         }).catch((error) => {
            updateStatusText(ip, error.toString());
         });
      })
   });
}

function setSliderHandler(sliderId, outputId, paramname) {
   const slider = document.querySelector(sliderId);
   const output = document.querySelector(outputId);
   slider.addEventListener ("input", async function () {
      broadcast("Setting parameter...", "set_param/" + paramname, {'value': this.value});
      output.value = this.value;
   });
}

async function setDate() {
   const now = Date.now();
   const today = new Date(now);
   const s = today.toISOString();
   console.log(s)
   broadcast("Setting time and date", "set_date", {'value': (s)});
}

async function setupButtonHandlers() {
   cameraPort = await getServer("get_camera_port");
   console.log(cameraPort)
   
   document.querySelector("#sync-time-button").addEventListener ("click", async function () {
      setDate();
   });
   document.querySelector("#update-state-button").addEventListener ("click", async function () {
      broadcast("Updating state", "recording_state");
   });
   document.querySelector("#delete-all-recordings-button").addEventListener ("click", async function () {
      if(confirm('Do you really want to delete all recordings?')) {
         broadcast("Delete all recordings", "delete_all_recordings")
      }
   });
   document.querySelector("#reset-button").addEventListener ("click", async function () {
      if(confirm('Do you really want to reset all cameras?')) {
         broadcast("Reseting camera", "reset")
      }
   });
   
   document.querySelector("#all-capture-still-image-button").addEventListener ("click", async function () {
      broadcast("Capture still image", "capture_still_image", getNameDesc());
   });
   
   document.querySelector("#all-record-video-button").addEventListener ("click", async function () {
      broadcast("Start recording", "record_video", getNameDesc());
   });
   document.querySelector("#all-stop-record-video-button").addEventListener ("click", async function () {
      broadcast("Stop recording", "stop_record_video");
   });
   
   document.querySelector("#all-capture-image-sequence-button").addEventListener ("click", async function () {
      broadcast("Start image sequence", "capture_image_sequence", getNameDesc());
   });
   document.querySelector("#all-stop-capture-image-sequence-button").addEventListener ("click", async function () {
      broadcast("Stop image sequence", "stop_capture_image_sequence");
   });
   
   document.querySelector("#all-start-detection-button").addEventListener ("click", async function () {
      broadcast("Start object detection", "detect_objects", getNameDesc());
   });
   document.querySelector("#all-stop-detection-button").addEventListener ("click", async function () {
      broadcast("Stop object detection", "stop_detect_objects");
   });
  
   setupButtons("capture-still-image", "capture_still_image", true);
   setupButtons("record-video", "record_video", true);
   setupButtons("stop-record-video", "stop_record_video");
   setupButtons("capture-image-sequence", "capture_image_sequence", true);
   setupButtons("stop-capture-image-sequence", "stop_capture_image_sequence");
   setupButtons("start-detection", "detect_objects", true);
   setupButtons("stop-detection", "stop_detect_objects");
   
   setSliderHandler("#detector-threshold", "#detector-threshold-output", "detector_threshold");
   setSliderHandler("#capture-interval", "#capture-interval-output", "capture_interval");
   setSliderHandler("#iso", "#iso-output", "iso");
   setSliderHandler("#shutter-speed", "#shutter-speed-output", "shutter_speed");
}

function setupDetectorControlHandler() {
   const detectorDropDown = document.querySelector("#detector-selection");
   detectorDropDown.addEventListener("change", async function() {
      const resp = await getServer("get_hosts");
      for(const [ip, host] of Object.entries(resp)) {
         updateStatusText(ip, "Sending: Setting detector...");
         const urls = makeRequest(ip, cameraPort, "set_detector");
         var url = new URL(urls);
         url.search = new URLSearchParams({'value': this.value}).toString();
         fetch(url).then(response => response.json()).then(data => {
            updateStatusText(ip, data.status_text);
         }).catch((error) => {
            updateStatusText(ip, error.toString());
         });
      }
   });
}

document.addEventListener("DOMContentLoaded", function() {
    setupButtonHandlers();
    setupDetectorControlHandler();
    broadcast("Updating state", "recording_state");
});
