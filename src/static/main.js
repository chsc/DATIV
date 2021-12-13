
const statusSpan           = document.querySelector("#status");
const recordButtonTextSpan = document.querySelector("#record-button-text");
const recordButtonOrigText = "Start Video Recording"

const stateTemp      = document.querySelector("#temperature");
const stateDiskTotal = document.querySelector("#total");
const stateDiskUsed  = document.querySelector("#used");
const stateDiskFree  = document.querySelector("#free");

const rulerXResInput   = document.querySelector("#ruler-xres");
const rulerYResInput   = document.querySelector("#ruler-yres");
const rulerLengthInput = document.querySelector("#ruler-length");

const passePartoutHSlider  = document.querySelector("#passe-partout-h");
const passePartoutHOutput  = document.querySelector("#passe-partout-h-output");
const passePartoutVSlider  = document.querySelector("#passe-partout-v");
const passePartoutVOutput  = document.querySelector("#passe-partout-v-output");

const modeDropDown       = document.querySelector("#setting-mode");
const resolutionDropDown = document.querySelector("#setting-resolution")

const shutterSlider   = document.querySelector("#setting-shutter");
const shutterOutput   = document.querySelector("#setting-shutter-output");
const isoSlider       = document.querySelector("#setting-iso");
const isoOutput       = document.querySelector("#setting-iso-output");
const brighSlider     = document.querySelector("#setting-brightness");
const brighOutput     = document.querySelector("#setting-brightness-output");
const contrSlider     = document.querySelector("#setting-contrast");
const contrOutput     = document.querySelector("#setting-contrast-output");

const thresholdSlider = document.querySelector("#detector-threshold");
const thresholdOutput = document.querySelector("#detector-threshold-output");

const recordingTable = document.querySelector("#recording-table")

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
   //console.log("Normal: " + status);
}

function setStatusError(status)
{
   statusSpan.textContent = status;
   statusSpan.className = "status-error";
   //console.log("Error: " + status);
}

function setButtonTextRecording()
{
   recordButtonTextSpan.textContent = "Stop";
}

function setButtonTextNotRecording()
{
   recordButtonTextSpan.textContent = recordButtonOrigText;
}

function addTableEntry(name, id, isVideo, description, dateTime)
{
   var rowCount = recordingTable.rows.length;
   var row      = recordingTable.insertRow(rowCount);

   var cellName     = row.insertCell(0);
   var cellIcons    = row.insertCell(1);
   var cellDesc     = row.insertCell(2);
   var cellDateTime = row.insertCell(3);
   
   cellName.innerHTML = name;
   
   if(isVideo) {
      cellIcons.innerHTML = "<a href=\"/player/" + id +  "\"><img src=\"/static/icons/video-24.png\" alt=\"Video Player\"/></a> ";
   } else {
      cellIcons.innerHTML = "<a href=\"/player/" + id +  "\"><img src=\"/static/icons/image-24.png\" alt=\"Image View\"/></a> ";
   }
   cellIcons.innerHTML += "<a href=\"/download/" + id + "\" download><img src=\"/static/icons/download-24.png\" alt=\"Download\"/></a> ";
   cellIcons.innerHTML += "<a href=\"/download_transcoded/" + id + "\" download><img src=\"/static/icons/download-24.png\" alt=\"Download\"/></a> ";
   cellIcons.innerHTML += "<a href=\"/detector/" + id + "\"><img src=\"/static/icons/detect-24.png\" alt=\"Detector\"/></a> ";
   cellIcons.innerHTML += "<a href=\"#\" onclick=\"deleteTableEntry(this)\" data-id=\"" + id + "\"><img src=\"/static/icons/delete-24.png\" alt=\"Delete\"/></a>";

   cellDesc.innerHTML = description;
   cellDateTime.innerHTML = dateTime;
}

async function deleteTableEntry(row)
{
   var answer = window.confirm("Do you really want to delete the file?");
   if(!answer) return;
   var id = row.getAttribute("data-id")
   console.log("delete id")
   console.log(id)
   resp = await getServer("delete_recording/" + id, null);
   if(resp.result) {
      var rindex = row.parentNode.parentNode.rowIndex;
      recordingTable.deleteRow(rindex);
   } else {
      setStatusError(resp.stext);
   }   
}

