import roslib; roslib.load_manifest('velma_task_cs_ros_interface')
import roslib; roslib.load_manifest('velma_task_cs_ros_interface')
import rospy
import math
import PyKDL
from velma_common import *
from rcprg_ros_utils import exitError

from inverse_kinematics import InverseKinematics

class MoveJarToTable():
    #params
    tolerance= 0.1

    #box 2 params
    box_2_X=0.1
    box_2_Y=0.1
    box_2_Z=0.2

    #table a params
    table_a_leg_Z= 0.71
    table_a_top_Z= 0.04
    table_a_X= 0.9
    table_a_Y= 0.6
    table_a_Z= table_a_leg_Z+table_a_top_Z

    #table b params
    table_b_leg_Z= 0.71
    table_b_top_Z=0.04
    table_b_X= 1.04
    table_b_Y= 0.6
    table_b_Z= table_b_leg_Z+table_b_top_Z


    table_Z= table_b_Z +0.13 #dodatkowe przesuniecie stolu w gore
    table_X= table_b_Y

    def who_wants_to_get_the_jar(self, velma):
        T_B_Jar = velma.getTf('B', 'jar_hollow')
        tb_A = velma.getTf('B', 'table_a')
        tb_B = velma.getTf('B', 'table_b')
        if self.get_distance(T_B_Jar.p, tb_A.p) < self.get_distance(T_B_Jar.p, tb_B.p):
            return 'table_b'
        else:
            return 'table_a'

    def get_distance(self, vec1, vec2):
        dist= math.sqrt( (vec1.x()-vec2.x())**2+ (vec1.y()-vec2.y())**2+ (vec1.z()-vec2.z())**2 )
        return dist

    def get_Ik_for_table(self, velma):
        R= self.table_X/2 - self.tolerance
        Z= self.table_Z +0.01 + self.box_2_Z/2
        IKtable= InverseKinematics()

        table_name= self.who_wants_to_get_the_jar(velma)
        T_B_Table = velma.getTf('B', table_name)
        T_B_Wr_Table= IKtable.T_B_Wr_aroud_goal( T_B_Table.p, velma, R, Z)
        IK, torso_angle = IKtable.my_Ik(T_B_Wr_Table)

        return IK, torso_angle, T_B_Wr_Table

