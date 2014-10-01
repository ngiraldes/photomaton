#!/usr/bin/python
# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.graphics import *
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
#from kivy.uix.progressbar import ProgressBar
from functools import partial
import RPi.GPIO as GPIO
import os
import re
from PIL import Image
import shutil
import glob
import sys

##led control
from LedStrip_WS2801 import LedStrip_WS2801



##Force screen size
#Config.set('graphics', 'fullscreen', 'fake')
#Config.set('graphics', 'width', '800')
#Config.set('graphics', 'height', '480')
#Config.write()

Builder.load_string("""
<ready>:    
    Button:
        background_color: (0,0,0,1)
        text: "Appuyez sur l'écran pour commencer"
        #color: (0,0,0,1)
        text_size: self.size
        font_size: 80
        bold: 'true'
        halign: 'center'
        valign: 'middle'
        on_press: app.start()
        
<steady>:
    Label:
        text: "Préparez-vous !"
        color: (1,1,1,1)
        text_size: self.size
        font_size: 100
        bold: 'true'
        halign: 'center'
        valign: 'middle'
        
<count5>:
    Label:
        text: "5"
        color: (0,0,1,1)
        text_size: self.size
        font_size: 400
        bold: 'true'
        halign: 'center'
        valign: 'middle'

<count4>:
    Label:
        text: '4'
        color: (1,1,0,1)
        text_size: self.size
        font_size: 400
        bold: 'true'
        halign: 'center'
        valign: 'middle'
        
<count3>:
    Label:
        text: '3'
        color: (1,.6,0,1)
        text_size: self.size
        font_size: 400
        bold: 'true'
        halign: 'center'
        valign: 'middle'
        
<count2>:
    Label:
        text: '2'
        color: (1,.4,0,1)
        text_size: self.size
        font_size: 400
        bold: 'true'
        halign: 'center'
        valign: 'middle'
        
<count1>:
    Label:
        text: '1'
        color: (1,0,0,1)
        text_size: self.size
        font_size: 400
        bold: 'true'
        halign: 'center'
        valign: 'middle'
        
<photos>:     
    Image:
        source: '13504.jpg'
        keep_ratio: 'true'
        allow_stretch: 'false'

<finish>
    Label:
        text: "C'est fini !"
        color: (1,1,1,1)
        text_size: self.size
        font_size: 150
        bold: 'true'
        halign: 'center'
        valign: 'middle'

<montage>
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Montage en cours...'
            color: (1,1,1,1)
            text_size: self.size
            font_size: 100
            bold: 'true'
            halign: 'center'
            valign: 'middle'
        #ProgressBar:
            #value: 50
            #max: 100        
""")

#################################################
# set variables
#################################################
pictures_folder = "/media/camera/DCIM/"
bgpicture_file = "/home/pi/photomaton/fond.jpg"
temp_folder = "/home/pi/photomaton/temp/"
output_folder = "/home/pi/photomaton/montages/"

#################################################
# Check everything before starting
#################################################
# Check temp folder if not create it
if not os.access(temp_folder, os.W_OK):
    print("create missing temp folder")
    os.mkdir(temp_folder)

# check output folder if not create it
if not os.access(output_folder, os.W_OK):
    #print("create missing output folder")
    os.mkdir(output_folder)

# Check background picture
if not os.access(bgpicture_file, os.R_OK):
    sys.exit("ERROR: Missing background picture or bad path => " + bgpicture_file)

#################################################    
#GPIO Setup
################################################# 
GPIO.setmode(GPIO.BCM)
#GPIO 23 for shutter
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, False)
#GPIO 24 for USB mount
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, False)
#GPIO 25 for focus
GPIO.setup(25, GPIO.OUT)
GPIO.output(25, False)


#Function to set GPIO port state
#where port is gpio port number and state can be True for up and False for down.
def gpio_set(port, state, *largs):
    GPIO.output(port, state)


#Functions to control leds
def led_flash(lednbr):
    for i in range(0, lednbr):
        ledStrip.setPixel(i, [255, 255, 255])
        ledStrip.update()
        time.sleep(0.01)

def led_off(lednbr):
    for i in range(0, lednbr):
        ledStrip.setPixel(i, [0, 0, 0])
        ledStrip.update()
        time.sleep(0.01)


# Declare all screens
class ready(Screen):
    pass
        
class steady(Screen):
    pass
  
class count5(Screen):
    pass
  
class count4(Screen):
    pass
      
class count3(Screen):
    pass
      
class count2(Screen):
    pass
      
class count1(Screen):
    pass
      
class photos(Screen):
    pass
    
class finish(Screen):
    pass
    
class montage(Screen):
    pass
    
#################################################
#   Start of main App
#################################################

