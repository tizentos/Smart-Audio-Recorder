#add a shutdown button to free audio resources or port

import RPi.GPIO as GPIO
import pyaudio
import audio_script as aud
from time import  sleep
import datetime
import wave
import os 

GPIO.setmode(GPIO.BOARD)

#pin used 
pushButton = 10
recordLED =  11
stopRecordLED = 12


#make pin 10 pull-down
GPIO.setup(pushButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#setup  LED pins
GPIO.setup(recordLED,GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(stopRecordLED, GPIO.OUT, initial = GPIO.HIGH)


form_1 = pyaudio.paInt16
chans = 1
samp_rate = 44100
chunk = 4096
record_secs = 30

frames = []
recording = False
isActive = False
stream = None


homepath = os.path.expanduser("~/")

def main():
    print("New code:.....Now in main()")
    global stream
    global frames
    global isActive
    global recording
    # recording = GPIO.input(pushButton)
 #  instantiate PyAudio (1)
    audio = pyaudio.PyAudio()
    for ii in range(audio.get_device_count()):
        print(audio.get_device_info_by_index(ii).get('name'))

    #dev_index = input("Enter your preferred audio device index\n")
    dev_index = 1
    ##detect interrupt for rise/fall edge and debounce switch by 200ms
    GPIO.add_event_detect(pushButton, GPIO.RISING, callback = performAction,bouncetime = 1000)
    startTime = datetime.datetime.now()
    while True:
        #if not GPIO.input(pushButton):
        #    stopRecording(pushButton)
        print(recording)
        if recording:
          print("in recording")
          if not isActive:
              print("audio is not active")
              stream = audio.open(format = form_1, rate = samp_rate, channels = chans, \
                        input_device_index = dev_index, input = True, \
                        frames_per_buffer = chunk, stream_callback = callback)
              stream.start_stream()
              startTime = datetime.datetime.now()
              # stream,audio = aud.record(chans,samp_rate,form_1,record_secs,chunk)  
          else:
              print("audio is active")
              endTime = datetime.datetime.now()
              elapseTime = endTime - startTime
              print("%d seconds" % elapseTime.seconds)
              if elapseTime.seconds >= record_secs:
                   stream.stop_stream()
                   stream.close() 
                   save(chans,samp_rate,audio,form_1,frames)
                   frames = []     
                   isActive = False
        else:
           print("recording is false")
           if isActive:
              print("stream is active  when recording is false")
              stream.stop_stream()
              stream.close()
              #audio.terminate()  should be the last f-ing thing to do
              save(chans,samp_rate,audio,form_1,frames)
              frames = []
              isActive = False
        sleep(1)  

def performAction(channel):
    print("in gpio interrupt")
    global recording 
    recording = recording ^ GPIO.input(channel)
    if recording:
       startRecording(channel)
    elif not recording:
       stopRecording(channel)

def startRecording(channel):
    global recording
    print("start rec")
    GPIO.output(recordLED, GPIO.HIGH)
    GPIO.output(stopRecordLED, GPIO.LOW)
    recording = True

def stopRecording(channel):
    print("stop rec") 
    global recording
    GPIO.output(stopRecordLED, GPIO.HIGH)
    GPIO.output(recordLED, GPIO.LOW)
    recording = False 
    


# define callback (2)
def callback(in_data, frame_count, time_info, status):
    print("in audio callback")
    global isActive
    global frames
    isActive = True
    frames.append(in_data)
    return (None, pyaudio.paContinue)

def save(chans,samp_rate,audio,form_1,frames):


    print("saving voice recording")
    wav_output_filename = datetime.datetime.now().isoformat()[:-10] + '.wav'
    wav_output_filename = wav_output_filename.replace(":","-")
    saved_file = homepath+"recordings/"+wav_output_filename
    print(saved_file)

    wavefile = wave.open(saved_file, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    print("done")


if __name__ == "__main__":
    main()
