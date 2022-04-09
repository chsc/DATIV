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

async function setupButtons(idprefix, requeststr)
{
   var capture = document.querySelectorAll("[id^='" + idprefix + "']");
   console.log(capture)
   capture.forEach(node => {
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
      })
   });
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
   document.querySelector("#all-stop-record-video-button").addEventListener ("click", async function () {
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
});
