
import rospy
import math
from rcprg_ros_utils import exitError

class moveGriper():
    def close_gripper(self, velma, side='right'):
        gr_cmd='close'
        if gr_cmd == 'close':
            q = [math.radians(110), math.radians(110), math.radians(110), 0]
            velma.moveHand(side, q, [1, 1, 1, 1], [4000,4000,4000,4000], 1000, hold=False)
        else:
            raise Exception('Unknown gripper command: "{}"'.format(gr_cmd))
        if velma.waitForHand(side) != 0:
            exitError(6)
    def open_gripper(self, velma, side='right'):
        gr_cmd='open'
        if gr_cmd == 'open':
            q = [0, 0, 0, 0]
            velma.moveHand(side, q, [1, 1, 1, 1], [4000,4000,4000,4000], 1000, hold=False)
        else:
            raise Exception('Unknown gripper command: "{}"'.format(gr_cmd))

    
    def three_fingers_conf(self, velma, side='right'):
        gr_cmd='open'
        if gr_cmd == 'open':
            q = [math.radians(90), math.radians(90), math.radians(90), math.radians(180)]
            velma.moveHand(side, q, [1, 1, 1, 1], [4000,4000,4000,4000], 1000, hold=False)
        else:
            raise Exception('Unknown gripper command: "{}"'.format(gr_cmd))
