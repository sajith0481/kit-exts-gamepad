

class EmitterManager:
    def __init__(self):
        self.emitters = []
        self.emitters = [{
            "display_name": "Panzer Kaserne",
            "prim_name": self.generate_unique_prim_name("Panzer_Kaserne"),
            "latitude": 48.73516,
            "longitude": 9.07533,
            "height": 250,
            "radius": 2000
        }
        ]

    def generate_unique_prim_name(self, display_name, exclude_index=None):
        base_name = display_name.replace(" ", "_")  # Remove spaces
        prim_name = base_name
        counter = 1

        # Check if this prim_name already exists
        existing_prim_names = [emitter['prim_name'] for i, emitter in enumerate(self.emitters) if i != exclude_index]
        for existing_name in existing_prim_names:
            if prim_name == existing_name:
                prim_name = f"{base_name}_{counter}"
                counter += 1

        return prim_name
    
    def add_emitter(self, name, latitude, longitude, height, radius):
        prim_name = self.generate_unique_prim_name(name)
        emitter = {
            "display_name": name,
            "prim_name": prim_name,
            "latitude": latitude,
            "longitude": longitude,
            "height": height,
            "radius": radius
        }
        self.emitters.append(emitter)

    def update_emitter(self, index, name, latitude, longitude, height, radius):
        updated_prim_name = self.generate_unique_prim_name(name, index)
        if index < len(self.emitters):
            self.emitters[index] = {
                "display_name": name,
                "latitude": latitude,
                "longitude": longitude,
                "height": height,
                "radius": radius,
                "prim_name": updated_prim_name
            }
        else:
            print("Emitter index out of range")

    def delete_emitter(self, index):
        if index < len(self.emitters):
            del self.emitters[index]
        else:
            print("Emitter index out of range")

    def get_emitters(self):
        return self.emitters
