import roslib; roslib.load_manifest('velma_task_cs_ros_interface')

import rospy
import math
import PyKDL
from threading import Thread

from velma_common import *
from rcprg_planner import *
from rcprg_ros_utils import MarkerPublisher, exitError

from moveit_msgs.msg import AttachedCollisionObject, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose
from visualization_msgs.msg import Marker
import tf_conversions.posemath as pm

class MarkerPublisherThread:
    def threaded_function(self, obj):
        pub = MarkerPublisher("attached_objects")
        while not self.stop_thread:
            pub.publishSinglePointMarker(PyKDL.Vector(), 1, r=1, g=0, b=0, a=1, namespace='default', frame_id=obj.link_name, m_type=Marker.CYLINDER, scale=Vector3(0.02, 0.02, 1.0), T=pm.fromMsg(obj.object.primitive_poses[0]))
            try:
                rospy.sleep(0.1)
            except:
                break

        try:
            pub.eraseMarkers(0, 10, namespace='default')
            rospy.sleep(0.5)
        except:
            pass

    def __init__(self, obj):
        self.thread = Thread(target = self.threaded_function, args = (obj, ))

    def start(self):
        self.stop_thread = False
        self.thread.start()

    def stop(self):
        self.stop_thread = True
        self.thread.join()

class JarAttached:
    @staticmethod
    def init_jar_atached():
        object1 = AttachedCollisionObject()
        object1.link_name = "right_HandGripLink"
        object1.object.header.frame_id = "right_HandGripLink"
        object1.object.id = "object1"
        object1_prim = SolidPrimitive()
        object1_prim.type = SolidPrimitive.CYLINDER
        object1_prim.dimensions=[None, None]    # set initial size of the list to 2
        object1_prim.dimensions[SolidPrimitive.CYLINDER_HEIGHT] = 0.18
        object1_prim.dimensions[SolidPrimitive.CYLINDER_RADIUS] = 0.04
        object1_pose = pm.toMsg(PyKDL.Frame(PyKDL.Rotation.RotY(math.pi/2)))
        object1.object.primitives.append(object1_prim)
        object1.object.primitive_poses.append(object1_pose)
        object1.object.operation = CollisionObject.ADD
        object1.touch_links = ['right_HandPalmLink',
            'right_HandFingerOneKnuckleOneLink',
            'right_HandFingerOneKnuckleTwoLink',
            'right_HandFingerOneKnuckleThreeLink',
            'right_HandFingerTwoKnuckleOneLink',
            'right_HandFingerTwoKnuckleTwoLink',
            'right_HandFingerTwoKnuckleThreeLink',
            'right_HandFingerThreeKnuckleTwoLink',
            'right_HandFingerThreeKnuckleThreeLink']
    
        print("Publishing the attached object marker on topic /attached_objects")
        pub = MarkerPublisherThread(object1)
        pub.start()

        return object1