from lxml import html
import requests
import os.path
import hashlib
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def readLinks(inputFile):
    print("Reading links from file "+inputFile)
    with open(inputFile) as f:
        content = f.readlines()
    return [x.strip().split(";") for x in content if not x.startswith("#")]

def retrieveDataForLink(url):
    print("Retrieving data for link: "+url)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    return tree

def processCar(carData):
    adTitle = carData.xpath('div[@class="ResultsAdData"]//a[@class="Adlink"]//span/text()')
    adInfo = carData.xpath('div[@class="ResultsAdData"]//ul//li/text()')
    print("Ad title -->"+adTitle[0])
    print("Ad info -->")
    print(adInfo)
    result = [adTitle[0]]
    result.extend(adInfo)
    print("Result -->")
    print(result)
    return result

def processLink(url):
    print("Processing link...")
    data = retrieveDataForLink(url)
    print("Parsing link...")
    carsRaw = data.xpath('//div[@class="ResultsAd"]')
    carsParsed = []
    for car in carsRaw:
        print("Parsing car "+str(len(carsParsed)+1))
        carDataResult = processCar(car)
        print("Result for car:")
        print(carDataResult)
        carsParsed.append(carDataResult)
    print("Parsed cars are...")
    print(carsParsed)
    return carsParsed

def readPrevious(path):
    content = []
    print("Reading previously stored results from file: "+path)
    if os.path.isfile(path):
        with open(path) as f:
            content = f.readlines()
    else:
        print("File with results does not exist.")
    return content

def carHash(car):
    print("Hashing...")
    print(car)
    hash_object = hashlib.sha256(json.dumps(car, sort_keys=True).encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def storeHashes(data, path):
    file = open(path, 'w')
    for line in data:
        file.write("%s\n" % line)

def sendEmail(sender, reciever, username, password, serverAddr, data, tag):
    print("Sending email notification about new car...")
    server = smtplib.SMTP(serverAddr)
    server.ehlo()
    server.starttls()
    server.login(username,password)
    msg = MIMEMultipart('alternative')
    msg.set_charset('utf8')
    msg['FROM'] = sender
    msg['To'] = reciever
    msg['Subject'] = Header(("New car add was detected | "+tag).encode('utf-8'), 'UTF-8').encode()
    payloadRaw = "Car info:<br/><b>%s</b><br/><b>%s</b><br/><b>%s</b><br/><b>%s</b><br/><b>%s</b>" % (data[0], data[1], data[2], data[3], data[4])
    _attach = MIMEText(payloadRaw.encode('utf-8'), 'html', 'UTF-8')
    msg.attach(_attach)
    server.sendmail(sender, reciever, msg.as_string())
    server.close()

if __name__ == "__main__":
    print("Starting...")
    links = readLinks("input.txt")
    previous = readPrevious("previous.txt")
    current = []
    print("Found "+str(len(links))+" links in input file.")
    i = 0
    for tag, link in links:
        #Process link
        cars = processLink(link)
        print(str(len(cars))+" cars were found for link.")
        print(cars)
        #Check if there is stored result for add
        if(len(previous) > i):
            #check stored result of most recent add
            if not (str(carHash(cars[0])).strip() == previous[i].strip()):
                print("Car is new, send notification")
                sendEmail("xxx", "xxx", "xxx", "xxx", "smtp.gmail.com:587", cars[0], tag)
            else:
                print("Nothing has changed, nothing will be reported.")
        #create new hash
        current.append(carHash(cars[0]))
        i+=1
    #store new current values
    storeHashes(current, "previous.txt")

