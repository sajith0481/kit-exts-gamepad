import carb
from carb.input import GamepadInput, GamepadEvent, acquire_input_interface
from pxr import Gf, UsdGeom, Usd
import omni


class GamepadEventHandler:
    def __init__(self, stage, drone_movement_handler, prim_path="/World/iris"):

        # subscribe to gamepad events
        self._app_window = omni.appwindow.get_default_app_window()
        self.gamepad = self._app_window.get_gamepad(0)
        self.input = acquire_input_interface()
        self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event_FPS)

        self.stage = stage
        self.prim_path = prim_path
        self.current_mode = 0  # 0 for FPS mode, 1 for another mode
        self.drone_movement_handler = drone_movement_handler

        # Initialize the primary game object
        self.prim = self.stage.GetPrimAtPath(self.prim_path)
        self.xform = UsdGeom.Xformable(self.prim)

    def unsubscribe_to_gamepad_events(self):
        if self.gamepad_event_sub:
            self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
            self.gamepad_event_sub = None

    def toggle_gamepad_mode(self):
        self.unsubscribe_to_gamepad_events()
        self.current_mode = (self.current_mode + 1) % 2
        if self.current_mode == 0:
            self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event_FPS)
        else:
            self.gamepad_event_sub = self.input.subscribe_to_gamepad_events(self.gamepad, self.on_gamepad_event)

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
                
        self.drone_movement_handler.update_drone_movement(throttle, yaw, pitch, roll)

    def on_gamepad_event_FPS(self, event: GamepadEvent):
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
            pitch = -cur_val
        elif event.input == GamepadInput.RIGHT_STICK_LEFT:
            pitch = cur_val

        # shoulder bottons for up/down
        if event.input == GamepadInput.LEFT_TRIGGER:
            up_down = -1
        elif event.input == GamepadInput.RIGHT_TRIGGER:
            up_down = 1
        
        # Update the drone movement
        self.drone_movement_handler.update_drone_movement_FPS(forward, strafe, up_down, yaw, pitch)

    def shutdown(self):
        self.unsubscribe_to_gamepad_events()
        print("Gamepad event handler shutdown")
