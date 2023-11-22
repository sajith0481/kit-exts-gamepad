import omni.kit.commands
from pxr import Sdf, Gf, UsdGeom, Usd
from cesium.omniverse.api.globe_anchor import anchor_xform_at_path


class SphereMaterialHandler:
    def __init__(self, stage, emitter_manager):
        self.stage = stage
        self.emitter_manager = emitter_manager
        self.sphere_prims = {}  # Dictionary to map emitter names to sphere prims
        
        # Don't want to keep creating more materials
        self.material_path = '/World/Looks/Clear_Glass'
        if self.stage.GetPrimAtPath(self.material_path).GetPrim().IsValid():
            return None
        
        self.clean_up_old_emitters()
        
        # create prim to hold materials
        omni.kit.commands.execute(
            'CreatePrim',
            prim_path='/World/Looks',
            prim_type='Scope',
            select_new_prim=False)
        
        # create prim to hold emitters
        omni.kit.commands.execute(
            'CreatePrim',
            prim_path='/World/emitters',
            prim_type='Scope',
            select_new_prim=False)
        
        # Create the material path
        omni.kit.commands.execute(
            'CreateAndBindMdlMaterialFromLibrary',
            mdl_name='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Glass/Clear_Glass.mdl',
            mtl_name='Clear_Glass',
            mtl_created_list=[self.material_path],
            select_new_prim=False)
        
        # create the material prim
        omni.kit.commands.execute(
            'CreateMdlMaterialPrim',
            mtl_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Glass/Clear_Glass.mdl',
            mtl_name='Clear_Glass',
            mtl_path=self.material_path,
            select_new_prim=False)
        
        # make material red
        omni.kit.commands.execute(
            'ChangeProperty',
            prop_path=Sdf.Path(f"{self.material_path}/Shader.inputs:glass_color"),
            value=Gf.Vec3f(1.0, 0.0, 0.0),
            prev=None,
            # target_layer=Sdf.Find('omniverse://localhost/Projects/soceur/google_maps_stage.usd'),
            # usd_context_name=Usd.Stage.Open(rootLayer=Sdf.Find('omniverse://localhost/Projects/soceur/google_maps_stage.usd'), sessionLayer=Sdf.Find('anon:00000246D28DF0E0'), pathResolverContext=<invalid repr>)
            )

    def create_spheres_for_emitters(self):
        # Iterate through emitters and create spheres
        for emitter in self.emitter_manager.get_emitters():
            self.create_or_update_sphere(emitter)

    def create_or_update_sphere(self, emitter):
        # Create or update a sphere based on emitter data
        prim_name = emitter['prim_name']
        if prim_name not in self.sphere_prims:
            # Create a new sphere if it doesn't exist
            sphere_path = self.create_sphere(emitter)
            self.sphere_prims[prim_name] = sphere_path
        else:
            # Update the existing sphere
            self.update_sphere(emitter)

    def create_sphere(self, emitter):
        # don't create empty spheres
        if emitter['radius'] == 0:
            return None
        
        sphere_path = f"/World/emitters/{emitter['prim_name']}"

        # Create Sphere
        omni.kit.commands.execute(
            'CreateMeshPrimWithDefaultXform',
            prim_type='Sphere',
            prim_path=sphere_path,
            select_new_prim=False,
            prepend_default_prim=True)
        
        # Bind the material to the new sphere
        omni.kit.commands.execute(
            'BindMaterial',
            prim_path=Sdf.Path(sphere_path),
            material_path=Sdf.Path(self.material_path),
            strength=None)
        
        # set global anchor
        xform_path = Sdf.Path(sphere_path)
        anchor_xform_at_path(
            xform_path,
            emitter['latitude'],
            emitter['longitude'],
            emitter['height']
            )

        # Execute the command to scale the sphere
        radius = emitter['radius']
        omni.kit.commands.execute(
            'ChangeProperty',
            prop_path=Sdf.Path(f"{sphere_path}.cesium:anchor:scale"),
            value=Gf.Vec3d(radius, radius, radius),
            prev=None)

        return sphere_path

    def update_sphere(self, emitter):
        self.delete_sphere(emitter['prim_name'])

        self.create_or_update_sphere(emitter)

    def clean_up_old_emitters(self):
        self.stage.RemovePrim(self.stage.GetPrimAtPath(Sdf.Path("/World/emitters")))
        # prims_to_delete = []
        # for prim in Usd.PrimRange(self.stage.GetPrimAtPath(Sdf.Path("/World/emitters"))):
        #     if prim.GetName() == 'emitters':
        #         continue
        #     else:
        #         # prims_to_delete.append(prim)
        #         self.stage.RemovePrim(prim.GetPath())
        # for prim in prims_to_delete:
            
        #     del self.sphere_prims[prim.GetName()]
        #     self.stage.RemovePrim(prim.GetPath())
            # omni.kit.commands.execute(
            #         'DeletePrims',
            #         paths=[Sdf.Path(prim.GetPath())],
            #         destructive=True)
        # good_emitter_names = [emitter['prim_name'] for emitter in self.emitter_manager.get_emitters()]
        # bad_emitter_prims = []
        # for prim in Usd.PrimRange(self.stage.GetPrimAtPath(Sdf.Path("/World/emitters"))):
        #     if prim.GetName() == 'emitters':
        #         continue
        #     elif prim.GetName() not in good_emitter_names:
        #         bad_emitter_prims.append(prim)
        # try:
        #     for prim in bad_emitter_prims:
        #         omni.kit.commands.execute(
        #             'DeletePrims',
        #             paths=[Sdf.Path(prim.GetPath())],
        #             destructive=False)
        #         del self.sphere_prims[prim.GetName()]
        # except Exception as e:
        #     pass


    def delete_sphere(self, prim_name):
        if prim_name in self.sphere_prims:
            sphere_path = self.sphere_prims[prim_name]
            omni.kit.commands.execute(
                'DeletePrims',
                paths=[Sdf.Path(sphere_path)],
                destructive=False)
            del self.sphere_prims[prim_name]
        else:
            print(f"No sphere found with prim_name: {prim_name}")

    def shutdown(self):
        self.clean_up_old_emitters()
