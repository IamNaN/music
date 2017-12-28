#!/usr/bin/env python
# ssh -R 52698:localhost:52698 root@10.0.1.9
# password: musicbox
# rmate music.py
# rmate music.ini
# rmate /opt/musicbox/startup.sh
# rmate /music/playlists/ROTS.m3u
# rmate /var/log/musicbox_startup.log
# rmate /etc/rc.local
#
import RPi.GPIO as GPIO
import os
import time
import ConfigParser

LRoAPin = 23
LRoBPin = 17
LRoPPin = 27
RRoPPin = 24
volume = 50
track = 0
config = ConfigParser.ConfigParser()
config.read('music.ini')

flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0

def setup():
  global config
  global volume
  global track
  global localtrack

  volume = config.getint('DEFAULT', 'volume')
  track = config.getint('DEFAULT', 'track')
  localtrack = config.getint('DEFAULT', 'localtrack')

  GPIO.setmode(GPIO.BCM)         # Numbers GPIOs by chip location
  GPIO.setup(LRoAPin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)    # input mode
  GPIO.setup(LRoBPin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(LRoPPin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(RRoPPin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

  setVolume(volume)
  os.system('mpc -q clear')
  os.system('mpc -q single off')
  os.system('mpc -q random off')
  os.system('mpc -q repeat off')
  os.system('mpc -q consume off')
  os.system('mpc -q add file:///music/sounds/start.mp3')
  os.system('mpc -q play')
  queueTrack(track)

  with open('music.ini', 'wb') as configfile:
    config.write(configfile)

def playLocal():
  global config
  global track
  global localtrack

  localtrack = localtrack + 1
  if localtrack > 607:
    localtrack = 1

  config.set('DEFAULT', 'localtrack', localtrack)
  with open('music.ini', 'wb') as configfile:
    config.write(configfile)

  os.system('mpc -q clear')
  os.system('mpc -q load ROTS')
  os.system("mpc -q play %d" % localtrack)
  queueTrack(track)
  time.sleep(1)

def changeTrack(extra):
  global config
  global track

  track = track + 1
  if track > 4:
    track = 0

  print "Track %d selected" % track

  os.system('mpc -q clear')
  os.system('mpc -q add file:///music/sounds/ding.mp3')
  os.system('mpc -q play')
  queueTrack(track)

  config.set('DEFAULT', 'track', track)
  with open('music.ini', 'wb') as configfile:
    config.write(configfile)
  time.sleep(1)

def queueTrack(t):
  if t == 0:
    os.system('mpc -q insert http://dir.xiph.org/listen/5456/listen.m3u')
  elif t == 1:
    os.system('mpc -q insert http://files.hawaiipublicradio.org/hpr1.m3u')
  elif t == 2:
    os.system('mpc -q insert http://www2.kuow.org/stream/kuowhb.m3u')
  elif t == 3:
    os.system('mpc -q insert http://quarrel.str3am.com:7040/live-aac.m3u')
  else:
    os.system('mpc -q insert http://wsdownload.bbc.co.uk/worldservice/meta/live/shoutcast/mp3/eieuk.pls')
  print "Track %d added" % t

def changeVolume(direction):
  global volume
  global config

  volume = volume + direction
  volume = 0 if volume < 0 else volume
  volume = 100 if volume > 100 else volume
  setVolume(volume)
  config.set('DEFAULT', 'volume', volume)
  with open('music.ini', 'wb') as configfile:
    config.write(configfile)

def setVolume(v):
  if v > 90:
    v = 90
  os.system("mpc -q volume %d" % v)

def rotaryDeal():
  global flag
  global Last_RoB_Status
  global Current_RoB_Status
  Last_RoB_Status = GPIO.input(LRoBPin)
  while(not GPIO.input(LRoAPin) and not GPIO.input(LRoPPin) and not GPIO.input(RRoPPin)):
    if GPIO.input(LRoPPin):
      time.sleep(0.3)
      changeTrack(0)
    elif GPIO.input(RRoPPin):
      playLocal()
    else:
      Current_RoB_Status = GPIO.input(LRoBPin)
      flag = 1
  if flag == 1:
    flag = 0
    if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
      changeVolume(1)
    if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
      changeVolume(-1)

def loop():
  while True:
    rotaryDeal()

def destroy():
  GPIO.cleanup()             # Release resource

setup()
# GPIO.add_event_detect(LRoPPin, GPIO.RISING, callback=changeTrack, bouncetime=500)

if __name__ == '__main__':     # Program start from here
  try:
    loop()
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    destroy()

