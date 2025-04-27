.PHONY: test large final clean

SMALL = 300
LARGE = 3840
SIZES = 60 200 640

povtest:
	povray +W$(SMALL) +H$(SMALL) Declare=Dark=0 +Ododeca3_light.png dodeca3.pov
	povray +W$(SMALL) +H$(SMALL) Declare=Dark=1 +Ododeca3_dark.png dodeca3.pov

povlarge:
	povray +W$(LARGE) +H$(LARGE) Declare=Dark=0 +Ododeca3_light_large.png dodeca3.pov
	povray +W$(LARGE) +H$(LARGE) Declare=Dark=1 +Ododeca3_dark_large.png dodeca3.pov

BLENDER = /Applications/Blender.app/Contents/MacOS/Blender

preview:
	QUAL=0 $(BLENDER) -b dodeca3.blend -P blender-render.py | python nicer-progress.py
	magick convert dodeca3_transparent.png -background white -alpha remove -flatten -alpha off dodeca3_light_preview.png
	magick convert dodeca3_transparent.png -background '#1f1f1f' -alpha remove -flatten -alpha off dodeca3_dark_preview.png

blend:
	QUAL=2 $(BLENDER) -b dodeca3.blend -P blender-render.py | python nicer-progress.py
	magick convert dodeca3_transparent.png -background white -alpha remove -flatten -alpha off dodeca3_light_large.png
	magick convert dodeca3_transparent.png -background '#1f1f1f' -alpha remove -flatten -alpha off dodeca3_dark_large.png

final:
	for size in $(SIZES); do \
		for kind in light dark; do \
			magick dodeca3_$${kind}_large.png -resize $${size} dodeca3_$${kind}_$${size}.jpg; \
		done \
	done

ico:
	for size in 16 32 48 64 96; do \
		border=$$((($${size}-1)/32+1)); \
		magick dodeca3_light_large.png -resize $$(($${size}-2*$$border)) -bordercolor black -border $$border dodeca3_light_$${size}.bmp; \
	done
	magick convert dodeca3_light_{16,32,48,64,96}.bmp dodeca3.ico

publish:
	cp dodeca3_*_*.jpg ../../pix

publish_ico:
	cp dodeca3.ico ../../pages/favicon.ico

clean:
	rm -f *.pov-state
	rm -f *.png *.jpg *.bmp *.ico
	rm -f *.blend1
