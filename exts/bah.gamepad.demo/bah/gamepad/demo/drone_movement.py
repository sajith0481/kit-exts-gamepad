import omni.kit.commands
from pxr import Sdf, Gf, UsdGeom, Usd
import omni


class DroneMovementHandler:
    def __init__(self, stage, prim_path="/World/iris"):
        self.stage = stage
        self.prim_path = prim_path
        self.prim = self.stage.GetPrimAtPath(self.prim_path)
        self.xform = UsdGeom.Xformable(self.prim)

    def update_drone_movement(self, throttle, yaw, pitch, roll):
        # Get the current transformation of the drone
        try:
            local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        except Exception as e:
            self.prim = self.stage.GetPrimAtPath("/World/iris")
            self.xform = UsdGeom.Xformable(self.prim)
            local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()

        # Handle Yaw (rotation around Y-axis)
        yaw_speed_factor = 1  # simple temp value
        new_yaw = yaw * yaw_speed_factor  # Assuming 'yaw' is in degrees already

        # Handle Pitch (rotation around X-axis)
        pitch_speed_factor = 1  # Simple temp value
        new_pitch = pitch * pitch_speed_factor  # Assuming 'pitch' is in degrees already

        # Handle Roll (rotation around Z-axis)
        roll_speed_factor = 1  # Simple temp value
        new_roll = roll * roll_speed_factor  # Assuming 'roll' is in degrees already

        # Handle Throttle (translation along the up vector)
        drone_up_vector = Gf.Vec3d(0, 1, 0)  # No need for Vec4d since we don't use the w component
        move_direction = drone_up_vector.GetNormalized()
        throttle_speed_factor = 1  # simple temp value
        move_step = move_direction * throttle * throttle_speed_factor
        offset_mat = Gf.Matrix4d().SetTranslate(move_step)
        new_transform = local_transformation * offset_mat
        translate: Gf.Vec3d = new_transform.ExtractTranslation()

        # Set the new translation and rotation
        self.prim.GetAttribute("xformOp:translate").Set(translate)

        # Combine the rotations into one Euler angle vector
        # Assuming the rotations are small enough that they can be combined additively
        current_euler_rotation = self.prim.GetAttribute("xformOp:rotateXYZ").Get()
        new_euler_rotation = Gf.Vec3f(
            current_euler_rotation[0] + new_pitch,
            current_euler_rotation[1] + new_yaw,
            current_euler_rotation[2] + new_roll
        )
        self.prim.GetAttribute("xformOp:rotateXYZ").Set(new_euler_rotation)

    def update_drone_movement_FPS(self, forward, strafe, up_down, yaw, pitch):
        # Get the current transformation of the drone
        local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        # try:
        #     local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        # except Exception as e:
        #     self.stage = omni.usd.get_context().get_stage()
        #     self.prim = self.stage.GetPrimAtPath("/World/iris")
        #     self.xform = UsdGeom.Xformable(self.prim)
        #     local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()

        # Compute the translation vectors based on the local reference frame
        right_vector = local_transformation.TransformDir(Gf.Vec3d(0, -1, 0)).GetNormalized()
        forward_vector = local_transformation.TransformDir(Gf.Vec3d(1, 0, 0)).GetNormalized()
        up_vector = local_transformation.TransformDir(Gf.Vec3d(0, 0, 1)).GetNormalized()

        # Calculate the actual translation vectors based on input
        translation = (right_vector * strafe) + (forward_vector * forward) + (up_vector * up_down)

        # Apply the translation to the drone
        current_translation = self.prim.GetAttribute("xformOp:translate").Get()
        new_translation = current_translation + translation
        self.prim.GetAttribute("xformOp:translate").Set(new_translation)

        # Calculate new rotation values
        yaw_speed_factor = 1
        pitch_speed_factor = 1
        current_euler_rotation = self.prim.GetAttribute("xformOp:rotateXYZ").Get()
        
        # Apply yaw to the z component for rotation around the vertical axis
        new_yaw = current_euler_rotation[1] + (yaw * yaw_speed_factor)
        
        new_pitch = current_euler_rotation[2] + (pitch * pitch_speed_factor)

        # Set the new rotation
        # rotations around the z axis aren't being reflected in prim properties
        self.prim.GetAttribute("xformOp:rotateXYZ").Set(Gf.Vec3f(
            current_euler_rotation[0],
            new_yaw,
            new_pitch))
        # return 'yolo'
        # different method to rotate around z axis
        # omni.kit.commands.execute(
        #     'ChangeProperty',
        #     prop_path=Sdf.Path('/World/iris.xformOp:rotateXYZ'),
        #     value=Gf.Vec3f(-5.7126617431640625, -2.000185251235962, 43.0),
        #     prev=Gf.Vec3f(-5.7126617431640625, -2.000185251235962, 44.10000228881836),
        #     target_layer=Sdf.Find('omniverse://localhost/Projects/soceur/google_maps_stage.usd'),
        #     usd_context_name=Usd.Stage.Open(rootLayer=Sdf.Find('omniverse://localhost/Projects/soceur/google_maps_stage.usd'), sessionLayer=Sdf.Find('anon:00000246D28DF0E0'), pathResolverContext=<invalid repr>))

