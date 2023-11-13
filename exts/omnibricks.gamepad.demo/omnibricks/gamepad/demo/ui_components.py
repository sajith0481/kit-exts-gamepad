import omni.ui as ui
from pxr import Gf, Sdf, UsdGeom
import omni.usd


class UIComponents:
    def __init__(self, ext_id, gamepad_event_handler, sphere_material_handler):
        self.ext_id = ext_id
        self.manager = omni.kit.app.get_app().get_extension_manager()
        self.ext_path = self.manager.get_extension_path(ext_id)
        self.gamepad_event_handler = gamepad_event_handler
        self.sphere_material_handler = sphere_material_handler
        self.style = {
            "": {"background_color": ui.color.TRANSPARENT, "image_url": f"{self.ext_path}/icons/radio_off.svg"},
            ":checked": {"image_url": f"{self.ext_path}/icons/radio_on.svg"},
        }
        self._create_ui()

    def _create_ui(self):
        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                self._create_mode_selection_ui()
                self._create_coordinate_inputs_ui()
                self._create_sphere_radius_ui()
                ui.Button("Create Signal", clicked_fn=self.on_create_signal_clicked)

    def _create_mode_selection_ui(self):
        collection = ui.RadioCollection()
        with ui.HStack(style=self.style, height=20):
            for button_label in ["FPS Mode", "Mode 2"]:
                ui.RadioButton(radio_collection=collection,
                               clicked_fn=self.gamepad_event_handler.toggle_gamepad_mode,
                               width=40,
                               height=30)
                ui.Label(f"{button_label}", name="text")
        self.collection = collection

    def _create_coordinate_inputs_ui(self):
        ui.Label("Enter Transmitter Coordinates", alignment=ui.Alignment.CENTER)
        with ui.HStack():
            ui.Label("Latitude:")
            self.latitude_field = ui.FloatField(value=48.73516)
        with ui.HStack():
            ui.Label("Longitude:")
            self.longitude_field = ui.FloatField(value=9.07533)
        with ui.HStack():
            ui.Label("Height:")
            self.height_field = ui.FloatField(value=250)

    def _create_sphere_radius_ui(self):
        with ui.HStack():
            ui.Label("Sphere Radius:")
            self.radius_field = ui.FloatField(value=1.0)  # Default value of 1.0

    def on_create_signal_clicked(self):
        # Gather input values
        latitude = self.latitude_field.model.get_value_as_float()
        longitude = self.longitude_field.model.get_value_as_float()
        height = self.height_field.model.get_value_as_float()
        radius = self.radius_field.model.get_value_as_float()

        # Call create_signal on the sphere_material_handler
        self.sphere_material_handler.create_signal(latitude, longitude, height, radius)

    def shutdown(self):
        self._window.destroy()
        self._window = None
