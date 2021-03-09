
// does a json request and awaits a json response
async function requestFromServer(endPoint, data)
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

function setupStartRecordingButtonHandler()
{
   document.querySelector("#record-button").addEventListener ("click", async function () {
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
      
      resp = await requestFromServer("record", data);
      console.log("response:");
      console.log(resp)

      if(resp == null) {
         setStatusError("Recording failed!");
      } else {
         if(resp.result) {
            setStatusNormal(resp.text);
            //location.reload(); 
         } else {
            setStatusError(resp.text);
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

const isoSlider   = document.querySelector("#setting-iso");
const isoOutput   = document.querySelector("#setting-iso-output");
const brighSlider = document.querySelector("#setting-brightness");
const brighOutput = document.querySelector("#setting-brightness-output");
const contrSlider = document.querySelector("#setting-contrast");
const contrOutput = document.querySelector("#setting-contrast-output");

function setupCameraSettings() {
   isoSlider.addEventListener ("input", async function () {
      resp = await requestFromServer("set_iso", {'iso': this.value});
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
      resp = await requestFromServer("set_brightness", {'brightness': this.value});
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
      resp = await requestFromServer("set_contrast", {'contrast': this.value});
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

document.addEventListener("DOMContentLoaded", function() { 
   console.log("console");
   setupStartRecordingButtonHandler();
   setupCameraSettings();
   initCameraSettings();
});

updateDiskFree();
updateTemperature();

setInterval(updateTemperature, 5000);