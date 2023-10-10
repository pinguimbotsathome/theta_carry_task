#!/usr/bin/env python3

import rospy
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Twist
from theta_speech.srv import SpeechToText
from std_msgs.msg import Empty, String
import sys
import os
import rospkg
import time

PACK_DIR = rospkg.RosPack().get_path("theta_carry_my_luggage_task")

hotword_pub = rospy.Publisher('/hotword_activate', Empty, queue_size=1)
tts_pub  = rospy.Publisher('/textToSpeech', String, queue_size=10)
face_pub = rospy.Publisher('/hri/affective_loop', String, queue_size=10)
pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

def follow_me(data):

    rospy.logwarn("start follow")

    if "torso" in data.transforms[0].child_frame_id:
        torso_x = data.transforms[0].transform.translation.x #mais perto do robô fica negativo, mais longe do robô fica positivo
        torso_y = data.transforms[0].transform.translation.y #esquerda fica positivo, direita fica negativo
        
        distancia_seguranca = 0.8
        multiplicador_vel_lin_x = 0.4  
        multiplicador_vel_ang_z = 0.9  #0.8

        ex = torso_x - distancia_seguranca
        ey = torso_y 

        lin_x = 0.0
        ang_z = 0.0

        if ex < 0.0:
            lin_x = ex * 8.0
        elif ex < 0.0:
            lin_x = 0.0
        else:
            lin_x = multiplicador_vel_lin_x * ex
        
        if ey < 0.0:
            ang_z = multiplicador_vel_ang_z * ey 
        else:
            ang_z = multiplicador_vel_ang_z * ey * 1.5
            
        cmd_vel = Twist()
        cmd_vel.linear.x = lin_x
        cmd_vel.angular.z = ang_z
        follow = pub.publish(cmd_vel)

        return follow

def task_procedure(self):

    rospy.logwarn("start task")
    
    tts_pub.publish('Please put both bags carefully in the green mark next to red button, PLEASE dont touch the botton')
    face_pub.publish('littleHappy')
    time.sleep(10)

    while(confirmation != 'confirmation'):
        face_pub.publish('follow')
        tts_pub.publish('Please stand in the front of the sensor for the calibration as show in the imagem')
    
    time.sleep(1)
    face_pub.publish('confirmation')
    time.sleep(0.5)
    face_pub.publish('littleHappy')
    tts_pub.publish('Ok, we can go')

    follow_me()

    if(walk != 'walk'):
        while(confirmation != 'confirmation'):
            face_pub.publish('follow')
            tts_pub.publish('Sorry, I lost you, please stand in the front of the sensor again for the calibration as show in the imagem')
    else:
        follow_me()
        
def return_to_arena():

    rospy.logwarn("retorn")

    tts_pub.publish('OK')
    face_pub.publish('littleHappy')
    time.sleep(4)

    #navegação para retornar pra arena

    face_pub.publish('happy')
    tts_pub.publish('Finish task')

if __name__ == "__main__":
    rospy.init_node('carry_my_luggage_task_node', anonymous=True)

    rospy.Subscriber('tf', TFMessage, follow_me)

    confirmation = rospy.Subscriber('/tracker/confirmation', Empty, task_procedure) 
    walk = rospy.Subscriber('/tracker/confirmation', Empty, task_procedure) 
    rospy.Subscriber("hotword", Empty, return_to_arena)

    while not rospy.is_shutdown():
        pass