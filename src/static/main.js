
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
async function getServer(endPoint)
{
   try {
      const response = await fetch(endPoint)
      const json = await response.json();
      console.log(json);
      return json
    } catch (error) {
      console.log(error);
    }
}

function setStatusNormal(status)
{
   span = document.querySelector("#status");
   span.textContent = status;
   span.className = "status-normal";
}

function setStatusError(status)
{
   span = document.querySelector("#status");
   span.textContent = status;
   span.className = "status-error";
}

function setButtonTextRecording()
{
   span = document.querySelector("#record-button-text");
   span.textContent = "Stop";
}

function setButtonTextNotRecording()
{
   span = document.querySelector("#record-button-text");
   span.textContent = "Start";
}

function isRecording()
{
   span = document.querySelector("#record-button-text");
   return span.textContent == "Stop";
}

function setupStartRecordingButtonHandler()
{
   document.querySelector("#record-button").addEventListener ("click", async function () {
      if(isRecording()) {
         resp = await getServer("stop");
         console.log("response:");
         console.log(resp);
         if(resp == null) {
            setStatusError("Stop request failed!");
         } else {
            if(resp.result) {
               setStatusNormal(resp.stext);
               setButtonTextNotRecording();
            } else {
               setStatusError(resp.stext);
            }
         }        
         return;
      }

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
      console.log("response:");
      console.log(resp)

      if(resp == null) {
         setStatusError("Recording request failed!");
      } else {
         if(resp.result) {
            setStatusNormal(resp.stext);
            setButtonTextRecording();
            //location.reload(); 
         } else {
            setStatusError(resp.stext);
         }
      }
      
      return false;
   });
}

function updateTemperature()
{
   fetch( "/temperature" )
      .then( response => {
         if( !response.ok )
            throw new Error( "fetch failed" ) ;
         return response.json() ;
      } )
      .then( json => document.querySelector("#temperature").textContent = json.temperature )
      .catch( error => alert(error) ) ;
}

function updateDiskFree()
{
   fetch( "/diskfree" )
      .then( response => {
         if( !response.ok )
            throw new Error( "fetch failed" ) ;
         return response.json() ;
      } )
      .then( json => {
          document.querySelector("#total").textContent = json.total;
          document.querySelector("#used").textContent = json.used;
          document.querySelector("#free").textContent = json.free;
      })
      .catch( error => alert(error) ) ;
}


function setupCameraSettings() {
   isoSlider.addEventListener ("input", async function () {
      resp = await postServer("set_iso", {'iso': this.value});
      if(resp == null) {
         setStatusError("Request failed");
         return;
      }
      if(resp.result) {
         isoOutput.value = this.value;
      } else {
         setStatusError(resp.stext);
      }     
   });
   brighSlider.addEventListener ("input", async function () {
      resp = await postServer("set_brightness", {'brightness': this.value});
      if(resp == null) {
         setStatusError("Request failed");
         return;
      }
      if(resp.result) {
         brighOutput.value = this.value;
      } else {
         setStatusError(resp.stext);
      }     
   });
   contrSlider.addEventListener ("input", async function () {
      resp = await postServer("set_contrast", {'contrast': this.value});
      if(resp == null) {
         setStatusError("Request failed");
         return;
      }
      if(resp.result) {
         contrOutput.value = this.value;
      } else {
         setStatusError(resp.stext);
      }     
   });
}

function initCameraSettings() {
   isoOutput.value   = isoSlider.value;
   brighOutput.value = brighSlider.value;
   contrOutput.value = contrSlider.value;
}

function setupDeleteRecordingButtonHandler() {
   deleteRecordingImage.addEventListener ("click", async function () {
      var id = this.getAttribute("data-recording")
      console.log("delete recording")
      console.log(id)
      resp = await getServer("delete_recording/" + id, {'contrast': this.value});
      if(resp == null) {
         setStatusError("Request failed");
         return;
      }
      if(resp.result) {
         location.reload();
      } else {
         setStatusError(resp.stext);
      }     
   });
}

document.addEventListener("DOMContentLoaded", function() { 
   console.log("console");
   setupStartRecordingButtonHandler();
   setupDeleteRecordingButtonHandler();
   initCameraSettings();
   setupCameraSettings();
});

updateDiskFree();
updateTemperature();

setInterval(updateTemperature, 5000);