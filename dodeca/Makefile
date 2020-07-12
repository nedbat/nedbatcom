.PHONY: test large final clean

SMALL = 300
LARGE = 3840
SIZES = 60 200 640

test:
	povray +W$(SMALL) +H$(SMALL) Declare=Dark=0 +Ododeca3_light.png dodeca3.pov
	povray +W$(SMALL) +H$(SMALL) Declare=Dark=1 +Ododeca3_dark.png dodeca3.pov

large:
	povray +W$(LARGE) +H$(LARGE) Declare=Dark=0 +Ododeca3_light_large.png dodeca3.pov
	povray +W$(LARGE) +H$(LARGE) Declare=Dark=1 +Ododeca3_dark_large.png dodeca3.pov

final:
	for size in $(SIZES); do \
		for kind in light dark; do \
			magick dodeca3_$${kind}_large.png -resize $${size} dodeca3_$${kind}_$${size}.jpg; \
		done \
	done

publish:
	cp dodeca3_*_*.jpg ../pix

clean:
	rm -f *.pov-state *.png *.jpg
