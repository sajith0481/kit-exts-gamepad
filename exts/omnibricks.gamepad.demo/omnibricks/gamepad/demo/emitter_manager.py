import random


class EmitterManager:
    def __init__(self):
        self.emitters = []
        self.init_emitters = [{
            "display_name": "Panzer Kaserne",
            "prim_name": "Panzer_Kaserne",
            "latitude": 48.73516,
            "longitude": 9.07533,
            "height": 250,
            "radius": 2000
        },
        {"display_name": "Emitter 1", "latitude": 48.7625, "longitude": 9.1650, "height": 250, "radius": 1500, "prim_name": "Emitter_1"},
        {"display_name": "Emitter 2", "latitude": 48.7625, "longitude": 9.1650, "height": random.randint(250, 1000), "radius": random.randint(500, 2500), "prim_name": "Emitter_2"},
        {"display_name": "Emitter 3", "latitude": 48.7625, "longitude": 9.1650, "height": 250, "radius": 1500, "prim_name": "Emitter_3"},
        {"display_name": "Emitter 4", "latitude": 48.7360, "longitude": 9.1292, "height": random.randint(250, 1000), "radius": random.randint(500, 2500), "prim_name": "Emitter_4"},
        {"display_name": "Emitter 5", "latitude": 48.7227, "longitude": 9.1113, "height": random.randint(250, 1000), "radius": random.randint(500, 2500), "prim_name": "Emitter_5"},
        {"display_name": "Emitter 6", "latitude": 48.7094, "longitude": 9.0934, "height": random.randint(250, 1000), "radius": random.randint(500, 2500), "prim_name": "Emitter_6"},
        {"display_name": "Emitter 7", "latitude": 48.6899, "longitude": 9.0419, "height": random.randint(250, 1000), "radius": random.randint(500, 2500), "prim_name": "Emitter_7"}
        ]

        self.emitters = self.init_emitters

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
    
    def get_emitter(self, index):
        if index < len(self.emitters):
            return self.emitters[index]
        else:
            print("Emitter index out of range")

    def clean_up_old_emitters(self):
        for i, emitter in enumerate(self.emitters):
            self.delete_emitter(i)
        # init_emitter_display_names = [init_emitter['display_name'] for init_emitter in self.init_emitters]
        # for i, emitter in enumerate(self.emitters):
        #     if emitter['display_name'] in init_emitter_display_names:
        #         self.delete_emitter(i)
        #     else:
        #         continue

    def shutdown(self):
        self.clean_up_old_emitters()
