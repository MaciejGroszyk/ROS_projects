#!/usr/bin/env python
# license removed for brevity
import rospy
from math import pi
from geometry_msgs.msg import Twist

def talker():
    pub = rospy.Publisher('key_vel', Twist, queue_size=10)
    rospy.init_node('stero_vel_pub', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    
    #czas
    rospy.sleep(2)
    time_start = rospy.get_time()

    #wspolcynniki predkosci
    lin_ang= True # True- lin False- ang
    a= 1
    lin_vel = a* 0.05
    ang_vel = a* 0.12

    rotation_time= (pi/2)/ ang_vel
    linear_time= 4/ lin_vel

    i = 0
    while not rospy.is_shutdown():
        time_now = rospy.get_time()
        msg = Twist()
        
        interval = (time_now- time_start)
        if (i <4):
            if (lin_ang):
                if(linear_time>= interval):
                    msg.linear.x= lin_vel
                    msg.angular.z= 0
                else:
                    lin_ang= not lin_ang
                    
                    time_start = rospy.get_time()
                    interval= 0

            if (not lin_ang):       
                if(rotation_time>= interval):
                    msg.linear.x= 0
                    msg.angular.z= ang_vel
                else:
                    lin_ang= not lin_ang
                    interval= 0
                    time_start = rospy.get_time()
                    i+=1
       
        rospy.loginfo(msg)
        pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass