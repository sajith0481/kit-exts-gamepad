import omni.ui as ui
from pxr import Gf, Sdf, UsdGeom
import omni.usd


class UIComponents:
    def __init__(self, ext_id, gamepad_event_handler, sphere_material_handler, emitter_manager):
        self.ext_id = ext_id
        self.manager = omni.kit.app.get_app().get_extension_manager()
        self.ext_path = self.manager.get_extension_path(ext_id)
        self.gamepad_event_handler = gamepad_event_handler
        self.sphere_material_handler = sphere_material_handler
        self.emitter_manager = emitter_manager
        self.emitter_field_references = []
        self.style = {
            "": {"background_color": ui.color.TRANSPARENT, "image_url": f"{self.ext_path}/icons/radio_off.svg"},
            ":checked": {"image_url": f"{self.ext_path}/icons/radio_on.svg"},
        }
        self._window = ui.Window("DOVE", width=300, height=300)
        self._recreate_ui = self._window.frame

        self._create_ui()

    def _create_ui(self):
        with self._recreate_ui:
            with ui.VStack():
                self._create_mode_selection_ui()
                self._create_coordinate_inputs_ui()
                ui.Button(
                    "Add New Emitter",
                    clicked_fn=self.add_new_emitter,
                     alignment=ui.Alignment.CENTER,
                     height=30,
                     )

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
        ui.Label("Emitter Table", alignment=ui.Alignment.CENTER)
        with ui.VGrid(column_count=7, row_spacing=3, column_spacing=5):
            # header row
            ui.Label("Name")
            ui.Label("Latitude")
            ui.Label("Longitude")
            ui.Label("Height")
            ui.Label("Radius")
            ui.Label("Update")
            ui.Label("Delete")
            # Dynamically create rows for each emitter
            self.emitter_field_references.clear()
            for i, emitter in enumerate(self.emitter_manager.get_emitters()):
                field_references = {
                    'name_field': ui.StringField(name=f"emitter_name_{i}"),
                    'latitude_field': ui.FloatField(),
                    'longitude_field': ui.FloatField(),
                    'height_field': ui.FloatField(),
                    'radius_field': ui.FloatField()
                }

                # Set initial values for each field
                field_references['name_field'].model.set_value(emitter['display_name'])
                field_references['latitude_field'].model.set_value(emitter['latitude'])
                field_references['longitude_field'].model.set_value(emitter['longitude'])
                field_references['height_field'].model.set_value(emitter['height'])
                field_references['radius_field'].model.set_value(emitter['radius'])

                self.emitter_field_references.append(field_references)

                # Update button
                ui.Button("Update", clicked_fn=lambda x=i: self.handle_update_emitter(i))

                # Delete button
                ui.Button("Delete", clicked_fn=lambda x=i: self.handle_delete_emitter(i))

    def handle_update_emitter(self, index):
        field_references = self.emitter_field_references[index]

        name = field_references['name_field'].model.get_value_as_string()
        latitude = field_references['latitude_field'].model.get_value_as_float()
        longitude = field_references['longitude_field'].model.get_value_as_float()
        height = field_references['height_field'].model.get_value_as_float()
        radius = field_references['radius_field'].model.get_value_as_float()

        self.emitter_manager.update_emitter(index, name, latitude, longitude, height, radius)
        updated_emitter = self.emitter_manager.get_emitters()[index]
        self.sphere_material_handler.update_sphere(updated_emitter)

    def handle_delete_emitter(self, index):
        if index < len(self.emitter_manager.get_emitters()):
            # Retrieve the emitter to be deleted
            emitter_to_delete = self.emitter_manager.get_emitters()[index]
            self.emitter_manager.delete_emitter(index)
            self.sphere_material_handler.delete_sphere(emitter_to_delete['prim_name'])
            del self.emitter_field_references[index]
            self._create_coordinate_inputs_ui()
        else:
            print("Emitter index out of range")

    def add_new_emitter(self):
        default_values = {
            "name": "default",
            "latitude": 0.0,
            "longitude": 0.0,
            "height": 0.0,
            "radius": 0.0
        }

        self.emitter_manager.add_emitter(**default_values)
        self._create_ui()

    def shutdown(self):
        self._window.destroy()
        self._window = None
