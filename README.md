# Smart-Audio-Recorder
A smart audio recorder  implemented on a Raspberry Pi. 
The device consists of a Raspberry Pi, a USB mic, a button and two LEDs(red and green). When the button is pressed, a non-blocking audio streaming program running in the Raspberry Pi saves audio recordings in batch of  1 minutes per recording.  User can access the audio recording via SFTP if they are connected to same network with the Raspberry Pi  without interacting with the terminal/command line.
