import os
import re
import glob
import logging
import subprocess as sp


logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
from time import sleep
from uiautomator import device as d
from mobile_test1 import device_id as device_id

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
    xml = d.dump()
    d.press(5)
    d.press.back()
    d(scrollable=True).fling()
    d(scrollable=True).fling.vert.backward()
    d(className='android.widget.RelativeLayout')[9].child(
        className='android.widget.CheckBox').click()
    d(text='viber').sibling(className='android.widget.CheckBox').click()
    logging.info("--- Test Finished! ---")


if __name__ == "__main__":
    apk_names = glob.glob("*.apk")
    logging.debug(apk_names)
    #print getdata.func_doc
    for apk_name in apk_names:
            package, activity = getdata(apk_name)
            logging.debug("%s/%s"%(package, activity))
            run_test()
