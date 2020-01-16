#!/bin/python

from zwift import Client
import paho.mqtt.client as mqtt
import time
import json

# i know... this is not elegant!
from settings import *

OFFLINE_MSG = json.dumps({ 'is_online': 0, 'sport': 0.0, 'hr': 0.0, 'power': 0.0,  'speed': 0.0 , 'calories':0.0,'altitute':0.0,'cadenceUHz':0.0,'distance':0.0, 'slope':0.0}
)

def check_online(players):

   is_online = filter(lambda person: person['playerId'] == player_id, world.players['friendsInWorld'])   
 
   if len(is_online) > 0:
      return True
   else:
      return False

def players(players):
    
    for player in players['friendsInWorld']:
       print(player)

if __name__ == "__main__":


   mqtt_client = mqtt.Client(mqtt_client_name)
   mqtt_client.username_pw_set(mqtt_login, mqtt_pw)
   mqtt_client.will_set(mqtt_topic_will, payload="Offline", retain=True)
   mqtt_client.connect(mqtt_host_name)
   mqtt_client.publish(mqtt_topic_will, payload="Online", retain=True)

   client = Client(username, password)
   world = client.get_world(1)

   last_distance = -1
   last_altitude = -1
   
   #players(world.players)

   if check_online(world.players):
       while(True):
         try: 
           status = world.player_status(player_id)
           error = 0 
         except:
           error += 1
           #print("error while retrieving player status. Error count = " + str(error))
           if error > 5:
              break 
         if status.sport == 0:
             if(last_distance == -1 ):
                last_distance=status.distance
             if(last_altitude == -1 ):
                last_altitude=status.altitude

             run=status.distance-last_distance
             rise=status.altitude-last_altitude
             slope = (rise / (run*1000)) x 100

             #msg_dict = { 'is_online': 1, 'sport': 'cycling', 'hr': status.heartrate, 'power': status.power,  'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) } 
             msg_dict = { 'is_online': 1, 'sport': status.sport, 'hr': status.heartrate, 'power': status.power,  'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) , 'calories':status.calories,'altitute':status.altitude,'cadenceUHz':float("{:.2f}".format(float(status.cadenceUHz)*60/1000000)),'distance':status.distance, 'slope':slope}
         elif status.sport == 1:   
             #msg_dict = { 'is_online': 1, 'sport': 'running', 'hr': status.heartrate, 'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) } 
             msg_dict = { 'is_online': 1, 'sport': status.sport, 'hr': status.heartrate, 'power': status.power,  'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) , 'calories':status.calories,'altitute':status.altitude,'cadenceUHz':float("{:.2f}".format(float(status.cadenceUHz)*60/1000000)),'distance':status.distance, 'slope':slope}
         mqtt_client.publish(mqtt_topic, payload=json.dumps(msg_dict), retain=False)
         time.sleep(.31)
   else:
         #print("not online yet")
         mqtt_client.publish(mqtt_topic, payload=OFFLINE_MSG, retain=False)
   time.sleep(60)
