import rosbag
import math 
from scipy.spatial.transform import Rotation as R
import sys
import matplotlib.pyplot as plt

num=3 #wersja paczki

if num==1:
    paczka='../niska_predkosc.bag'
    xtrans=1.840
    ytrans=-0.629
    theta=-1.433 #kat w radianach
    o=-81.844 #kat w stopniach

if num==2:
    paczka='../srednia_predkosc.bag'
    
    xtrans=1.802
    ytrans=-0.675
    theta=-1.421 #radian
    o=-81.437

if num==3:
    paczka='../wysoka_predkosc.bag'
    
    xtrans=1.746
    ytrans=-0.695
    theta=-1.472 #radian
    o=-84.324

bag = rosbag.Bag(paczka)
bag1 = rosbag.Bag(paczka)

#inicjalizacja tabel
odomX=[]
odomY=[]
odomO=[]
poseX = []
poseY = []
poseO= []

i=0
for topic, msg, t in bag.read_messages(topics= 'mobile_base_controller/odom'):

    odomx=msg.pose.pose.position.x
    odomy=msg.pose.pose.position.y
    x = math.cos(theta)*(odomx)- math.sin(theta)*(odomy)
    y = math.sin(theta)*(odomx)+ math.cos(theta)*(odomy)
    
    odomX.append(x+xtrans)
    odomY.append(y+ytrans)

    quaternion= [
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w,
    ]
    r= R.from_quat(quaternion)
    r= r.as_euler('zyx', degrees=True)

    odomO.append(r[0]+o)

    i+=1
    
bag.close()

j=0
allErrX=[]
allErrY=[]
allErrO=[]
ErrX=0
ErrY=0
ErrO=0
for topic, msg, t in bag1.read_messages(topics= 'robot_pose'):
    poseX.append(msg.pose.pose.position.x)
    poseY.append(msg.pose.pose.position.y)
       

    if j<i:

        quaternion= [
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w,
        ]
        r= R.from_quat(quaternion)
        r= r.as_euler('zyx', degrees=True) 
        poseO.append(r[0]) 
        

        errX=abs(msg.pose.pose.position.x- odomX[j])
        errY=abs(msg.pose.pose.position.y- odomY[j])
        errO=abs(r[0]- odomO[j])
        if errO>340:
            errO= abs(errO-360)

        allErrX.append(errX)
        allErrY.append(errY)
        allErrO.append(errO)

        ErrX+=errX
        ErrY+=errY
        ErrO+=errO
        
        j+=1


print(paczka)
print("Bład całkowity położenia X: ", ErrX)
ErrX= ErrX/i
print("Średni błąd położenia X: ", ErrX)
print("Bład całkowity położenia Y: ", ErrY)
ErrY=ErrY/i
print("Średni błąd położenia Y: ", ErrY)
print("Bład całkowity rotacji: ", ErrO)
ErrO=ErrO/i
print("Średni błąd rotacji: ", ErrO)



plt.plot(odomX,odomY, 'r--', poseX,poseY)
plt.show()

