; load-frames.scm
; Load a sequence of files (frames) in as a single image with many layers.
; Ned Batchelder, May 2002
; http://www.nedbatchelder.com

(define (script-fu-load-frames base firstn lastn digits ext)
  (let* ()
	; Open the first frame as an image. Subsequent frames will be layers.
	(set! imgname (string-append base (number->string firstn 10 digits) ext))
	(set! img1 (car (gimp-file-load RUN-NONINTERACTIVE imgname imgname)))
	
	; Loop over the other frame numbers.
	(set! imgnum 2)
	(while (<= imgnum lastn)
	  
	  ; Build the file name.
	  (set! imgname (string-append base (number->string imgnum 10 digits) ext))
	  
	  ; Open the file as an image, and get its layer.
	  (set! imgn (car (gimp-file-load RUN-NONINTERACTIVE imgname imgname)))
	  (set! imgn-layer (car (gimp-image-active-drawable imgn)))
	  
	  ; Copy the image to the clipboard.
	  (gimp-selection-all imgn)
	  (gimp-edit-copy imgn-layer)
	  
	  ; Make a new layer in the original image to fit the new image.
	  (set! layern (car
		  (gimp-layer-new img1
			(car (gimp-image-width imgn)) (car (gimp-image-height imgn))
			(car (gimp-image-base-type imgn))
			imgname
			100
			NORMAL-MODE)
	  ))
		
	  (gimp-image-add-layer img1 layern -1)
	  
	  ; Paste the new image into the new layer.
	  (set! sel (car (gimp-edit-paste layern FALSE)))
	  (gimp-floating-sel-anchor sel)
	  
	  ; Delete the frame image (from memory).
	  (gimp-image-delete imgn)
	  
	  (set! imgnum (+ 1 imgnum))
	)
	
	(gimp-display-new img1)
  )
)	

(script-fu-register "script-fu-load-frames"
	_"<Toolbox>/Xtns/Script-Fu/Utils/Load Frames..."
	"Load a sequence of files (frames) into layers of an image"
	"Ned Batchelder (ned@nedbatchelder.com)"
	"Ned Batchelder"
	"May 2002"
	""
	SF-STRING _"File name prefix" "frame"
	SF-ADJUSTMENT _"First frame num" '(1 1 100 1 10 0 0)
	SF-ADJUSTMENT _"Last frame num" '(10 1 999 1 10 0 0)
	SF-ADJUSTMENT _"Frame num digits" '(2 1 10 1 10 0 0)
	SF-STRING _"File name suffix" ".bmp"
)
