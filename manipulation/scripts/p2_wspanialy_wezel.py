#!/usr/bin/env python
from pickle import NONE
import roslib; roslib.load_manifest('velma_task_cs_ros_interface')
import roslib; roslib.load_manifest('velma_task_cs_ros_interface')
import rospy
import math
import sys
from velma_common import *
from rcprg_ros_utils import exitError
from cart_imp import CartImp
from move_grip import moveGriper
from init_wspaniala_velma import InitWspanialaVelma
from move_hand import MoveHand
from inverse_kinematics import InverseKinematics
from two_tables_one_jar import MoveJarToTable
from velma_kinematics.velma_ik_geom import KinematicsSolverVelma
from jar_attached import JarAttached
from world_scan import WorldScanner





if __name__ == "__main__":



    state= 0
    while state!=13:

        if state== -1:
            print("ERROR.. RESTART REQUIRED")
            sys.exit(-1)

        #inicjalizacja wezla oraz welmy
        if state==0:
            print('STATE 0: VELMA INITIALIZATION')
            print('START')

            #utworzenie wezla
            rospy.init_node('moj_wspanialy_wezel', anonymous=False)
            rospy.sleep(1)

            #inicjalizacja velmy
            initWspanialaVelma= InitWspanialaVelma()
            velma = initWspanialaVelma.velma_interface()
             
            #inicjalizowanie potrzebnych klas
            mG= moveGriper() #zamykanie i otwieranie griperow
            moveHand= MoveHand() 
            solver = KinematicsSolverVelma()
            inverseKinematics= InverseKinematics()
            moveJarToTable= MoveJarToTable()
            print('END')
            state=1

        #zamkniecie griperow
        if state==1:
            print('STATE 1: CLOSING GRIPPERS')
            mG.close_gripper(velma)
            mG.close_gripper(velma, side='left')

            if(len(sys.argv)>1):
                state=2 
            else: state=3

        #skanowanie mapy -wersja online
        if state==2:
            print('STATE 2: WORLD SCANNING - ONLINE')
            WorldScanner.scan_world(velma)
            state=3
        

        #inicjalizacja plannera
        if state==3:
            print('STATE 3: PLANNER INITIALIZATION')

            T_B_Jar = velma.getTf('B', 'right_handle')
            if T_B_Jar== NONE:
                state = -1
            planner= initWspanialaVelma.planer_with_octomap(velma)
            print('HEY.. I WILL BE MOVING SOON')
            state=4
        
        #ruch do poczatkowej pozycji
        if state==4:
            print('STATE 4: IM TRYING TO REACH STARTING POSITION')
            if(moveHand.move_all_body_to_start(velma, planner)):
                print('STARTING POSITION REACHED')
                state=5
            else:
                print('I CANT REACH STARTING POSITION')
                state=-1

        #liczenie odwrotnej kinematyki
        if state==5:
            print('STATE 5: IM CALCULATING INVERSE KINEMATICS')
            T_B_Wr= inverseKinematics.T_B_Wr_aroud_goal( T_B_Jar.p, velma)
            IK, torso_angle = inverseKinematics.my_Ik(T_B_Wr)

            if len(IK)!=0:
                print('INVERSE KINEMATICS CALCULATED')
                state=6
            else:
                print('I CANT CALCULATE INVERSE KINEMATICS')
                state=-1

        #pubslisher TFA
        # while True:
        #     pub = rospy.Publisher('punkty_do_okolo',PoseStamped, queue_size=10)
        #     rate = rospy.Rate(10) # 10hz
        #     msg = PoseStamped()
        #     for i in range(0, len(T_B_Wr)):
        #         msg.header.frame_id = "world"
        #         msg.pose.position.x= T_B_Wr[i].p.x()
        #         msg.pose.position.y= T_B_Wr[i].p.y()
        #         msg.pose.position.z= T_B_Wr[i].p.z()
        #         msg.pose.orientation.x= T_B_Wr[i].M.GetQuaternion()[0]
        #         msg.pose.orientation.y= T_B_Wr[i].M.GetQuaternion()[1]
        #         msg.pose.orientation.z= T_B_Wr[i].M.GetQuaternion()[2]
        #         msg.pose.orientation.w= T_B_Wr[i].M.GetQuaternion()[3]
        #         #czas
        #         rospy.sleep(0.2)
        #         pub.publish(msg)
        #     print('juz udostepniam')
        #koniec pubslisher TFA

        
        #ruch w poblize raczki
        if state==6:
            print('STATE 6: MOVING CLOSE TO THE HANDLE')
            if (moveHand.fill_in_q_map_goals(IK, torso_angle, velma)):
                moveHand.init_move(velma, planner)
                if (moveHand.move_all_body_to_goal(velma, planner)):
                    print('GOAL REACHED')
                    state=7
                    rospy.sleep(0.5)
                else:
                    print('I CANT REACH GOAL')
                    print('I WILL BACK TO STARTING POSITION AND TRY AGAIN')
                    state=4

            else:
                print('TRAJECTORIES CLOSE TO JOINT LIMIT WAS DELETED')
                print('THERE ARE NO TRAJECTORIES')
                state= -1

        #lapanie drzwi i otwieranie ich
        if state == 7:
            print('STATE 7: TRYING TO CATCH THE HANDLE')
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.35, 0.2, 0.15, 0, 0)
            mG.three_fingers_conf(velma, 'right')
            rospy.sleep(4)
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.25, 0.2, 0.15, 0, 0)
            CartImp.set_impedance(velma, 500,500,500,500,500,500)
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.25, -0.01, 0.15, 0, 0)
            print('STATE 7: OPENING')
            CartImp.set_impedance(velma, 100,100,200,100,100,100)
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.40, -0.01, 0.15, 0 )
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.75, 0.1, 0.15, 0 )
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.75, 0.28, 0.15, 0 )
            state= 8


        if state == 8:
            print('STATE 8: MOVING TO STARTING POSITION')
            CartImp.move_hand_to_position(velma, T_B_Jar, 0.25, 0.5, 0.15, 0 )
            
            moveHand.init_move(velma, planner)
            mG.close_gripper(velma)
            if (moveHand.move_all_body_to_start(velma, planner)):
                print('I FINISHED MY JOB. TIME TO GET SOME REST')
                state= 13
            else:
                state= -1

        #otworzenie reki, inicjalizacja ruchu kartezjanskego
        # podjechanie do obiektu, lapanie obiektu