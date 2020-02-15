from flask import Flask, flash, redirect, render_template, url_for, request
from flask_cors import CORS
import ibm_watson
from gtts import gTTS
import os
import re
import webbrowser
import smtplib
import requests,json
import urllib
import boto3
import os
import subprocess
import cv2
import googlemaps
from datetime import datetime
import analyze as az
from opencage.geocoder import OpenCageGeocode
from pprint import pprint
import requests
import nexmo

app = Flask(__name__)

CORS(app)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/print/name', methods=['POST', 'GET'])
def get_names():

    if request.method == 'POST':
        resp_json = request.get_json()
        command = resp_json['text']
        if 'villa' in command or 'billa' in command:
            command= 'okay loco'
        else:
            command= command
    assistant = ibm_watson.AssistantV1(
    version='',
    iam_apikey='',
    url=''
    )

    response = assistant.message(
        workspace_id='',
        input={
            'text': command
        }
    ).get_result()


    a=response
    b=a['intents']
    if b==[]:
        intent= 'nothing'
    else:
        intent = b[0]['intent']
    print('the intent is:' , intent)
    def currentloc():
        send_url = "http://api.ipstack.com/check?access_key="
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        latitude = geo_json['latitude']
        longitude = geo_json['longitude']
        return [latitude,longitude]

    if intent=='weather':
        latt,long = currentloc()
        endpoint = 'http://api.openweathermap.org/data/2.5/forecast?'
        api_key = ''

        nav_request = 'lat={}&lon={}&APPID={}'.format(latt, long, api_key)
        reequest = endpoint + nav_request
        response = urllib.request.urlopen(reequest).read().decode('utf-8')
        weather = json.loads(response)
        current_temp = weather['list'][0]['main']['temp']
        temp_c = current_temp - 273.15
        temp_c_str = str(int(temp_c)) + ' degree Celsius '
        descript_place = weather['list'][0]['weather'][0]['main']
        if descript_place == 'Clouds':
            descript_place = 'overcast'
        print('It is a little '+descript_place + ' and temperature outside is, ' + temp_c_str +" "+str(latt)+" "+str(long))
        return json.dumps({"response": 'It is a little '+descript_place + ' and temperature outside is, ' + temp_c_str+" "+str(latt)+" "+str(long)}), 200
    elif intent == 'call':

        print("tirgger")
        client = nexmo.Client(key='', secret='')
        client.send_message({'from': 'Nexmo', 'to': '+919082180627', 'text': 'Hello there, your patient needs your assistance please report immediately.'})
        {'message-count': '1', 'messages': [{'to': '+919082180627', 'message-id': '0D00000039FFD940', 'status': '0', 'remaining-balance': '14.62306950', 'message-price': '0.03330000', 'network': '12345'}]}
        return json.dumps({"response": "I will let your nurse know that you need their assistance"}), 200


    elif intent=='person':
        thisdict={
        1:"priyanka.jpeg",
        2:"sneha.jpg",


            }
        n=2
        f=0

        ch='y'
        while(ch=='y'):

            camera = cv2.VideoCapture(0)
            return_value, image = camera.read()
            cv2.imwrite('test.jpeg', image)
            del(camera)


            sourceFile='test.jpeg'
            for i in range(1,n+1):

                targetFile= thisdict[i]
                client=boto3.client('rekognition')

                imageSource=open(sourceFile,'rb')
                imageTarget=open(targetFile,'rb')

                response=client.compare_faces(SimilarityThreshold=70,SourceImage={'Bytes': imageSource.read()},TargetImage={'Bytes': imageTarget.read()})
                print(response)
                f=2
                for faceMatch in response['FaceMatches']:
                    f=1
                    nameee=''
                    for i in targetFile:
                        if i != '.':
                            nameee+=i
                        else:
                            break

                    os.remove("test.jpeg")
                    return json.dumps({"response": 'This is' + ' ' + nameee + ', '+ ' who\'s come to visit you! '
                            }), 200
                imageSource.close()
                imageTarget.close()
            if(f!=1):
                return json.dumps({"response": 'This person doesn\'t exist in our database. Would you like to add him? '
                            }), 200

    elif 'add' in command:
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite('new.jpeg', image)
        del(camera)
        namee= command[4::1]
        namee= namee+ ".jpeg"
        n=n+1
        os.rename("new.jpeg", namee)
        d1={n:namee}
        thisdict.update(d1)

    elif intent=='text':
        new=[]
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite('test1.jpeg', image)
        del(camera)

        s3 = boto3.resource('s3')
        images=[('test1.jpeg','test'),]

        for image in images:
            file = open(image[0],'rb')
            object = s3.Object('text-identifier',image[0])
            ret = object.put(Body=file,
                                Metadata={'Name':image[1]}
                                )



        bucket='text-identifier'
        photo='test1.jpeg'
        client=boto3.client('rekognition')
        response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
        textDetections=response['TextDetections']

        stuff=' '
        for text in textDetections:
            if(' ' in text['DetectedText']):
                stuff+= text['DetectedText'] +'\n'

        print(stuff)

        return json.dumps({"response": stuff}), 200

        s3.Object('aags-wheeler1', 'test1.jpeg').delete()

    elif intent=='news':
        def NewsFromBBC():
            global new
            new=[]
            main_url = "https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey="
            open_bbc_page = requests.get(main_url).json()
            article = open_bbc_page["articles"]
            results = []
            for ar in article:
                results.append(ar["title"])

            for i in range(0,3):
                stuff= str(str((i+1)) +'. '+ results[i])
                new.append(stuff)
            return new
        new = NewsFromBBC()
        news=' '
        for i in new:
            news+=i+',\n'+'\n'
        return json.dumps({"response": news})

    elif intent=='navigate_home':
        start=[-73.996,40.732]
        end=[-73.991,40.735]
        url = "https://api.mapbox.com/directions/v5/mapbox/walking/" + str(start[0]) + "," + str(start[1]) + ";" + str(end[0]) + "," + str(end[1]) + "?steps=true&geometries=geojson&access_token=pk.eyJ1IjoidGxhenlwYW5kYSIsImEiOiJjazZlZThiNDkxandsM2VtZ282dWhrNnpuIn0.MA9TNuCLK_rdaQVij5k6_w"
        results = requests.get(url)
        string =''
        print(results.json())
        result = results.json()
        steps = result['routes'][0]['legs'][0]['steps']
        for i in range(len(steps)):
            print(steps[i]['maneuver']['instruction'])
            string = string + str(i+1) + ". "+  steps[i]['maneuver']['instruction']+'\n'
        return json.dumps({"response":string})

    else:
        return json.dumps({"response":'Need some help go ahead'}), 200
if __name__=='__main__':


    key = ''
    geocoder = OpenCageGeocode(key)

    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=False)
