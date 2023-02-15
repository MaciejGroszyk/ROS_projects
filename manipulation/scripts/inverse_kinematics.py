import rospy
import copy
import cv2
import PyKDL
import math
import numpy as np
import random

from visualization_msgs.msg import *
from sensor_msgs.msg import JointState

from rcprg_ros_utils.marker_publisher import *
from velma_kinematics.velma_ik_geom import KinematicsSolverLWR4, KinematicsSolverVelma



class InverseKinematics():

    #obliczanie wektora wynikow odwrotnej kinematyki, tylko dla prawej reki
    #wybierana jest ostatnia poprawna
    def my_Ik(self, T_B_Wrs):
        solver = KinematicsSolverVelma()
        my_Iks= []
        torso_angles_ik= []
        side_str='right'

        for torso_angle in np.linspace(1.0, -1.0, 8):
            for elbow_circle_angle in np.linspace(1.55, -1.55, 8):
                for T_B_Wr in T_B_Wrs:
                    ik = solver.calculateIkRightArm( T_B_Wr, torso_angle, elbow_circle_angle, False, False, False)
                    if None not in ik:
                        my_Iks.append(ik)
                        torso_angles_ik.append(torso_angle)
        return my_Iks, torso_angles_ik


    def T_B_Wr_aroud_goal(self, point, velma, R=0.15, z_1=0.0):
        angle_step=math.pi/8

        steps = int(round(2*math.pi/angle_step))
        T_B_Wr = []
        for step in range(steps):
            angle = angle_step * step
            x = point.x() + R * math.cos(angle)
            y = point.y() + R * math.sin(angle)
            z = point.z()+z_1
            roll = 0.0
            pitch = 0.0
            yaw = self.correct_angle(math.pi + angle) #tylko obrot wokol osi z
            rotation = PyKDL.Rotation.RPY(roll, pitch, yaw)
            vector = PyKDL.Vector(x, y, z)
            frame =  PyKDL.Frame(rotation, vector) * PyKDL.Frame(PyKDL.Rotation.RPY(0,math.pi/2,0))
            # frame =  PyKDL.Frame(rotation, vector) * PyKDL.Frame(PyKDL.Rotation.RPY(0,math.pi/2,0)) * PyKDL.Frame(PyKDL.Rotation.RPY(0,0,math.pi))
            T_B_Wr.append(frame*velma.getTf('Gr', 'Wr'))

        return T_B_Wr

    def correct_angle(self, angle):
        angle =  angle % (2*math.pi)
        angle = (angle + 2*math.pi) % (2*math.pi)
        if angle > math.pi:  
            angle =angle- 2*math.pi
        return angle


        