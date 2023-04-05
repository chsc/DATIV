
const statusSpan     = document.querySelector("#status");

const stateTemp      = document.querySelector("#temperature");
const stateDiskTotal = document.querySelector("#total");
const stateDiskUsed  = document.querySelector("#used");
const stateDiskFree  = document.querySelector("#free");

const rulerXResInput   = document.querySelector("#ruler-xres");
const rulerYResInput   = document.querySelector("#ruler-yres");
const rulerLengthInput = document.querySelector("#ruler-length");

const pmsIntervalInput = document.querySelector("#pms-interval");

const passePartoutHSlider  = document.querySelector("#passe-partout-h");
const passePartoutHOutput  = document.querySelector("#passe-partout-h-output");
const passePartoutVSlider  = document.querySelector("#passe-partout-v");
const passePartoutVOutput  = document.querySelector("#passe-partout-v-output");

const resolutionDropDown = document.querySelector("#setting-resolution")

const shutterSlider   = document.querySelector("#setting-shutter");
const shutterOutput   = document.querySelector("#setting-shutter-output");
const isoSlider       = document.querySelector("#setting-iso");
const isoOutput       = document.querySelector("#setting-iso-output");
const brighSlider     = document.querySelector("#setting-brightness");
const brighOutput     = document.querySelector("#setting-brightness-output");
const contrSlider     = document.querySelector("#setting-contrast");
const contrOutput     = document.querySelector("#setting-contrast-output");

const zoomSlider     = document.querySelector("#view-zoom");
const zoomOutput     = document.querySelector("#view-zoom-output");

const detectorDropDown = document.querySelector("#detector-selection");
const thresholdSlider = document.querySelector("#detector-threshold");
const thresholdOutput = document.querySelector("#detector-threshold-output");

const intervalSlider = document.querySelector("#capture-interval");
const intervalOutput = document.querySelector("#capture-interval-output");

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

