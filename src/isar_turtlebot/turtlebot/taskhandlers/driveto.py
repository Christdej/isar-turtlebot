import time
from typing import Optional

from isar_turtlebot.config import config
from isar_turtlebot.models.turtlebot_status import Status
from isar_turtlebot.ros_bridge.ros_bridge import RosBridge
from isar_turtlebot.turtlebot.taskhandlers.taskhandler import TaskHandler
from isar_turtlebot.utilities.pose_message import encode_pose_message
from robot_interface.models.geometry.pose import Pose
from robot_interface.models.mission.task import DriveToPose, Task


class DriveToHandler(TaskHandler):
    def __init__(
        self,
        bridge: RosBridge,
        publishing_timeout: float = config.getfloat("mission", "publishing_timeout"),
    ) -> None:
        self.bridge = bridge
        self.publishing_timeout = publishing_timeout

    def start(
        self,
        task: DriveToPose,
    ) -> None:

        goal_pose: Pose = task.pose
        goal_id: Optional[str] = self._goal_id()

        pose_message: dict = encode_pose_message(pose=goal_pose)
        self.bridge.execute_task.publish(message=pose_message)

        start_time: float = time.time()
        while self._goal_id() == goal_id:
            time.sleep(0.1)
            if (time.time() - start_time) > self.publishing_timeout:
                raise TimeoutError("Publishing navigation message timed out")

    def _goal_id(self) -> Optional[str]:
        goal_id: str = self.goal_id_from_message(
            message=self.bridge.task_status.get_value()
        )
        return goal_id

    def get_status(self) -> Status:
        status: Status = self.status_from_message(
            message=self.bridge.task_status.get_value()
        )
        return status