import rclpy
import math
from rclpy.node import Node
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped

class OdomRecorder(Node):
    def __init__(self):
        super().__init__('odom_recorder')
        self.sub = self.create_subscription(
            Odometry, '/odom', self.on_odom, 10)
        self.path_pub = self.create_publisher(Path, '/robot_path', 10)
        self.path_msg = Path()
        self.path_msg.header.frame_id = 'odom'
        
        self.last_x = None
        self.last_y = None

    def on_odom(self, msg):
        p = msg.pose.pose.position
        
        if self.last_x is not None:
            dist = math.hypot(p.x - self.last_x, p.y - self.last_y)
            if dist < 0.05:
                return
            
        self.last_x = p.x
        self.last_y = p.y
        
        self.get_logger().info(f'x={p.x:.2f} y={p.y:.2f} z={p.z:.2f}')
        
        pose = PoseStamped()
        pose.header = msg.header
        pose.header.frame_id = 'odom'
        pose.pose = msg.pose.pose
        
        self.path_msg.header.stamp = self.get_clock().now().to_msg()
        self.path_msg.poses.append(pose)
        
        self.path_pub.publish(self.path_msg)
        
        
def main(args=None):
    rclpy.init(args=args)
    node = OdomRecorder()
    rclpy.spin(node)  
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()