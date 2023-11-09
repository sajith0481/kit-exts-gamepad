import omni.ext
import omni.ui as ui
# subscribing to gamepad events
import omni.appwindow
from carb.input import GamepadInput, GamepadEvent, acquire_input_interface
import carb
from functools import partial
import logging
from pxr import Gf, UsdGeom, Usd, Gf, Vt, Sdf
import omni.usd
from omni.ui import color as cl
import numpy as np
from pxr.Sdf import Path
from typing import Optional
from cesium.omniverse.api.globe_anchor import anchor_xform_at_path

# This should be defined somewhere in your code
def set_global_anchor(latitude, longitude, height, sphere_path):

    # Example usage:
    xform_path = Sdf.Path(sphere_path)

    # Call the function to set the global anchor
    anchor_xform_at_path(xform_path, latitude, longitude, height)

    print(f"Setting global anchor at latitude: {latitude}, longitude: {longitude}, height: {height}")

class OmnibricksGamepadDemoExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo startup")
        self.manager = omni.kit.app.get_app().get_extension_manager()
        self.ext_path = self.manager.get_extension_path(ext_id)
        self.style = {
            "": {"background_color": cl.transparent, "image_url": f"{self.ext_path}/icons/radio_off.svg"},
            ":checked": {"image_url": f"{self.ext_path}/icons/radio_on.svg"},
        }

        self._count = 0
        self._dpad_count = 0
        self.sphere_count = 0

        self._window = ui.Window("My Window", width=300, height=300)

        # subscribe to gamepad events
        self._app_window = omni.appwindow.get_default_app_window()
        self.gamepad = self._app_window.get_gamepad(0)

        # get camera
        self.stage = omni.usd.get_context().get_stage()
        self.prim = self.stage.GetPrimAtPath("/World/iris")
        self.xform = UsdGeom.Xformable(self.prim)       

        self.input = acquire_input_interface()
        self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event_FPS)

        with self._window.frame:
            with ui.VStack():
                # Button to change controller scheme
                collection = ui.RadioCollection()
                with ui.HStack(style=self.style, height=20):
                    for button_label in ["FPS Mode", "Mode 2"]:
                        ui.RadioButton(radio_collection=collection,
                                    clicked_fn=self.toggle_mode,
                                    width=40,
                                    height=30
                                    )
                        ui.Label(f"{button_label}", name="text")
                self.collection = collection
                # Add input fields for latitude, longitude, and height
                ui.Label("Enter Transmitter Coordinates", alignment=ui.Alignment.CENTER)

                # Latitude input
                with ui.HStack():
                    ui.Label("Latitude:")
                    self.latitude_field = ui.FloatField()

                # Longitude input
                with ui.HStack():
                    ui.Label("Longitude:")
                    self.longitude_field = ui.FloatField()
                
                # Height input
                with ui.HStack():
                    ui.Label("Height:")
                    self.height_field = ui.FloatField()

                # Add input field for the sphere's radius
                with ui.HStack():
                    ui.Label("Sphere Radius:")
                    self.radius_field = ui.FloatField(value=1.0)  # Default value of 1.0
                
                # Add button to set the global anchor
                ui.Button("Create Signal", clicked_fn=self.create_signal)                
    
    def create_sphere_and_material(self):
        # Increment the sphere count
        self.sphere_count += 1
        sphere_name = f'Signal{self.sphere_count}'
        sphere_path = f'/World/{sphere_name}'

        # Create Sphere with the incremented name
        omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',
            prim_type='Sphere',
            prim_path=sphere_path,
            select_new_prim=False,
            prepend_default_prim=True)
        
        # Create the material path for this instance
        material_path = f'/World/Looks/Clear_Glass{self.sphere_count}'

        omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
            mdl_name='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Glass/Clear_Glass.mdl',
            mtl_name=f'Clear_Glass',
            mtl_created_list=[material_path],
            select_new_prim=False)

        omni.kit.commands.execute('CreatePrim',
            prim_path='/World/Looks',
            prim_type='Scope',
            select_new_prim=False)

        omni.kit.commands.execute('CreateMdlMaterialPrim',
            mtl_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Glass/Clear_Glass.mdl',
            mtl_name='Clear_Glass',
            mtl_path=material_path,
            select_new_prim=False)

        # Bind the material to the new sphere
        omni.kit.commands.execute('BindMaterial',
            prim_path=Sdf.Path(sphere_path),
            material_path=Sdf.Path(material_path),
            strength=None)
        
        # omni.kit.commands.execute('ChangeProperty',
        #     prop_path=Sdf.Path(f'{material_path}/Shader.inputs:glass_color'),
        #     value=Gf.Vec3f(0.6919831037521362, 0.42336520552635193, 0.42336520552635193),
        #     prev=Gf.Vec3f(1.0, 1.0, 1.0))

        return sphere_path, material_path  # Return the path of the newly created sphere

    def create_signal(self):
        # Get the latitude, longitude, and height from the UI fields
        latitude = self.latitude_field.model.get_value_as_float()
        longitude = self.longitude_field.model.get_value_as_float()
        height = self.height_field.model.get_value_as_float()
        radius = self.radius_field.model.get_value_as_float()

        # Call the function to create the sphere and apply the material
        sphere_path, material_path = self.create_sphere_and_material()

        # Now, call the function to set the global anchor
        set_global_anchor(latitude, longitude, height, sphere_path)

        # Now, scale the sphere to the given radius
        self.scale_sphere_to_radius(radius, sphere_path)

    def scale_sphere_to_radius(self, radius, sphere_path):
        # Assuming the sphere's original radius at scale (1,1,1) is 1 unit
        new_scale = Gf.Vec3d(radius, radius, radius)

        # The path of the sphere might need to be adjusted based on your scene
        #sphere_path = '/World/Sphere'

        # Turn on 'doNotCastShadows' for the sphere
        omni.kit.commands.execute('ChangeProperty',
            prop_path=Sdf.Path(f"{sphere_path}.primvars:doNotCastShadows"),
            value=True,
            prev=None  # Set this to whatever the previous value might be, or remove if not needed
        )

        # Execute the command to scale the sphere
        omni.kit.commands.execute('ChangeProperty',
            prop_path=Sdf.Path(f"{sphere_path}.cesium:anchor:scale"),
            value=new_scale,
            prev=Gf.Vec3d(1.0, 1.0, 1.0)  # You might need to get the actual previous scale if necessary
        )

    def toggle_mode(self):
        # Unsubscribe the current event subscription
        if self.gamepad_event_sub:
            self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
            self.gamepad_event_sub = None

        # Subscribe to the selected mode
        if self.collection.model.get_value_as_int() == 1:  # Mode 2
            self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event)
        elif self.collection.model.get_value_as_int() == 0:  # FPS Mode
            self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event_FPS)

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


    def on_gamepad_event_FPS(self, event: carb.input.GamepadEvent):
        cur_val = event.value
        absval = abs(event.value)

        if absval == 0:
            return
        if absval < 0.001:
            cur_val = 0

        # Initialize controls for translation and orientation
        forward = 0
        strafe = 0
        up_down = 0
        yaw = 0
        pitch = 0

        # Left stick y-axis for forward/backward translation
        if event.input == GamepadInput.LEFT_STICK_UP:
            forward = cur_val
        elif event.input == GamepadInput.LEFT_STICK_DOWN:
            forward = -cur_val

        # Left stick x-axis for left/right translation
        if event.input == GamepadInput.LEFT_STICK_RIGHT:
            strafe = cur_val
        elif event.input == GamepadInput.LEFT_STICK_LEFT:
            strafe = -cur_val

        # Right stick y-axis for pitch orientation
        if event.input == GamepadInput.RIGHT_STICK_UP:
            yaw = cur_val  # Inverting as typically pushing up tilts the nose down
        elif event.input == GamepadInput.RIGHT_STICK_DOWN:
            yaw = -cur_val

        # Right stick x-axis for yaw orientation
        if event.input == GamepadInput.RIGHT_STICK_RIGHT:
            pitch = cur_val
        elif event.input == GamepadInput.RIGHT_STICK_LEFT:
            pitch = -cur_val

        # shoulder bottons for up/down
        if event.input == GamepadInput.LEFT_TRIGGER:
            up_down = -1
        elif event.input == GamepadInput.RIGHT_TRIGGER:
            up_down = 1
        
        # Update the drone movement
        self.update_drone_movement_FPS(forward, strafe, up_down, yaw, pitch)


    def update_drone_movement_FPS(self, forward, strafe, up_down, yaw, pitch):
        # Get the current transformation of the drone
        try:
            local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()
        except Exception as e:
            self.stage = omni.usd.get_context().get_stage()
            self.prim = self.stage.GetPrimAtPath("/World/iris")
            self.xform = UsdGeom.Xformable(self.prim)
            local_transformation: Gf.Matrix4d = self.xform.GetLocalTransformation()

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
        new_yaw = current_euler_rotation[1] + (yaw * yaw_speed_factor)
        new_pitch = current_euler_rotation[0] + (pitch * pitch_speed_factor)

        # Set the new rotation
        self.prim.GetAttribute("xformOp:rotateXYZ").Set(Gf.Vec3f(new_pitch, new_yaw, current_euler_rotation[2]))



    
    def on_shutdown(self):
        self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
        self.gamepad_event_sub = None
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo shutdown")