function setButtonTextRecording(textspan, origText)
{
   recordButtonTextSpan = document.querySelector(textspan);
   recordButtonTextSpan.textContent = origText;
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
   
   cellIcons.innerHTML += "<a href=\"/download/" + id + "\" download><img src=\"/static/icons/download-24.png\" alt=\"Download File\"/></a> ";
   cellIcons.innerHTML += "<a href=\"/download_meta/" + id + "\" download><img src=\"/static/icons/meta-24.png\" alt=\"Download Meta\"/></a> ";
   cellIcons.innerHTML += "<a href=\"#\" onclick=\"deleteTableEntry(this)\" data-id=\"" + id + "\"><img src=\"/static/icons/delete-24.png\" alt=\"Delete File\"/></a>";
         
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

async function setupCaptureStillImageButtonHandler()
{
   document.querySelector("#capture-still-image-button").addEventListener ("click", async function () {
      setButtonTextRecording("#capture-still-image-button-text", "Capturing...");
      rname = document.querySelector("#record-name").value;
      rdescription = document.querySelector("#record-description").value;
      data = {
         "name" : rname,
         "description" : rdescription
      };
      resp = await getServer("capture_still_image", data);
      if(!resp.result) {
         setStatusError(resp.status_text);
      } else {
         addTableEntry(resp.name, resp.id, false, resp.description, resp.datetime);
      }
      setButtonTextRecording("#capture-still-image-button-text", "Capture Still Image");
      setStatusNormal(resp.status_text);
   });
}

async function setupStartButtonHandlerHelper(buttonid, buttextspan, origtext, recstr, stopstr, satestr, activestr, nonactivestr)
{
   resp = await getServer(satestr);
   if(resp.mode == nonactivestr) {
      setButtonTextRecording(buttextspan, origtext);
   } if(resp.mode == activestr) {
      setButtonTextRecording(buttextspan, "Stop");
   }
   document.querySelector(buttonid).addEventListener ("click", async function () {
      resp = await getServer(satestr);
      console.log(resp);
      if(resp.mode == nonactivestr) {
         rname = document.querySelector("#record-name").value;
         rdescription = document.querySelector("#record-description").value;
         data = {
            "name" : rname,
            "description" : rdescription
         };
         console.log("getServer", recstr, data);
         resp = await getServer(recstr, data);
         console.log(resp);
         if(resp.result) {
            setButtonTextRecording(buttextspan, "Stop");
            setStatusNormal(resp.status_text);
         } else {
            setStatusError(resp.status_text);
         }
      } if(resp.mode == activestr) {
         resp = await getServer(stopstr);
         if(resp.result) {
            addTableEntry(resp.name, resp.id, true, resp.description, resp.datetime);
            setButtonTextRecording(buttextspan, origtext);
            setStatusNormal(resp.status_text);
         } else {
            setStatusError(resp.status_text);
         }
      }
      return false;
   });
}

async function setupStartButtonHandlerCamera(buttonid, buttextspan, origtext, recstr, stopstr)
{
   return setupStartButtonHandlerHelper(buttonid, buttextspan, origtext, recstr, stopstr, "recording_state", "recording", "playback")
}

async function setupStartButtonHandlerPMSensor(buttonid, buttextspan, origtext, recstr, stopstr)
{
   return setupStartButtonHandlerHelper(buttonid, buttextspan, origtext, recstr, stopstr, "particle_measurement_state", "measuring", "not_measuring")
}

async function updateSystemState()
{
   resp = await getServer("/system_state", null);

   document.querySelector("#temperature").textContent = resp.temperature;

   stateDiskTotal.textContent = resp.disk.total;
   stateDiskUsed.textContent  = resp.disk.used;
   stateDiskFree.textContent  = resp.disk.free;
   document.querySelector("#percent_used").textContent = Math.round((resp.disk.used / resp.disk.total) * 100);
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
   resolutionDropDown.addEventListener("change", async function() {
      resp = await getServer("set_resolution_and_mode", {'value': this.value});
      if(resp.result) {
         setStatusNormal(resp.status_text);
      } else {
         setStatusError(resp.status_text);
      }
   });
   
   setSpinHandler(rulerXResInput, "ruler_xres");
   setSpinHandler(rulerYResInput, "ruler_yres");
   setSpinHandler(rulerLengthInput, "ruler_length");
   
   setSpinHandler(pmsIntervalInput, "pms_interval")

   setSliderHandler(passePartoutHSlider, passePartoutHOutput, "passe_partout_h");
   setSliderHandler(passePartoutVSlider, passePartoutVOutput, "passe_partout_v");

   setSliderHandler(shutterSlider, shutterOutput, "shutter_speed");
   setSliderHandler(isoSlider, isoOutput, "iso");
   setSliderHandler(brighSlider, brighOutput, "brightness");
   setSliderHandler(contrSlider, contrOutput, "contrast");
   
   setSliderHandler(zoomSlider, zoomOutput, "zoom")
}

function setupDetectorControlHandler() {
   detectorDropDown.addEventListener("change", async function() {
      resp = await getServer("set_detector", {'value': this.value});
      if(resp.result) {
         setStatusNormal(resp.status_text);
         resp = await getServer("get_params", {});
         thresholdSlider.value = resp.detector_threshold;
         thresholdOutput.value = thresholdSlider.value;
      } else {
         setStatusError(resp.status_text);
      }
   });
   
   setSliderHandler(thresholdSlider, thresholdOutput, "detector_threshold");
   setSliderHandler(intervalSlider, intervalOutput, "capture_interval");
}

function setupSyncTimeButtonHandler() {
   document.querySelector("#sync-time-button").addEventListener ("click", async function () {
      setDate();
   });
}

function setupResetButtonHandler() {
   document.querySelector("#reset-button").addEventListener ("click", async function () {
      if(confirm('Do you really want to reset all camera settings?')) {
         resp = await getServer("/reset", null);
         if(resp.result) {
            setStatusNormal(resp.status_text);
            window.location.reload();
         } else {
            setStatusError(resp.status_text);
         }
      }
   });
}

function setupDeleteAllButtonHandler() {
   document.querySelector("#delete-all-button").addEventListener ("click", async function () {
      if(confirm('Do you really want to delete all recordings?')) {
         resp = await getServer("/delete_all_recordings", null);
         if(resp.result) {
            setStatusNormal(resp.status_text);
            window.location.reload();
         } else {
            setStatusError(resp.status_text);
         }
      }
   });
}

async function initCameraSettings() {
   let resp = await getServer("get_params", {});

   rulerLengthInput.value  = resp.ruler_length;
   rulerXResInput.value    = resp.ruler_xres;
   rulerYResInput.value    = resp.ruler_yres;
   pmsIntervalInput.value  = resp.pms_interval;

   passePartoutHSlider.value = resp.passe_partout_h;
   passePartoutVSlider.value = resp.passe_partout_v;
   passePartoutHOutput.value = passePartoutHSlider.value;
   passePartoutVOutput.value = passePartoutVSlider.value;

   shutterSlider.value = resp.shutter_speed
   isoSlider.value     = resp.iso;
   brighSlider.value   = resp.brightness;
   contrSlider.value   = resp.contrast;
   zoomSlider.value    = resp.zoom;
   
   shutterOutput.value = shutterSlider.value;
   isoOutput.value     = isoSlider.value;
   brighOutput.value   = brighSlider.value;
   contrOutput.value   = contrSlider.value;
   zoomOutput.value    = zoomSlider.value;
   
   thresholdSlider.value = resp.detector_threshold;
   thresholdOutput.value = thresholdSlider.value;
   
   intervalSlider.value = resp.capture_interval;
   intervalOutput.value = intervalSlider.value;
   
   
   resp = await getServer("get_detector", {});
   detectorDropDown.value = resp.detector;
   
   resp = await getServer("get_resolution_and_mode", {});
   resolutionDropDown.value = resp.resmode;
}

async function setDate() {
   const now = Date.now();
   const today = new Date(now);
   const s = today.toISOString();
   console.log(s)
   resp = await getServer("set_date", {'value': (s)});
   if(resp.result) {
      setStatusNormal(resp.status_text);
   } else {
      setStatusError(resp.status_text);
   }
}

document.addEventListener("DOMContentLoaded", function() { 
   setupStartButtonHandlerCamera("#record-video-button", "#record-video-button-text", "Record Video", "record_video", "stop_record_video")
   setupStartButtonHandlerCamera("#capture-sequence-button", "#capture-sequence-button-text", "Capture Image Sequence", "capture_image_sequence", "stop_capture_image_sequence")
   setupStartButtonHandlerCamera("#detect-objects-button", "#detect-objects-button-text", "Detect Objects", "detect_objects", "stop_detect_objects")
   setupStartButtonHandlerPMSensor("#measure-particles-button", "#measure-particles-button-text", "Measure Particles", "measure_particles", "stop_measure_particles")
   setupCaptureStillImageButtonHandler();
   
   setupSyncTimeButtonHandler();
   setupResetButtonHandler();
   setupDeleteAllButtonHandler();
  
   setupCameraSettingControlHandler();
   setupDetectorControlHandler();
   
   initCameraSettings();
   
   updateSystemState();
   
   setInterval(updateSystemState, 10000);
});
