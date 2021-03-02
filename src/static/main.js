
// does a json request and awaits a json response
function requestFromServer(endPoint, data)
{
   fetch (endPoint, {
      method: 'post',
      headers: {'Content-Type' : 'application/json'},
      body: JSON.stringify(data)
   })
   .then (response => response.json())
   .then(json => {
      console.log(json)
      return json;
   })
   .catch (error => {
      console.log("Error: ", error)
      return null;
   })
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
   document.querySelector("#record-button").addEventListener ("click", function () {
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
      
      console.log("clicked: sending:");
      console.log(data);
      resp = requestFromServer("record", data);

      if(resp == null) {
         setStatusError("Recording failed!");
      } else {
         setStatusNormal(resp.status);
      }      
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

document.addEventListener("DOMContentLoaded", function() { 
   console.log("console  556 ");
   setupStartRecordingButtonHandler();
});


updateDiskFree();
updateTemperature();

setInterval(updateTemperature, 5000);