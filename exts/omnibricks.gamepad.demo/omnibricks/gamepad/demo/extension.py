import omni.ext
import omni.ui as ui
# subscribing to gamepad events
import omni.appwindow
from carb.input import GamepadInput, GamepadEvent, acquire_input_interface
import carb
from functools import partial
import logging
from pxr import Gf, UsdGeom, Usd
import omni.usd



    


class OmnibricksGamepadDemoExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo startup")

        self._count = 0
        self._dpad_count = 0

        self._window = ui.Window("My Window", width=300, height=300)

        # subscribe to gamepad events
        self._app_window = omni.appwindow.get_default_app_window()
        self.gamepad = self._app_window.get_gamepad(0)

        # get camera
        self.stage = omni.usd.get_context().get_stage()
        self.prim = self.stage.GetPrimAtPath("/Camera")
        self.xform = UsdGeom.Xformable(self.prim)
        

        self.input = acquire_input_interface()
        self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event)

        with self._window.frame:
            with ui.VStack():
                label = ui.Label("")
                self.gamepad_info = ui.Label("")


                def on_click():
                    self._count += 1
                    label.text = f"count: {self._count}"
                    # gamepad_info.text = f"gamepad: {self._count}"

                def on_reset():
                    self._count = 0
                    label.text = "empty"

                on_reset()

                with ui.HStack():
                    ui.Button("Add", clicked_fn=on_click)
                    ui.Button("Reset", clicked_fn=on_reset)

    # Handling Gamepad Events for a Vehicle
    def on_gamepad_event(self, event: carb.input.GamepadEvent):
        cur_val = event.value
        absval = abs(event.value)

        if absval == 0:
            return
        if absval < 0.001:
            cur_val = 0

        # initialize controls
        throttle = 0
        yaw = 0
        pitch = 0
        roll = 0

        # left stick y-axis for throttle/altitude
        if event.input == GamepadInput.LEFT_STICK_UP:
            if event.value > 0.5:
                throttle = 1
        elif event.input == GamepadInput.LEFT_STICK_DOWN:
            if event.value > 0.5:
                throttle = -1

        # left stick x-axis for yaw
        if event.input == GamepadInput.LEFT_STICK_RIGHT:
            if event.value > 0.5:
                yaw = 1
        elif event.input == GamepadInput.LEFT_STICK_LEFT:
            if event.value > 0.5:
                yaw = -1

        # right stick y-axis for pitch
        if event.input == GamepadInput.RIGHT_STICK_UP:
            if event.value > 0.5:
                pitch = 1
        elif event.input == GamepadInput.RIGHT_STICK_DOWN:
            if event.value > 0.5:
                pitch = -1

        # right stick y-axis for roll
        if event.input == GamepadInput.RIGHT_STICK_RIGHT:
            if event.value > 0.5:
                roll = 1
        elif event.input == GamepadInput.RIGHT_STICK_LEFT:
            if event.value > 0.5:
                roll = -1
                
        self.update_drone_movement(throttle, yaw, pitch, roll)


    

    def update_drone_movement(self, throttle, yaw, pitch, roll):
        local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()

        # Handle Yaw
        current_rot = local_transformation.ExtractRotation()
        yaw_speed_factor = 1  # simple temp value
        yaw_rotation = Gf.Rotation(Gf.Vec3d(0, 1, 0), yaw * yaw_speed_factor)
        yaw_quat = yaw_rotation.GetQuat()
        current_rot_quat = current_rot.GetQuat()
        new_rot_quat = yaw_quat * current_rot_quat
        new_rot_quat.Normalize()

        # Handle Pitch and Roll
        pitch_speed_factor = 1  # Simple temp value
        roll_speed_factor = 1  # Simple temp value
        pitch_rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), pitch * pitch_speed_factor)
        roll_rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), roll * roll_speed_factor)
        pitch_quat = pitch_rotation.GetQuat()
        roll_quat = roll_rotation.GetQuat()
        new_rot_quat = roll_quat * pitch_quat * new_rot_quat
        new_rot_quat.Normalize()

        # Handle Throttle
        drone_up_vector = Gf.Vec4d(0, 1, 0, 0)
        transformed_up_vector = drone_up_vector * local_transformation
        move_direction = Gf.Vec3d(transformed_up_vector[:3]).GetNormalized()
        throttle_speed_factor = 1  # simple temp value
        move_step = move_direction * throttle * throttle_speed_factor
        offset_mat = Gf.Matrix4d().SetTranslate(move_step)
        new_transform = local_transformation * offset_mat
        translate: Gf.Vec3d = new_transform.ExtractTranslation()

        # Apply new rotation and translation
        self.prim.GetAttribute("xformOp:orient").Set(new_rot_quat)
        self.prim.GetAttribute("xformOp:translate").Set(translate)






    
    def on_shutdown(self):
        self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
        self.gamepad_event_sub = None
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo shutdown")
