import omni.ext
import omni.ui as ui
# subscribing to gamepad events
import omni.appwindow
from carb.input import GamepadInput, GamepadEvent, acquire_input_interface
import carb
from functools import partial
import logging



    


class OmnibricksGamepadDemoExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo startup")

        self._count = 0
        self._dpad_count = 0

        self._window = ui.Window("My Window", width=300, height=300)

        # subscribe to gamepad events
        self._app_window = omni.appwindow.get_default_app_window()
        self.gamepad = self._app_window.get_gamepad(0)

        self.logger = logging.getLogger()
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
    def on_gamepad_event(self, event: GamepadEvent):

        # carb.log_info(event.input)
        # carb.log_info('yolo')
        # self.logger('yolo_logger')
        # print('yolo_print')
        # D-pad Up for accelerating
        if event.input == GamepadInput.DPAD_UP:
            if event.value > 0.5:
                self._dpad_count += 1

        # D-pad Down for braking
        elif event.input == GamepadInput.DPAD_DOWN:
            if event.value > 0.5:
                self._dpad_count -= 1

        elif event.input == GamepadInput.A:
            self._dpad_count = 0
        
        self.gamepad_info.text = f"gamepad: {self._dpad_count}"

    def on_shutdown(self):
        self.input.unsubscribe_to_gamepad_events(self.gamepad, self.gamepad_event_sub)
        self.gamepad_event_sub = None
        print("[omnibricks.gamepad.demo] omnibricks gamepad demo shutdown")
