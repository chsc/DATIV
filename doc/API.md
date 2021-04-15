# Camera Remote API

The camera can be remote controlled by sending HTTP requests:

    http://<camera_ip>:5000/<request>

Where *request* can one of the following strings:

## video_stream

Returns the current camera view as a motion jpeg stream.

## download/< ident >

Downloads a recorded video or still image file, identified by *ident*.

## delete_recording/< ident >

Returns a recorded video file, identified by *ident*.

## record (POST)

Starts a recording.

## record_video

Starts a recording.

## stop

Stops a recording.

## capture_still_image

Captures a still image.

## recording_state

Returns the current recording state.

## system_state

Returns the current system state, like temperature level and disk usage.

## set_param/< param >?value=< val >

Sets a camera parameter. Param can be one of the following strings:

* iso
* contrast
* brightness
* ruler_xres
* ruler_yres

The *value* argument specifies the new value of the camera parameter.

## get_params

Returns all camera parameters.
