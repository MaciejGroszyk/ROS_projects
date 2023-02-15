from velma_common import *
from init_wspaniala_velma import InitWspanialaVelma
from velma_kinematics.velma_ik_geom import KinematicsSolverVelma
from rcprg_ros_utils import exitError
from rcprg_planner import *
import math


class WorldScanner:

    torso_center = symmetricalConfiguration({'torso_0_joint': 0.0,})
    torso_left = symmetricalConfiguration({'torso_0_joint': -1.05,})
    torso_right = symmetricalConfiguration({'torso_0_joint': 1.05,})
    torso_leftleft = symmetricalConfiguration({'torso_0_joint': -1.3,})
    torso_rightright = symmetricalConfiguration({'torso_0_joint': 1.3,})
    torso_leftleftleft = symmetricalConfiguration({'torso_0_joint': -1.5,})
    torso_rightrightright = symmetricalConfiguration({'torso_0_joint': 1.5,})
    head_center = (0, 0)
    head_down = (0, 1.0)
    head_up = (0, -0.75)

    @staticmethod
    def move_torso(pos, time, velma):
        velma.moveJoint(pos, time, start_time=0.5, position_tol=10.0/180.0*math.pi)
        error = velma.waitForJoint()
        if error != 0:
            exitError(2, msg="The action should have ended without error,"\
                            " but the error code is {}".format(error))

    @staticmethod
    def move_head(pos, time, velma):
        velma.moveHead(pos, time, start_time=0.5)
        if velma.waitForHead() != 0:
            exitError(14)
        if not isHeadConfigurationClose( velma.getHeadCurrentConfiguration(), pos, 0.1 ):
            exitError(15)

    @staticmethod
    def scan_world(velma):
        print('Movint to starting position')
        WorldScanner.move_torso(WorldScanner.torso_center, 2.0, velma)
        print('Scanning center')
        WorldScanner.move_head(WorldScanner.head_up, 2.0, velma)
        WorldScanner.move_head(WorldScanner.head_down, 4.0, velma)
        WorldScanner.move_head(WorldScanner.head_center, 2.0, velma)
        print('Moving to left')
        WorldScanner.move_torso(WorldScanner.torso_left, 2.0, velma)
        print('Scanning left')
        WorldScanner.move_head(WorldScanner.head_up, 2.0, velma)
        WorldScanner.move_head(WorldScanner.head_down, 4.0, velma)
        WorldScanner.move_head(WorldScanner.head_center, 2.0, velma)
        print('Moving to left-left')
        WorldScanner.move_torso(WorldScanner.torso_leftleft, 1.0, velma)
        WorldScanner.move_head((-1.0, 0), 2.0, velma)
        print("Scanning left-left")
        WorldScanner.move_head((-1, -0.75), 2.0, velma)
        WorldScanner.move_head((-1, 1), 4.0, velma)
        WorldScanner.move_head(WorldScanner.head_center, 2.0, velma)
        print('Moving to right')
        WorldScanner.move_torso(WorldScanner.torso_right, 4.0, velma)
        print('Scanning right')
        WorldScanner.move_head(WorldScanner.head_up, 2.0, velma)
        WorldScanner.move_head(WorldScanner.head_down, 4.0, velma)
        WorldScanner.move_head(WorldScanner.head_center, 2.0, velma)
        print('Moving right-right')
        WorldScanner.move_torso(WorldScanner.torso_rightright, 1.0, velma)
        WorldScanner.move_head((1.0, 0), 2.0, velma)
        print('Scanning right-right')
        WorldScanner.move_head((1, -0.75), 2.0, velma)
        WorldScanner.move_head((1, 1), 4.0, velma)
        WorldScanner.move_head(WorldScanner.head_center, 2.0, velma)
        print('Moving to starting position')
        WorldScanner.move_torso(WorldScanner.torso_center, 2.0, velma)

if __name__ == "__main__":
    rospy.init_node('test_cimp_pose')
    initWspanialaVelma= InitWspanialaVelma()
    velma = initWspanialaVelma.velma_interface()
    WorldScanner.scan_world(velma)