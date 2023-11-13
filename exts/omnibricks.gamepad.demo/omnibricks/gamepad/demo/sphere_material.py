import omni.kit.commands
from pxr import Sdf, Gf, UsdGeom
from cesium.omniverse.api.globe_anchor import anchor_xform_at_path


class SphereMaterialHandler:
    def __init__(self, stage):
        self.stage = stage
        self.sphere_count = 0

    def create_sphere_and_material(self):
        # Increment the sphere count
        self.sphere_count += 1
        sphere_name = f'Signal{self.sphere_count}'
        sphere_path = f'/World/{sphere_name}'

        # Create Sphere with the incremented name
        omni.kit.commands.execute(
            'CreateMeshPrimWithDefaultXform',
            prim_type='Sphere',
            prim_path=sphere_path,
            select_new_prim=False,
            prepend_default_prim=True)

        # Create the material path for this instance
        material_path = f'/World/Looks/Clear_Glass{self.sphere_count}'

        omni.kit.commands.execute(
            'CreateAndBindMdlMaterialFromLibrary',
            mdl_name='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Glass/Clear_Glass.mdl',
            mtl_name=f'Clear_Glass',
            mtl_created_list=[material_path],
            select_new_prim=False)

        omni.kit.commands.execute(
            'CreatePrim',
            prim_path='/World/Looks',
            prim_type='Scope',
            select_new_prim=False)

        omni.kit.commands.execute(
            'CreateMdlMaterialPrim',
            mtl_url='http://omniverse-content-production.s3-us-west-2.amazonaws.com/Materials/Base/Glass/Clear_Glass.mdl',
            mtl_name='Clear_Glass',
            mtl_path=material_path,
            select_new_prim=False)

        # Bind the material to the new sphere
        omni.kit.commands.execute(
            'BindMaterial',
            prim_path=Sdf.Path(sphere_path),
            material_path=Sdf.Path(material_path),
            strength=None)
        
        return sphere_path, material_path

    def scale_sphere_to_radius(self, radius, sphere_path):
        new_scale = Gf.Vec3d(radius, radius, radius)

        # Turn on 'doNotCastShadows' for the sphere
        omni.kit.commands.execute(
            'ChangeProperty',
            prop_path=Sdf.Path(f"{sphere_path}.primvars:doNotCastShadows"),
            value=True,
            prev=None
        )

        # Execute the command to scale the sphere
        omni.kit.commands.execute(
            'ChangeProperty',
            prop_path=Sdf.Path(f"{sphere_path}.cesium:anchor:scale"),
            value=new_scale,
            prev=None
        )

    def set_global_anchor(self, latitude, longitude, height, sphere_path):
        xform_path = Sdf.Path(sphere_path)
        anchor_xform_at_path(xform_path, latitude, longitude, height)

    def create_signal(self, latitude, longitude, height, radius):
        # create spheres near stuttgart without having to enter coordinates
        # for testing and troubleshooting purposes
        if latitude == 0 and longitude == 0 and height == 0 and radius == 0:
            latitude = 48.73516
            longitude = 9.07533
            height = 250
            radius = 1000

        sphere_path, material_path = self.create_sphere_and_material()
        self.set_global_anchor(latitude, longitude, height, sphere_path)

        # Now, scale the sphere to the given radius
        self.scale_sphere_to_radius(radius, sphere_path)
