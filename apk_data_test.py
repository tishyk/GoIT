#! coding: utf-8

import os
import re
import glob
import time
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL)
logging.disable(logging.DEBUG)

class AppData():
    def __init__(self,apk_name,device_id=''):
        if not device_id:
            self.device_id = os.popen('adb get-serialno').read().strip()
        self.apk = apk_name
        self.getdata()
        os.popen('mkdir Logs')
        logging.info('\nApplication name: %s\nPackage: %s\nActivity: %s'\
                     %(self.apk,self.package,self.activity) )
        
    def getdata(self,dirpath=''):
        package_line = os.popen(dirpath+'aapt dump badging %s | findstr "package"'%self.apk).read()
        logging.debug('package_line is %s'%package_line)
        activity_line = os.popen(dirpath+'aapt dump badging %s | findstr "launchable-activity"'%self.apk).read()
        logging.debug('activity_line is %s'%activity_line)    
        pet = re.compile("name='(.*?)'")
        self.package = pet.findall(package_line)[0]
        self.activity = pet.findall(activity_line)[0]
        
class ApkTest(AppData):
    log_clean = lambda self: os.popen('adb -s %s logcat -c'%self.device_id )
    log_save = lambda self: os.popen('adb -s %s logcat -d>Logs%sLogs_%s.txt'\
                                    %(self.device_id,os.sep,self.apk.replace('.apk','')) )
        
    install_apk = lambda self: os.popen('adb -s %s install %s'%(self.device_id,self.apk))
    uninstall_apk = lambda self: os.popen('adb -s %s uninstall %s'%(self.device_id,self.package))
    run_keycode = lambda self,keycode: os.popen('adb -s %s shell input keyevent %s'%(self.device_id,keycode))
    run_apk = lambda self: os.popen('adb -s %s shell am start -n %s/%s'\
                                      %(self.device_id,self.package,self.activity))

    def check_activity(self):
        time.sleep(5)# change to activity waiting
        state = os.popen('adb -s %s shell dumpsys window | findstr mCurrentFocus'%self.device_id).read()
        logging.info(state)
        if self.activity in state:
            self.run_keycode('4')
            return True
        else:
            if 'Error' in state:
                self.run_keycode('66 66')
            self.log_save()
            return False
            
    def test_activity(self):
        self.log_clean()
        self.install_apk()
        logging.debug(self.run_apk().read())
        result = self.check_activity()
        print "Test result: %s"%result
        self.uninstall_apk()                                   
        return result
            
if __name__ == "__main__" :
    apk_list = glob.glob('*.apk')
    for apk in apk_list:
        appdata = ApkTest(apk)
        print apk, apk_list.index(apk)+1,'from',len(apk_list)
        result= appdata.test_activity()
        with open('result.txt','a+') as f:
            f.write('%s\t%s\n'%(result,apk))
            f.flush()
        print '-'*80
                         

