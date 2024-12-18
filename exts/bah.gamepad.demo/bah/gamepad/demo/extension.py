import omni.ext

from .drone_movement import DroneMovementHandler
from .ui_components import UIComponents
from .gamepad_events import GamepadEventHandler
from .sphere_material import SphereMaterialHandler
from .emitter_manager import EmitterManager
from .animation_manager import AnimationManager
from .camera_manager import CameraManager

class bahGamepadDemoExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self.stage = omni.usd.get_context().get_stage()

        self.emitter_manager = EmitterManager()
        self.sphere_material_handler = SphereMaterialHandler(self.stage, self.emitter_manager)
        self.sphere_material_handler.create_spheres_for_emitters()
        self.drone_movement_handler = DroneMovementHandler(self.stage)
        self.gamepad_event_handler = GamepadEventHandler(self.stage, self.drone_movement_handler)
        self.animation_manager = AnimationManager(self.stage, self.emitter_manager)
        self.camera_manager = CameraManager()
        print(f"CameraManager initialized: {type(self.camera_manager)}")
        self.ui_components = UIComponents(
            ext_id,
            self.gamepad_event_handler,
            self.sphere_material_handler,
            self.emitter_manager,
            self.animation_manager,
            self.camera_manager
            )

    def on_shutdown(self):
        self.gamepad_event_handler.shutdown()
        self.ui_components.shutdown()
        self.emitter_manager.shutdown()
        self.sphere_material_handler.shutdown()
        self.animation_manager.shutdown()
        self.camera_manager.shutdown()
        print("[bah.gamepad.demo] bah gamepad demo shutdown")
