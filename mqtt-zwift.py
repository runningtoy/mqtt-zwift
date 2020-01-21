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

def filter_gen(signal,n,avgsum,max_n):
   #http://www.lothar-miller.de/s9y/archives/25-Filter-in-C.html
   if n<max_n:
      n=n+1
      avgsum += signal
      return avgsum/n
   else:
      avgsum -= avgsum/max_n
      avgsum += signal
      return avgsum/max_n
   return Null
   
def filter_PT1(oldVal,NewVal, Periode, Tau):
   #http://www.lothar-miller.de/s9y/archives/25-Filter-in-C.html
   FF=Tau/Periode
   return ((oldVal * FF) + NewVal) / (FF +1)

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

   
   
   #players(world.players)

   if check_online(world.players):
       last_distance = -1
       last_altitude = -1
       last_slope=0
       avgsum_Slope=0
       cnt_Slope = 0
	   
       avgsum_altitude=0
       cnt_altitude = 0
       avgsum_distance=0
       cnt_distance = 0
	   
       pt1_altitude=0
       pt1_distance = 0
       t_sleep = 1.2	   	   
       slope = 0
	 
       #fp=open("values.txt","a+")
       while(True):
         #fp=open("values.txt","a+")
         try: 
           status = world.player_status(player_id)
           error = 0
           #fp=open("values.txt","a+")		   
         except:
           error += 1
           #print("error while retrieving player status. Error count = " + str(error))
           if error > 5:
              #fp.close()
              break 
         if status.sport == 0:
             #Filter input signals
             tmp_distance=filter_gen(status.distance,cnt_distance, avgsum_distance,2.8)
             tmp_altitude=filter_gen(status.altitude,cnt_altitude, avgsum_altitude,2.8)
			 
			 #PT1 Filter
             pt1_distance=filter_PT1(pt1_distance,status.distance,t_sleep,0.25)
             pt1_altitude=filter_PT1(pt1_altitude,status.altitude,t_sleep,0.25)
             #tmp_distance=pt1_distance
             #tmp_altitude=pt1_altitude
             #tmp_distance=status.distance
             #tmp_altitude=status.altitude
			 
             if(last_distance == -1 ):
                last_distance=tmp_distance
             if(last_altitude == -1 ):
                last_altitude=tmp_altitude
             
             run=tmp_distance-last_distance
             rise=tmp_altitude-last_altitude
             
             #last_distance=tmp_distance
             #last_altitude=tmp_altitude

             try: 
                slope = (((rise) / (run)))
                last_distance=tmp_distance
                last_altitude=tmp_altitude
                last_slope=slope
             except:
                slope = last_slope
                print("Error: filterSlope(((rise) / (run)))")
             #slope = filter_gen(slope,cnt_Slope, avgsum_Slope,2)
             print("-------------------")
             print(tmp_distance)
             print(tmp_altitude)
             print(run)
             print(rise)
             print(slope)
             ##fp.write('%s,%s,%s,%s,%s\n' % (tmp_distance, tmp_altitude, run, rise,slope))
			 
             #msg_dict = { 'is_online': 1, 'sport': 'cycling', 'hr': status.heartrate, 'power': status.power,  'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) } 
             msg_dict = { 'is_online': 1, 'sport': status.sport, 'hr': status.heartrate, 'power': status.power,  'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) , 'calories':status.calories,'altitute':float("{:.2f}".format(tmp_altitude)),'cadenceUHz':float("{:.2f}".format(float(status.cadenceUHz)*60/1000000)),'distance':float("{:.2f}".format(tmp_distance)), 'slope':float("{:.2f}".format(slope))}
         elif status.sport == 1:   
             #msg_dict = { 'is_online': 1, 'sport': 'running', 'hr': status.heartrate, 'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) } 
             msg_dict = { 'is_online': 1, 'sport': status.sport, 'hr': status.heartrate, 'power': status.power,  'speed': float("{:.2f}".format(float(status.speed)/1000000.0)) , 'calories':status.calories,'altitute':float("{:.2f}".format(tmp_altitude)),'cadenceUHz':float("{:.2f}".format(float(status.cadenceUHz)*60/1000000)),'distance':float("{:.2f}".format(tmp_distance)), 'slope':float("{:.2f}".format(slope))}
         mqtt_client.publish(mqtt_topic, payload=json.dumps(msg_dict), retain=False)
         time.sleep(t_sleep)
   else:
         #print("not online yet")
         mqtt_client.publish(mqtt_topic, payload=OFFLINE_MSG, retain=False)
   time.sleep(60)
