
const statusSpan           = document.querySelector("#status");
const recordButtonTextSpan = document.querySelector("#record-button-text");

const stateTemp      = document.querySelector("#temperature");
const stateDiskTotal = document.querySelector("#total");
const stateDiskUsed  = document.querySelector("#used");
const stateDisk      = document.querySelector("#free");

const isoSlider   = document.querySelector("#setting-iso");
const isoOutput   = document.querySelector("#setting-iso-output");
const brighSlider = document.querySelector("#setting-brightness");
const brighOutput = document.querySelector("#setting-brightness-output");
const contrSlider = document.querySelector("#setting-contrast");
const contrOutput = document.querySelector("#setting-contrast-output");

const deleteRecordingImage = document.querySelector("#delete-recording-image");

// does a json request and awaits a json response
async function postServer(endPoint, data)
{
   console.log(data);
   try {
      const response = await fetch(endPoint, {
         method: 'post',
         headers: {'Content-Type' : 'application/json'},
         body: JSON.stringify(data)
      })
      const json = await response.json();
      console.log(json);
      return json
    } catch (error) {
      console.log(error);
    }
}

// does not post anything and request a json response
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

function setStatusNormal(status)
{
   statusSpan.textContent = status;
   statusSpan.className = "status-normal";
}

function setStatusError(status)
{
   statusSpan.textContent = status;
   statusSpan.className = "status-error";
}

function setButtonTextRecording()
{
   recordButtonTextSpan.textContent = "Stop";
}

function setButtonTextNotRecording()
{
   recordButtonTextSpan.textContent = "Start";
}

async function setupStartRecordingButtonHandler()
{
   resp = await getServer("recording_state");
   if(resp.mode == "playback") {
      setButtonTextNotRecording();
   } if(resp.mode == "recording") {
      setButtonTextRecording();
   }
   document.querySelector("#record-button").addEventListener ("click", async function () {
      resp = await getServer("recording_state");
      if(resp.mode == "playback") {
         
         ruler_xres = document.querySelector("#ruler-xres").value;
         ruler_yres = document.querySelector("#ruler-yres").value;

         rname = document.querySelector("#record-name").value;
         rdescription = document.querySelector("#record-description").value;
         rdetector = document.querySelector("#record-detector").value
   
         rtrigger = "manual"
         if(document.querySelector("#record-trigger-manual").checked) {
            rtrigger = "manual";
         } else if(document.querySelector("#record-trigger-motion").checked) {
            rtrigger = "motion";
         }
   
         rmode = "film-only"
         if(document.querySelector("#record-film-only").checked) {
            rmode = "film-only";
         } else if(document.querySelector("#record-detect-only").checked) {
            rmode = "detect-only";
         } else if(document.querySelector("#record-film-and-detect").checked) {
            rmode = "film-and-detect";
         }
   
         data = {
            "name" : rname,
            "description" : rdescription,
            "detector" : rdetector,
            "trigger" : rtrigger,
            "mode" : rmode,
            "ruler_xres": ruler_xres,
            "ruler_yres": ruler_yres
         };
         
         resp = await postServer("record", data);
         if(resp.result) {
            setButtonTextRecording();
         } else {
            setStatusError(resp.stext);
         }
      } if(resp.mode == "recording") {
         resp = await getServer("stop");
         if(resp.result) {
            location.reload(); 
         } else {
            setStatusError(resp.stext);
         }
      }

      return false;
   });
}

async function updateSystemState()
{
   resp = await getServer("/system_state", null);
   document.querySelector("#temperature").textContent = resp.temperature;
   document.querySelector("#total").textContent = resp.disk.total;
   document.querySelector("#used").textContent = resp.disk.used;
   document.querySelector("#free").textContent = resp.disk.free;
   document.querySelector("#percent_used").textContent = Math.round((resp.disk.used / resp.disk.total) * 100);
}

function setupCameraSettingControlHandler() {
   isoSlider.addEventListener ("input", async function () {
      resp = await getServer("set_param/iso", {'value': this.value});
      if(resp.result) {
         isoOutput.value = this.value;
      } else {
         setStatusError(resp.stext);
      }     
   });
   brighSlider.addEventListener ("input", async function () {
      resp = await getServer("set_param/brightness", {'value': this.value});
      if(resp.result) {
         brighOutput.value = this.value;
      } else {
         setStatusError(resp.stext);
      }
   });
   contrSlider.addEventListener ("input", async function () {
      resp = await getServer("set_param/contrast", {'value': this.value});
      if(resp.result) {
         contrOutput.value = this.value;
      } else {
         setStatusError(resp.stext);
      }
   });
}

async function initCameraSettings() {
   resp = await getServer("get_params", {});

   isoSlider.value   = resp.iso;
   brighSlider.value = resp.brightness;
   contrSlider.value = resp.contrast;

   isoOutput.value   = isoSlider.value;
   brighOutput.value = brighSlider.value;
   contrOutput.value = contrSlider.value;
}

function setupDeleteRecordingButtonHandler() {
   if(deleteRecordingImage == null) {
      return;
   }
   deleteRecordingImage.addEventListener ("click", async function () {
      var id = this.getAttribute("data-recording")
      console.log("delete recording")
      console.log(id)
      resp = await getServer("delete_recording/" + id, null);
      if(resp.result) {
         location.reload();
      } else {
         setStatusError(resp.stext);
      }     
   });
}

document.addEventListener("DOMContentLoaded", function() { 
   setupStartRecordingButtonHandler();
   setupDeleteRecordingButtonHandler();
   setupCameraSettingControlHandler();
   initCameraSettings();
   updateSystemState();
   setInterval(updateSystemState, 5000);
});
