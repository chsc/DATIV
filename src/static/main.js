
const statusSpan           = document.querySelector("#status");
const recordButtonTextSpan = document.querySelector("#record-button-text");
const recordButtonOrigText = recordButtonTextSpan.textContent;

const stateTemp      = document.querySelector("#temperature");
const stateDiskTotal = document.querySelector("#total");
const stateDiskUsed  = document.querySelector("#used");
const stateDisk      = document.querySelector("#free");

const rulerXResInput   = document.querySelector("#ruler-xres");
const rulerYResInput   = document.querySelector("#ruler-yres");
const rulerLengthInput = document.querySelector("#ruler-length");

const passePartoutHSlider  = document.querySelector("#passe-partout-h");
const passePartoutHOutput  = document.querySelector("#passe-partout-h-output");
const passePartoutVSlider  = document.querySelector("#passe-partout-v");
const passePartoutVOutput  = document.querySelector("#passe-partout-v-output");

const isoSlider   = document.querySelector("#setting-iso");
const isoOutput   = document.querySelector("#setting-iso-output");
const brighSlider = document.querySelector("#setting-brightness");
const brighOutput = document.querySelector("#setting-brightness-output");
const contrSlider = document.querySelector("#setting-contrast");
const contrOutput = document.querySelector("#setting-contrast-output");

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
   recordButtonTextSpan.textContent = recordButtonOrigText;
}

async function setupCaptureStillImageButtonHandler()
{
   document.querySelector("#capture-button").addEventListener ("click", async function () {
      resp = await getServer("capture_still_image");
      if(!resp.result) {
         setStatusError(resp.stext);
      } else {
         location.reload();
      }
   });
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
            "mode" : rmode
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

function setSpinHandler(input, paramname) {
   input.addEventListener("input", async function() {
      resp = await getServer("set_param/" + paramname, {'value': this.value});
      if(!resp.result) {
         setStatusError(resp.stext);
      }
   });
}

function setSliderHandler(input, output, paramname) {
   input.addEventListener ("input", async function () {
      resp = await getServer("set_param/" + paramname, {'value': this.value});
      if(resp.result) {
         output.value = this.value;
      } else {
         setStatusError(resp.stext);
      }
   });
}

function setupCameraSettingControlHandler() {
   setSpinHandler(rulerXResInput, "ruler_xres");
   setSpinHandler(rulerYResInput, "ruler_yres");
   setSpinHandler(rulerLengthInput, "ruler_length");

   setSliderHandler(passePartoutHSlider, passePartoutHOutput, "passe_partout_h");
   setSliderHandler(passePartoutVSlider, passePartoutVOutput, "passe_partout_v");

   setSliderHandler(isoSlider, isoOutput, "iso");
   setSliderHandler(brighSlider, brighOutput, "brightness");
   setSliderHandler(contrSlider, contrOutput, "contrast");
}

async function initCameraSettings() {
   resp = await getServer("get_params", {});

   rulerLengthInput.value  = resp.ruler_length;
   rulerXResInput.value    = resp.ruler_xres;
   rulerYResInput.value    = resp.ruler_yres;

   passePartoutHSlider.value = resp.passe_partout_h;
   passePartoutVSlider.value = resp.passe_partout_v;
   passePartoutHOutput.value = passePartoutHSlider.value;
   passePartoutVOutput.value = passePartoutVSlider.value;

   isoSlider.value   = resp.iso;
   brighSlider.value = resp.brightness;
   contrSlider.value = resp.contrast;
   isoOutput.value   = isoSlider.value;
   brighOutput.value = brighSlider.value;
   contrOutput.value = contrSlider.value;
}

function setupDeleteRecordingButtonHandler() {
   const deleteRecordingImageList = document.getElementsByClassName("delete-recording-image");
   if(deleteRecordingImageList == null) {
      return;
   }
   Array.from(deleteRecordingImageList).forEach(function(deleteRecordingImage) {
      deleteRecordingImage.addEventListener ("click", async function () {
         var answer = window.confirm("Do you really want to delete the file?");
         if(!answer) return;
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
   });
}

document.addEventListener("DOMContentLoaded", function() { 
   setupStartRecordingButtonHandler();
   setupCaptureStillImageButtonHandler();
   setupDeleteRecordingButtonHandler();
   setupCameraSettingControlHandler();
   initCameraSettings();
   updateSystemState();
   setInterval(updateSystemState, 5000);
});