class MainApp(App):
    ################################################
    #listLastModified
    #Parameters:dirPath(string),maxFiles(int),pattern(string) and optional
    #dirPath : Directory to inspect
    #maxFiles : Max last updated files to return
    #pattern : optional regular expression to match (Ex : "\.jpg$" for filename extension .jpg)
    #Return a list containing last maxFiles updated
    #################################################
    def listLastModified(self, dirPath,maxFiles,pattern="\w"):
        print("fonction lasfiles")
        # Liste contenant l'ensemble des fichiers
        allFiles=[]

        for root,_,files in os.walk(dirPath,followlinks=False):
            for fileName in files:
                if re.search(pattern, fileName):
                    allFiles.extend([os.path.join(root,fileName)])

        allFiles.sort(key=os.path.getmtime,reverse=True)
        return(allFiles[:maxFiles])

    '''def wake_camera(*largs):
        Clock.schedule_once(partial(gpio_set, 25, True))
        Clock.schedule_once(partial(gpio_set, 25, False), 2)'''

    def take_picture(*largs):
        Clock.schedule_once(partial(gpio_set, 23, True))
        Clock.schedule_once(partial(gpio_set, 23, False), 0.7)

    def light_on(*largs):
        Clock.schedule_once(partial(led_flash, 10))

    def light_off(*largs):
        Clock.schedule_once(partial(led_off, 10))
        
    def start(self, *args):
        print('start !!!!!!!!!!')
        print('----------------')    
        #Clock.schedule_once(self.wake_camera)
        self.root.current = 'steady'
        Clock.schedule_once(self.light_on)
	Clock.schedule_once(self.prepa, 5)

    def prepa(self, *args):
        #print(dir(self.root))
        self.num = 6
        Clock.schedule_once(self.light_off)
        Clock.schedule_interval(self.countdown, 1)
        
    def countdown(self, *args):
        print('countdown !!!!!!')
        print('----------------')
        self.num = self.num - 1
        self.root.current = "count" + str(self.num)
        if self.num == 1:
            Clock.unschedule(self.countdown)
            Clock.schedule_once(self.photos_screen, 1)
        
    def photos_screen(self, *args):
        print('photos !!!!!')
        print('----------------')        
        self.root.current = 'photos'
        self.photoshoot = 4
        Clock.schedule_once(led_flash, 10)
        Clock.schedule_once(self.take_picture, 1)
        Clock.schedule_interval(self.photos_shoot, 3)
        
    def photos_shoot(self, *args):
        self.photoshoot = self.photoshoot - 1
        Clock.schedule_once(self.take_picture)
        if self.photoshoot == 0:
            Clock.unschedule(self.photos_shoot)
            Clock.schedule_once(self.finish_screen)            
        
    def finish_screen(self, *args):
        print('finish !!!!')
        print('----------------')                
        self.root.current = 'finish'
        GPIO.output(24, True)
        Clock.schedule_once(self.montage_screen, 3)
            
    def montage_screen(self, *args):
        print('montage !!!!!')
        print('-----------------')
        #self.root.current = 'montage'
        if os.access(pictures_folder, os.R_OK):
        #Copy youngest 4 jpg files from camera
            for fileName in self.listLastModified(pictures_folder,4,"\.JPG"):
                shutil.copy(fileName,temp_folder)
            GPIO.output(24, False)

        # List pictures in temp dir
        pictures_files = os.listdir(temp_folder)
        #print('pictures files:')
        #print(pictures_files)

        # Open pictures
        os.chdir(temp_folder)
        picture1 = Image.open(pictures_files[0])
        picture2 = Image.open(pictures_files[1])
        picture3 = Image.open(pictures_files[2])
        picture4 = Image.open(pictures_files[3])

        # Remove .jpg of filenames for new filename
        out = "photomaton-" + pictures_files[0][:-4] +"-"+ pictures_files[1][:-4] +"-"+ pictures_files[2][:-4] +"-"+ pictures_files[3]
        # Check if file exist
        if os.access(output_folder + out, os.R_OK):
            sys.exit("ERROR: Montage yet exist => " + out)
            #print(out)

        # Make the montage
        bgpicture = Image.open(bgpicture_file)
        bgpicture.paste(picture1,(100,200))
        bgpicture.paste(picture2,(2248,200))
        bgpicture.paste(picture3,(100,1736))
        bgpicture.paste(picture4,(2248,1736))
        bgpicture.save(output_folder + out)

        #Clean temporary folder
        for f in pictures_files:
            #print( f + " deleted")
            os.remove(f)
    
        #Go back to first screen
        self.root.current = 'ready'

#################################################
#   End of main App
#################################################

    def build(self):
        # Create the screen manager
        #print("load manager")
        manager = ScreenManager()
        manager.add_widget(ready(name='ready'))
        manager.add_widget(steady(name='steady'))
        manager.add_widget(count5(name='count5'))
        manager.add_widget(count4(name='count4'))
        manager.add_widget(count3(name='count3'))
        manager.add_widget(count2(name='count2'))
        manager.add_widget(count1(name='count1'))
        manager.add_widget(photos(name='photos'))
        manager.add_widget(finish(name='finish'))
        manager.add_widget(montage(name='montage'))      
        return manager
 
if __name__ == '__main__':
    MainApp().run()
    
if KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
