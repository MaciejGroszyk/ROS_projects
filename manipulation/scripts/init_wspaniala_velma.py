
import roslib; roslib.load_manifest('velma_task_cs_ros_interface')
import rospy
import PyKDL

from velma_common import *
from rcprg_ros_utils import exitError
from rcprg_planner import *


class InitWspanialaVelma():

    def velma_interface(self):
        #uruchomienie interfejsu Velmy
        velma = VelmaInterface()
        #oczekiwanie na inizjalizacje VelmaInterface
        if not velma.waitForInit(timeout_s=10.0):
            print("Could not initialize VelmaInterface\n")
            exitError(1)
        print("Initialization ok!\n")

        print("Motors must be enabled every time after the robot enters safe state.")
        print("If the motors are already enabled, enabling them has no effect.")
        print("Enabling motors...")
        if velma.enableMotors() != 0:
            exitError(14)

        print("Also, head motors must be homed after start-up of the robot.")
        print("Sending head pan motor START_HOMING command...")
        velma.startHomingHP()
        if velma.waitForHP() != 0:
            exitError(14)
        print("Head pan motor homing successful.")

        print("Sending head tilt motor START_HOMING command...")
        velma.startHomingHT()
        if velma.waitForHT() != 0:
            exitError(15)
        print("Head tilt motor homing successful.")

        return velma


    def  planer_with_octomap(self, velma):
        p = Planner(velma.maxJointTrajLen())
        p.waitForInit()
        oml = OctomapListener("/octomap_binary")
        rospy.sleep(1.0)
        octomap = oml.getOctomap(timeout_s=5.0)
        p.processWorld(octomap)
        return p