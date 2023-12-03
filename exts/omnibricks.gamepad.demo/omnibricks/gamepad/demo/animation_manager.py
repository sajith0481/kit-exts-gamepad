import carb
import omni.timeline
from pxr import Gf, UsdGeom, Usd, Sdf
import omni.kit.commands
import omni
import time



class AnimationManager:
    def __init__(self, stage, emitter_manager):

        self._app_window = omni.appwindow.get_default_app_window()
        self.stage = stage
        self.emitter_manager = emitter_manager
        # subscribe to timeline
        self.itimeline = omni.timeline.get_timeline_interface()
        self._time_sub = self.itimeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event,
            name='timer event'
        )



        # Define the range and steps for radius values
        self.min_radius = 2000
        self.max_radius = 5000
        self.radius_step = 50  # Adjust the step size as needed
        self.radius_values = list(range(self.min_radius, self.max_radius, self.radius_step)) + \
                             list(range(self.max_radius, self.min_radius, -self.radius_step))
        self.current_index = 0

        # Updates per second and time tracking
        self.updates_per_second = 7  # Adjust as needed
        self.last_update_time = time.time()

        # Manage example emitter
        self.emitter = self.emitter_manager.get_emitter(2)
        self.sphere_path = f"/World/emitters/{self.emitter['prim_name']}"
        self.radius_attribute = self.stage.GetPrimAtPath(self.sphere_path).GetAttribute("cesium:anchor:scale")

    def _on_timeline_event(self, e: carb.events.IEvent):
        current_time = time.time()
        time_since_last_update = current_time - self.last_update_time

        # Check if it's time to update based on updates_per_second
        if time_since_last_update >= 1 / self.updates_per_second:
            self.last_update_time = current_time
            new_radius = self.radius_values[self.current_index]
            self.update_radius(new_radius)
            self.current_index = (self.current_index + 1) % len(self.radius_values)

    def update_radius(self, radius):
        self.radius_attribute.Set(Gf.Vec3d(2000, 2000, radius))

    def shutdown(self):
        self.itimeline = None
        self._time_sub = None
        print("Animation Manager shutdown")
