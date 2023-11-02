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
        self.prim = self.stage.GetPrimAtPath("/World/Camera")
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
                    ui.Button("Move Camera", clicked_fn=self.move_camera)

    # Handling Gamepad Events for a Vehicle
    def on_gamepad_event(self, event: GamepadEvent):

        # D-pad Up for accelerating
        if event.input == GamepadInput.DPAD_UP:
            if event.value > 0.5:
                self._dpad_count += 1

        # D-pad Down for braking
        elif event.input == GamepadInput.DPAD_DOWN:
            if event.value > 0.5:
                self._dpad_count -= 1

        elif event.input == GamepadInput.A:
            # self._dpad_count = 0
            self.move_camera()
        
        self.gamepad_info.text = f"gamepad: {self._dpad_count}"

    def move_camera(self):
        local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        # Apply the local matrix to the start and end points of the camera's default forward vector (-Z)
        a: Gf.Vec4d = Gf.Vec4d(0,0,0,1) * local_transformation
        b: Gf.Vec4d = Gf.Vec4d(0,0,-1,1) * local_transformation
        # Get the vector between those two points to get the camera's current forward vector
        cam_fwd_vec = b-a
        # Convert to Vec3 and then normalize to get unit vector
        cam_fwd_unit_vec = Gf.Vec3d(cam_fwd_vec[:3]).GetNormalized()
        # Multiply the forward direction vector with how far forward you want to move
        forward_step = cam_fwd_unit_vec * 100
        # Create a new matrix with the translation that you want to perform
        offset_mat = Gf.Matrix4d()
        offset_mat.SetTranslate(forward_step)
        # Apply the translation to the current local transform
        new_transform = local_transformation * offset_mat
        # Extract the new translation
        translate: Gf.Vec3d = new_transform.ExtractTranslation()
        # Update the attribute
        self.prim.GetAttribute("xformOp:translate").Set(translate)

    def on_shutdown(self):
        self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
        self.gamepad_event_sub = None
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo shutdown")
