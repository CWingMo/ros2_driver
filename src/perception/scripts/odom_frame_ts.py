#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster, TransformListener, Buffer
from geometry_msgs.msg import TransformStamped
import rclpy.time

class OdomRemapNode(Node):
    """
    将 TF 从 odom_wheel->base_link 重新映射为 odom->base_link
    方便导航模块使用标准的 odom 坐标系
    """
    def __init__(self):
        super().__init__('odom_remap_node')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.declare_parameter('source_odom', 'odom_wheel')
        self.declare_parameter('target_odom', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        self.source_odom = self.get_parameter('source_odom').value
        self.target_odom = self.get_parameter('target_odom').value
        self.base_frame = self.get_parameter('base_frame').value

        self.timer = self.create_timer(0.02, self.timer_callback)  # 50Hz

        self.get_logger().info(
            f"TF映射节点启动: {self.source_odom}->{self.base_frame} -> {self.target_odom}->{self.base_frame}"
        )

    def timer_callback(self):
        """定时查询 TF 并重新发布"""
        try:
            tf_now = self.tf_buffer.lookup_transform(
                self.source_odom, self.base_frame, rclpy.time.Time()
            )

            new_tf = TransformStamped()
            new_tf.header.stamp = self.get_clock().now().to_msg()
            new_tf.header.frame_id = self.target_odom
            new_tf.child_frame_id = self.base_frame
            new_tf.transform = tf_now.transform

            self.tf_broadcaster.sendTransform(new_tf)

        except Exception:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = OdomRemapNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
