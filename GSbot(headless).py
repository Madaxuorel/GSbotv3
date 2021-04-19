

#Under MIT Licsence


#Imports 
import os
import requests
import discord
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os

from time import sleep
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from fp.fp import FreeProxy
from termcolor import colored



#Options of chrome browser, not activated by default
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--log-level=3")

#Bot class
class GSbot():
    def __init__(self):
        self.trusts = ''
        self.list = []
        self.driver =''
        self.msg = ''
        self.old = ''
        
        #flags
        self.tries = 0
        self.tunnel = 0
        self.captcha = 0
        self.success = 0

        
    #Check to see if a captcha is blocking the driver
    def captchacheck(self):
        sleep(5)
        try:
            self.driver.find_element_by_xpath('/html/body/form/div[4]/table/tbody/tr[2]/td[2]/div[2]/table/tbody/tr[2]/td[1]/span')
            return False
        except NoSuchElementException:#Captcha
            return True

    #Generates browser with new ip 
    def getbrowser(self):
        self.tries +=1
        self.proxy = FreeProxy(rand=True).get()
        while self.proxy in self.list:
            self.proxy = FreeProxy(rand=True).get()
        self.list.append(self.proxy)
        print('nouvelle ip  = {}'.format(self.proxy))    
        webdriver.DesiredCapabilities.CHROME['proxy']={
        "httpProxy":self.proxy,
        "ftpProxy":self.proxy,
        "sslProxy":self.proxy,    
        "proxyType":"MANUAL",
        }
        webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
        self.driver = webdriver.Chrome(executable_path= r"chromedriver.exe",chrome_options = chrome_options)
    #Search for trusts, with a new ip after every error
    def GSlast(self):
        trusts = []
        self.getbrowser()
        try:# if no ip error
            self.driver.get('https://icis.corp.delaware.gov/ecorp/entitysearch/namesearch.aspx')
            self.driver.find_element_by_xpath('/html/body/form/div[4]/table/tbody/tr[2]/td[2]/table[3]/tbody/tr[4]/td[1]/input').send_keys('Grayscale')
            self.driver.find_element_by_xpath('/html/body/form/div[4]/table/tbody/tr[2]/td[2]/table[4]/tbody/tr[1]/td/input').click()
            if self.captchacheck():#if captcha
                self.captcha +=1
                print('\nCaptcha :( Restart ...\n')
                self.driver.close()#Endpoint
                self.GSlast()
                
            else:#if no captcha
                i=0
                trusts = []
                while i < 50:
                    try:
                        trusts.append(self.driver.find_element_by_xpath('/html/body/form/div[4]/table/tbody/tr[2]/td[2]/div[2]/table/tbody/tr[{}]/td[2]/a'.format(i)).text)
                        i+=1
                    except NoSuchElementException:
                        i+=1
                self.trusts = (',').join(trusts)
                print('\nnew trusts : {}\n'.format(self.trusts))
                print('\nold trusts : {}\n'.format(self.old))
                if self.trusts != self.old: # if new trusts
                    diff = self.trusts.replace(self.old, '')
                    print('NEW TRUSTS')
                    self.msg = 'Nouveau trust, {}'.format(diff)
                    self.success +=1
                    self.writenew()
                    self.driver.close()#Endpoint
                elif self.trusts == self.old:
                    print('Rien de nouveau')
                    self.msg=''
                    self.driver.close()#Endpoint
        except WebDriverException: # If Ip error
            self.tunnel +=1
            print('\nBad ip :( Restart ...\n')
            self.driver.close()#Endpoint
            self.GSlast()
            


    def getolds(self):
        with open('trusts.txt', 'r') as fileread:
            self.old = fileread.read()
    
    def writenew(self):
        with open('trusts.txt','w') as filewrite:
            filewrite.write(self.trusts)
        
    
def main(client):
    @client.event
    
    async def on_ready(): #When bot ready (connects)
        bot = GSbot()#creates bot
        #inits bot
        bot.getolds()
        bot.GSlast()
        if bot.msg != '':
            await client.get_channel(829334620885090344).send(bot.msg + '<@&829124050197413900>')# if new trust, senbs msg
        elif bot.msg == '':
            print('\nRien de nouveau\n')
            print('flags :\n  tries : {} \n  captcha : {} \n  tunnel : {} \n  sucess : {} \n'.format(bot.tries, bot.captcha, bot.tunnel, bot.success))
            print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
        
client = discord.Client()
main(client)
client.run('ODI5MTE2NjM4MDI3NzEwNDc1.YGzdCg.I3VgOgX-MyWzlvPN5mxvz2thL-k')#Private token