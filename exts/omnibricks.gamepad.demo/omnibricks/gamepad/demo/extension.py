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
        self.prim = self.stage.GetPrimAtPath("/World/quadrotor")
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

        # D-pad Up for accelerating
        if event.input == GamepadInput.DPAD_UP:
            if event.value > 0.5:
                self.move_drone_forward(1)  # Move forward
            else:
                self.move_drone_forward(0)  # Stop

        # D-pad Down for braking
        elif event.input == GamepadInput.DPAD_DOWN:
            if event.value > 0.5:
                self.move_drone_forward(-1)  # Move backward (brake)
            else:
                self.move_drone_forward(0)  # Stop

        # Use right stick for steering
        if event.input == GamepadInput.RIGHT_STICK_RIGHT:
            self.move_drone_lateral(cur_val)  # Move right
        elif event.input == GamepadInput.RIGHT_STICK_LEFT:
            self.move_drone_lateral(-cur_val)  # Move left


    def move_drone_forward(self, direction):
        local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        drone_forward_vector = Gf.Vec4d(1,0,0,1)  # Adjust based on drone's orientation

        a: Gf.Vec4d = Gf.Vec4d(0,0,0,1) * local_transformation
        b: Gf.Vec4d = drone_forward_vector * local_transformation

        drone_fwd_vec = b-a
        drone_fwd_unit_vec = Gf.Vec3d(drone_fwd_vec[:3]).GetNormalized()

        forward_step = drone_fwd_unit_vec * direction  # Use the direction to determine forward or backward

        offset_mat = Gf.Matrix4d()
        offset_mat.SetTranslate(forward_step)

        new_transform = local_transformation * offset_mat
        translate: Gf.Vec3d = new_transform.ExtractTranslation()
        self.prim.GetAttribute("xformOp:translate").Set(translate)

    def move_drone_lateral(self, direction):
        local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        drone_right_vector = Gf.Vec4d(1,0,0,0)  # Adjust based on drone's orientation

        a: Gf.Vec4d = Gf.Vec4d(0,0,0,1) * local_transformation
        b: Gf.Vec4d = drone_right_vector * local_transformation

        drone_right_vec = b-a
        drone_right_unit_vec = Gf.Vec3d(drone_right_vec[:3]).GetNormalized()

        sideways_step = drone_right_unit_vec * direction

        offset_mat = Gf.Matrix4d()
        offset_mat.SetTranslate(sideways_step)

        new_transform = local_transformation * offset_mat
        translate: Gf.Vec3d = new_transform.ExtractTranslation()
        self.prim.GetAttribute("xformOp:translate").Set(translate)
    
    def on_shutdown(self):
        self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
        self.gamepad_event_sub = None
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo shutdown")
