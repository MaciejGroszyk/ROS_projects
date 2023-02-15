import rospy
from nav_msgs.msg import  Odometry
from geometry_msgs.msg import Twist
import math
from scipy.spatial.transform import Rotation as R
import sys

start_position = (100, 10)

#wspolcynniki predkosci
lin_ang= True # True- lin False- ang
a= 1
lin_vel = a* 0.05
ang_vel = a* 0.12

#square
distance_goal= 4
angle_goal= 90
current_angle= 0
start_angle= 0
clockwise_turning = False
#flaga prawdziwa tylko podczas odebrania pierwszej wiadomosci
start = True
i = 0

def callback(data):
    global pub, rate, start_position, lin_ang, lin_vel, ang_vel, distance_goal, angle_goal, current_angle, start_angle, start, i
    msg = Twist()
    x= data.pose.pose.position.x
    y= data.pose.pose.position.y

    #pobieranie pozycji startowej
    if (start):
        start_position = (x, y)
        start = False
    print("Start position: ", start_position)

    distance_from_last_vertex = math.sqrt((x-start_position[0])**2 +(y-start_position[1])**2 )

    quaternion= [
        data.pose.pose.orientation.x,
        data.pose.pose.orientation.y,
        data.pose.pose.orientation.z,
        data.pose.pose.orientation.w,
    ]

    r= R.from_quat(quaternion)
    r= r.as_euler('zyx', degrees=True)
    
    if(i<4):
        if (lin_ang):
            if(distance_goal> distance_from_last_vertex):
                msg.linear.x= lin_vel
                msg.angular.z= 0
            else:
                lin_ang= not lin_ang
                start_position = (x, y)
                current_angle= 0
                start_angle= r[0]

        else:       
            if(angle_goal>= current_angle):
                msg.linear.x= 0
                msg.angular.z= -ang_vel if (clockwise_turning) else ang_vel
                # current_angle+= abs(abs(abs(r[0])- abs(start_angle))- abs(current_angle))
                current_angle = abs(r[0] - start_angle)
                if (current_angle>180):
                    current_angle-= 360
                    current_angle = abs(current_angle)
            else:
                lin_ang= not lin_ang
                current_angle= 0
                start_position = (x, y)
                start_angle= r[0]
                i+=1
        print("Clock wise turning: ", clockwise_turning)
        print("currnet ang vel: ", msg.angular.z)
        print(current_angle)
        print(distance_from_last_vertex)
        print(r)
    pub.publish(msg)



def listener():
    global pub

    rospy.init_node('stero_listener', anonymous=True)
    rospy.sleep(2)
    rospy.Subscriber("mobile_base_controller/odom", Odometry, callback)
    pub = rospy.Publisher('key_vel', Twist, queue_size=10)
    odom = Odometry()
    
    print(odom.pose.pose.orientation)
    rospy.spin()




if __name__ == '__main__':

    # podawanie argumentow obok komendy:
    #  argument 1 - dlugosc boku,
    #  agrument 2 - zmiana kierunku obortu robota (0 - ruch zgonie z ruchem wskazowek zegar,  inna liczba - przeciwnie)

    if (len(sys.argv)>1):
        distance_goal = float(sys.argv[1])
        print("Side length: ", distance_goal)
        if(len(sys.argv)>2):
            clockwise_turning = True if (sys.argv[2] == "0") else False

    listener()