async function setupObjectDetectionButtonHandler()
{
   document.querySelector("#objdet-button").addEventListener ("click", async function () {
      resp = await getServer("start_object_detection");
      if(!resp.result) {
         setStatusError(resp.stext);
      } else {
         addTableEntry(resp.name, resp.id, false, resp.description, resp.datetime);
      }
   });
}

async function setupCaptureStillImageButtonHandler()
{
   document.querySelector("#capture-button").addEventListener ("click", async function () {
      resp = await getServer("capture_still_image");
      if(!resp.result) {
         setStatusError(resp.stext);
      } else {
         addTableEntry(resp.name, resp.id, false, resp.description, resp.datetime);
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
         //rdetector = document.querySelector("#record-detector").value
   
         data = {
            "name" : rname,
            "description" : rdescription
         };
         
         resp = await getServer("record_video", data);
         if(resp.result) {
            setButtonTextRecording();
         } else {
            setStatusError(resp.stext);
         }
      } if(resp.mode == "recording") {
         resp = await getServer("stop");
         if(resp.result) {
            addTableEntry(resp.name, resp.id, true, resp.description, resp.datetime);
            setButtonTextNotRecording();
         } else {
            setStatusError(resp.status_text);
         }
      }
      return false;
   });
}

async function updateSystemState()
{
   resp = await getServer("/system_state", null);

   document.querySelector("#temperature").textContent = resp.temperature;

   stateDiskTotal.textContent = resp.disk.total;
   stateDiskUsed.textContent  = resp.disk.used;
   stateDiskFree.textContent  = resp.disk.free;
   document.querySelector("#percent_used").textContent = Math.round((resp.disk.used / resp.disk.total) * 100);

   //statusSpan.textContent = resp.recording.status_text
}

function setSpinHandler(input, paramname) {
   input.addEventListener("input", async function() {
      resp = await getServer("set_param/" + paramname, {'value': this.value});
      if(!resp.result) {
         setStatusError(resp.status_text);
      }
   });
}

function setSliderHandler(input, output, paramname) {
   input.addEventListener ("input", async function () {
      resp = await getServer("set_param/" + paramname, {'value': this.value});
      if(resp.result) {
         output.value = this.value;
      } else {
         setStatusError(resp.status_text);
      }
   });
}

function setupCameraSettingControlHandler() {
   modeDropDown.addEventListener("change", async function() {
      resp = await getServer("set_camera_mode", {'mode': this.value});
      if(resp.result) {
         setStatusNormal(resp.status_text);
      } else {
         setStatusError(resp.status_text);
      }
   });
   
   resolutionDropDown.addEventListener("change", async function() {
      resp = await getServer("set_resolution", {'value': this.value});
      if(resp.result) {
         setStatusNormal(resp.status_text);
      } else {
         setStatusError(resp.status_text);
      }
   });
   
   setSpinHandler(rulerXResInput, "ruler_xres");
   setSpinHandler(rulerYResInput, "ruler_yres");
   setSpinHandler(rulerLengthInput, "ruler_length");

   setSliderHandler(passePartoutHSlider, passePartoutHOutput, "passe_partout_h");
   setSliderHandler(passePartoutVSlider, passePartoutVOutput, "passe_partout_v");

   setSliderHandler(shutterSlider, shutterOutput, "shutter_speed");
   setSliderHandler(isoSlider, isoOutput, "iso");
   setSliderHandler(brighSlider, brighOutput, "brightness");
   setSliderHandler(contrSlider, contrOutput, "contrast");

   setSliderHandler(thresholdSlider, thresholdOutput, "detector_threshold");
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

   shutterSlider.value = resp.shutter_speed
   isoSlider.value     = resp.iso;
   brighSlider.value   = resp.brightness;
   contrSlider.value   = resp.contrast;
   
   shutterOutput.value = resp.shutter_speed
   isoOutput.value     = isoSlider.value;
   brighOutput.value   = brighSlider.value;
   contrOutput.value   = contrSlider.value;
}

document.addEventListener("DOMContentLoaded", function() { 
   setupStartRecordingButtonHandler();
   setupCaptureStillImageButtonHandler();
   setupObjectDetectionButtonHandler();
   setupCameraSettingControlHandler();
   initCameraSettings();
   updateSystemState();
   setInterval(updateSystemState, 2000);
});
