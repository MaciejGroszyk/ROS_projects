#test_jimp_planning.py
 
import roslib; roslib.load_manifest('velma_task_cs_ros_interface')

import rospy
import math
import PyKDL

from velma_common.velma_interface import VelmaInterface, isConfigurationClose,\
    symmetricalConfiguration
from control_msgs.msg import FollowJointTrajectoryResult
from rcprg_ros_utils import exitError
from rcprg_planner import *

# joint impedance move
class MoveHand():
    # define some configurations
    # q_map_starting = {'torso_0_joint':0, 'right_arm_0_joint':-0.3, 'right_arm_1_joint':-1.8,
    #      'right_arm_2_joint':1.25, 'right_arm_3_joint':0.85, 'right_arm_4_joint':0, 'right_arm_5_joint':-0.5,
    #      'right_arm_6_joint':0, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
    #      'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }
 
    # q_map_goal = {'torso_0_joint':0, 'right_arm_0_joint':-0.3, 'right_arm_1_joint':-1,
    #      'right_arm_2_joint':-1.25, 'right_arm_3_joint':0.85, 'right_arm_4_joint':0, 'right_arm_5_joint':-0.5,
    #      'right_arm_6_joint':0, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
    #      'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }
    q_map_starting = {'torso_0_joint':0, 'right_arm_0_joint':-0.3, 'right_arm_1_joint':-1.8,
        'right_arm_2_joint':1.25, 'right_arm_3_joint':0.85, 'right_arm_4_joint':0, 'right_arm_5_joint':-0.5,
        'right_arm_6_joint':0, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
        'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }

    q_map_goal = {'torso_0_joint':1, 'right_arm_0_joint':-0.3, 'right_arm_1_joint':-1.8,
        'right_arm_2_joint':1.25, 'right_arm_3_joint':0.85, 'right_arm_4_joint':0, 'right_arm_5_joint':-0.5,
        'right_arm_6_joint':0, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
        'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }

    q_map_goals = []    
    def init_move(self, velma, p):
        diag = velma.getCoreCsDiag()
        if not diag.motorsReady():
            print("Motors must be homed and ready to use for this test.")
            exitError(1)

        if velma.enableMotors() != 0:
            exitError(3)

        print("Switch to jnt_imp mode (no trajectory)...")
        velma.moveJointImpToCurrentPos(start_time=0.5)
        error = velma.waitForJoint()
        if error != 0:
            print("The action should have ended without error, but the error code is", error)
            exitError(4)

        # print("Checking if the starting configuration is as expected...")
        # rospy.sleep(0.5)
        # js = velma.getLastJointState()
        # if not isConfigurationClose(self.q_map_starting, js[1], tolerance=0.2):
        #     print("This test requires starting pose:")
        #     print(self.q_map_starting)
        #     exitError(10)
    def fill_in_q_map_goals(self, IK, torso_angle, velma):
        if IK != None or len(IK)!=0:
            self.q_map_goals= []
            dict_joint_limits= self.__get_body_joint_limits(velma)
            for i in range(0, len(IK)):
                q_map_goal = {'torso_0_joint':torso_angle[i], 'right_arm_0_joint':IK[i][0], 'right_arm_1_joint':IK[i][1],
                    'right_arm_2_joint':IK[i][2], 'right_arm_3_joint':IK[i][3], 'right_arm_4_joint':IK[i][4], 'right_arm_5_joint':IK[i][5],
                    'right_arm_6_joint':IK[i][6],  'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
                'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }
                
                if (not self.__delete_ik_close_to_joints_limit(dict_joint_limits, q_map_goal)):
                    self.q_map_goals.append(q_map_goal)

            if len(self.q_map_goals)== 0:
                return False
            else:
                return True
        else:
            print('nie przeksztalcilo ik')
            return False
        return True

    #zwraca limity stawowow
    def __get_body_joint_limits(self, velma):
        dict_joint_limits= velma.getBodyJointLimits()
        return dict_joint_limits

    #zwraca True jesli za blisko limitow
    def __delete_ik_close_to_joints_limit(self, dict_joint_limits, q_map_goal):
        tolerance =0.1
        for key, value in q_map_goal.items():
            if dict_joint_limits[key][0] + tolerance > value:
                return True
            if dict_joint_limits[key][1] - tolerance < value:
                return True
        return False
        
    def move_all_body_to_goal(self, velma, p, object1=None):
        print("Moving to valid position, using planned trajectory.")
        goal_constraint_1=[]
        for goal in self.q_map_goals:
            goal_constraint_1.append(qMapToConstraints(goal, 0.01, group=velma.getJointGroup("impedance_joints")))
        for i in range(15):
            rospy.sleep(0.5)
            js = velma.getLastJointState()
            print("Planning (try", i, ")...")
            if object1==None:
                traj = p.plan(js[1], goal_constraint_1, "impedance_joints", num_planning_attempts=10, max_velocity_scaling_factor=0.15, planner_id="RRTConnect")
            else:
                traj = p.plan(js[1], goal_constraint_1, "impedance_joints", num_planning_attempts=10, max_velocity_scaling_factor=0.15, planner_id="RRTConnect", attached_collision_objects=[object1])
            
            if traj == None:
                continue
            print("Executing trajectory...")
            if not velma.moveJointTraj(traj, start_time=0.5, position_tol=10.0/180.0 * math.pi, velocity_tol=10.0/180.0*math.pi):
                exitError(5)
            if velma.waitForJoint() == 0:
                return True
            else:
                print("The trajectory could not be completed, retrying...")
                continue

        return False

    def move_all_body_to_start(self, velma, p, object1=None):
        print("Moving to valid position, using planned trajectory.")
        goal_constraint_1 = qMapToConstraints(self.q_map_starting, 0.01, group=velma.getJointGroup("impedance_joints"))
        for i in range(15):
            rospy.sleep(0.5)
            js = velma.getLastJointState()
            print("Planning (try", i, ")...")
            if object1==None:
                traj = p.plan(js[1], [goal_constraint_1], "impedance_joints", num_planning_attempts=10, max_velocity_scaling_factor=0.15, planner_id="RRTConnect")
            else:
                traj = p.plan(js[1], [goal_constraint_1], "impedance_joints", num_planning_attempts=10, max_velocity_scaling_factor=0.15, planner_id="RRTConnect", attached_collision_objects=[object1])


            if traj == None:
                continue
            print("Executing trajectory...")
            if not velma.moveJointTraj(traj, start_time=0.5, position_tol=10.0/180.0 * math.pi, velocity_tol=10.0/180.0*math.pi):
                exitError(5)
            if velma.waitForJoint() == 0:
                return True
            else:
                print("The trajectory could not be completed, retrying...")
                continue

        return False
