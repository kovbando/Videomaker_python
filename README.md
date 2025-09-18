# Videomaker_python
This python script takes in the output of the "LiDAR_multicam_multithread" application's output pictures, and makes a video from them. \
The output is a 2x2 grid of videos. 
The input files should be placed in a folder named `pictures` next to the script. 
Filenames must have theis numbers zero padded, so the `rename.py` script can help you with that. \
If there is a missing frame, it can be detected by looking at the indexes in the filename, however this quick video making script *does not care*. |
So if there are missing frames, the output video will become desynchronized.
For this script to work, you must have a copy of FFMPEG's static build next to the script, in a folder calledd `ffmpeg`.
For linux: https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
For windows: https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip
\
\
\
\
\
A kind warning: \
This code has been tested and working, but it was created by an unknown student, probbably vibecodding at the university based on the comments in the code.
Use it at you own risk.
