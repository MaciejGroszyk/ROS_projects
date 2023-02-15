import rospy
import math
import PyKDL

from rcprg_ros_utils import exitError
from velma_common import *
from rcprg_planner import *
import PyKDL
import rospy


def calc_frame_pose(frame, x, y, z):
    (_,_, yaw) = frame.M.GetRPY()
    pose_X = frame.p.x() + math.cos(yaw)*x - math.sin(yaw)*y
    pose_Y = frame.p.y() + math.sin(yaw)*x + math.cos(yaw)*y
    pose_Z = frame.p.z() + z
    angle = yaw - math.pi
    if angle < -math.pi:
        angle = 2*math.pi +angle
    return [pose_X, pose_Y, pose_Z, angle]

def makeWrench(lx,ly,lz,rx,ry,rz):
    return PyKDL.Wrench(PyKDL.Vector(lx,ly,lz), PyKDL.Vector(rx,ry,rz))


class CartImp:
    @staticmethod
    def init_cart_imp(velma):
        print("Cartesian impedance mode initialization")
        if not velma.moveCartImpRightCurrentPos(start_time=0.2):
            exitError(8)
        if velma.waitForEffectorRight() != 0:
            exitError(9)
    
        rospy.sleep(0.5)
    
        diag = velma.getCoreCsDiag()
        if not diag.inStateCartImp():
            print ("The core_cs should be in cart_imp state, but it is not")
            exitError(3)
    @staticmethod
    def set_impedance(velma, lin_x, lin_y, lin_z, ang_x, ang_y, ang_z):
        if not velma.moveCartImpRight(None, None, None, None, [makeWrench(lin_x, lin_y, lin_z, ang_x, ang_y, ang_z)], [2], PyKDL.Wrench(PyKDL.Vector(5,5,5), PyKDL.Vector(5,5,5)), start_time=0.5):
            exitError(1234)
        if velma.waitForEffectorRight() != 0:
            exitError(4321)
    @staticmethod
    def move_hand_to_position(velma, frame, x, y, z, angle, tol=1):

        [x_calc, y_calc, z_calc, angle_calc] = calc_frame_pose(frame, x, y, z)
        T_B_Trd = PyKDL.Frame(PyKDL.Rotation.RPY( 0.0 , 0.0 , angle_calc+angle), PyKDL.Vector(x_calc, y_calc,z_calc))
        if not velma.moveCartImpRight([T_B_Trd], [5.0], None, None, None, None, PyKDL.Wrench(PyKDL.Vector(5,5,5), PyKDL.Vector(5,5,5)), start_time=0.5, path_tol=PyKDL.Twist(PyKDL.Vector(tol,tol,tol), PyKDL.Vector(tol,tol, tol))):
            exitError(567)
        if velma.waitForEffectorRight() != 0:
            exitError(567)
        rospy.sleep(0.5)

    @staticmethod
    def move_directly_to_jar(velma, solver):
        # dX = 0.2
        gripper_frame = velma.getTf('B','Gr')
        jar_frame = velma.getTf('B', 'jar_hollow')
        distX = abs(gripper_frame.p.x() - jar_frame.p.x())
        distX = distX + 0.09

        time, velma_pos = velma.getLastJointState()
        configuration = (velma_pos['right_arm_0_joint'], velma_pos['right_arm_1_joint'], velma_pos['right_arm_2_joint'],
        velma_pos['right_arm_3_joint'], velma_pos['right_arm_4_joint'], velma_pos['right_arm_5_joint'], velma_pos['right_arm_6_joint'])
        frame = solver.getRightArmFk(velma_pos['torso_0_joint'], configuration)
        p = PyKDL.Vector(distX, 0, 0)
        p = frame * p
        frame.p = p
        if not velma.moveCartImpRight([frame], [2.0], None, None, None, None, PyKDL.Wrench(PyKDL.Vector(5,5,5), PyKDL.Vector(5,5,5)), start_time=0.5):
            exitError(16)
        if velma.waitForEffectorRight() != 0:
            exitError(17)
            
    @staticmethod
    def move_jar_back(velma, solver):
        distX = -0.05

        time, velma_pos = velma.getLastJointState()
        configuration = (velma_pos['right_arm_0_joint'], velma_pos['right_arm_1_joint'], velma_pos['right_arm_2_joint'],
        velma_pos['right_arm_3_joint'], velma_pos['right_arm_4_joint'], velma_pos['right_arm_5_joint'], velma_pos['right_arm_6_joint'])
        frame = solver.getRightArmFk(velma_pos['torso_0_joint'], configuration)
        p = PyKDL.Vector(distX, 0, 0)
        p = frame * p
        frame.p = p
        if not velma.moveCartImpRight([frame], [2.0], None, None, None, None, PyKDL.Wrench(PyKDL.Vector(5,5,5), PyKDL.Vector(5,5,5)), start_time=0.5):
            exitError(16)
        if velma.waitForEffectorRight() != 0:
            exitError(17)  


    @staticmethod
    def move_jar_up(velma, solver):
        distZ = 0.2
        time, velma_pos = velma.getLastJointState()
        configuration = (velma_pos['right_arm_0_joint'], velma_pos['right_arm_1_joint'], velma_pos['right_arm_2_joint'],
        velma_pos['right_arm_3_joint'], velma_pos['right_arm_4_joint'], velma_pos['right_arm_5_joint'], velma_pos['right_arm_6_joint'])
        frame = solver.getRightArmFk(velma_pos['torso_0_joint'], configuration)
        p = PyKDL.Vector(0, 0, distZ)
        p = frame * p
        frame.p = p
        if not velma.moveCartImpRight([frame], [2.0], None, None, None, None, PyKDL.Wrench(PyKDL.Vector(5,5,5), PyKDL.Vector(5,5,5)), start_time=0.5):
            exitError(16)
        if velma.waitForEffectorRight() != 0:
            exitError(17)