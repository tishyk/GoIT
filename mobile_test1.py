import os
import re
import glob
import logging
import subprocess as sp


logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.DEBUG)
from time import sleep
from uiautomator import Adb

device_id = Adb().device_serial()

# Uncoment bellow data if not one device connected!
'''from uiautomator import Device
    device_id = '0123456789ABCDEF'
    d = Device(device_id)
    # adb get-serialno  for only one connected device
    # adb devices for multiconnection

adb shell pm list packages -f 
adb shell screencap /sdcard/screen.png
adb pull /sdcard/screen.png
adb rm /sdcard/screen.png
    
C:\Users\tishyk>adb shell input
usage: input ...
       input text <string>
       input keyevent <key code number or name>
       input tap <x> <y>
       input swipe <x1> <y1> <x2> <y2>    
 
http://publish.illinois.edu/weiyang-david/2013/08/08/code-numbers-for-adb-input/   
''' 



def getdata(apk_name,dirpath=''):
    "Application name should have no any spaces!!!"
    package_line = os.popen(dirpath+'aapt dump badging %s | findstr "package"'%apk_name).read()
    activity_line = os.popen(dirpath+'aapt dump badging %s | findstr "launchable-activity"'%apk_name).read()
    pet = re.compile("name='(.*?)'")
    package = pet.findall(package_line)[0]
    activity = pet.findall(activity_line)[0]
    return package, activity



def run_test():
    logging.info("--- Start Test ---")      
    sp.Popen('adb -s %s logcat -c' % device_id, shell=True)
    os.popen('adb -s %s install %s'%(device_id,apk_name))
    os.popen('adb -s %s shell am start -n %s/%s'%(device_id,package,activity))
    sleep(7)
    os.popen('adb -s %s shell input keyevent %s'%(device_id,5))
    os.popen('adb -s %s shell am start -n %s/%s'%(device_id,package,activity))
    sleep(2)   
    os.popen('adb -s %s shell input swipe 400 5 400 600'%(device_id))
    sleep(2)    
    os.popen('adb -s %s shell input swipe 400 1280 400 5'%(device_id))
    sleep(2)
    os.popen('adb -s %s shell input swipe 400 1000 400 200'%(device_id))
    sleep(2)    
    os.popen('adb -s %s shell input swipe 5 100 500 100'%(device_id))
    sleep(2)
    os.popen('adb -s %s shell input swipe 500 100 5 100'%(device_id))
    sleep(2)
    os.popen('adb -s %s shell input keyevent %s'%(device_id,4))

    os.popen('adb -s %s uninstall %s'%(device_id,package))
    sp.Popen('adb -s %s logcat -d>Log.txt' % (device_id), shell=True)

    logging.info("--- Test Finished! ---") 


if __name__ == "__main__":
    apk_names = glob.glob("*.apk")
    logging.debug(apk_names)
    #print getdata.func_doc
    for apk_name in apk_names:
            package, activity = getdata(apk_name)
            logging.debug("%s/%s"%(package, activity))
            run_test()
