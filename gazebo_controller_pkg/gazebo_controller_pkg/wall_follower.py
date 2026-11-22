import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy

def safe_min(range_list):
    clean = []
    for r in range_list:
        if not math.isinf(r) and not math.isnan(r) and r > 0.05:
            clean.append(r)
    if len(clean) == 0:
        return 3.5 
    return min(clean)

class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')
        
        qos = QoSProfile(depth = 10, reliability=ReliabilityPolicy.BEST_EFFORT)
        
        self.sub = self.create_subscription(LaserScan, '/scan', self.on_scan, qos)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        
        self.state = 'FIND_WALL'
        self.get_logger().info('Start! Search wall...')

    def on_scan(self, msg):
        front = safe_min(msg.ranges[0:15] + msg.ranges[345:360])
#        left = safe_min(msg.ranges[80:100])
        right = safe_min(msg.ranges[260:280])

        cmd = Twist()

        if self.state == 'FIND_WALL':
            if front < 0.5:
                self.state = 'TURN_LEFT'
                self.get_logger().info('Wall, I turn left -> TURN_LEFT')
            elif right <= 1.0:
                self.state = 'FOLLOW_WALL'
                self.get_logger().info('Found wall -> FOLLOW_WALL')
                
        elif self.state == 'TURN_LEFT':
            if front > 0.7:
                self.state = 'FOLLOW_WALL'
                self.get_logger().info('Way is clear -> FOLLOW_WALL')
                
        elif self.state == 'FOLLOW_WALL':
            if front < 0.5:
                self.state = 'TURN_LEFT'
                self.get_logger().info('See obstacle -> TURN_LEFT')
            elif right > 1.0:
                self.state = 'FIND_WALL'
                self.get_logger().info('Wall is lost -> FIND_WALL')

        if self.state == 'FIND_WALL':
            cmd.linear.x = 0.12
            cmd.angular.z = -0.02
            
        elif self.state == 'TURN_LEFT':
            cmd.linear.x = 0.05
            cmd.angular.z = 0.5
            
        elif self.state == 'FOLLOW_WALL':
            cmd.linear.x = 0.16
            error = 0.4 - right
            turn_speed = 1.0 * error
            
            if turn_speed > 0.5: turn_speed = 0.5
            elif turn_speed < -0.5: turn_speed = -0.5
            
            cmd.angular.z = turn_speed
            
        self.pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()