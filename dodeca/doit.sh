size=3840
povray +W${size} +H${size} Declare=Dark=0 +Ododeca3_light_large.png dodeca3.pov
povray +W${size} +H${size} Declare=Dark=1 +Ododeca3_dark_large.png dodeca3.pov

for size in 60 200 640; do
    for kind in light dark; do
        magick dodeca3_${kind}_large.png -resize ${size} dodeca3_${kind}_${size}.jpg
    done
done
