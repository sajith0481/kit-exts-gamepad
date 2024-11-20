import omni.kit.commands

class CameraManager:
    def __init__(self):
        self.camera_mode = 0  # 0: FPV Camera Off, 1: FPV Camera On

    def toggle_camera_mode(self):
        self.camera_mode = (self.camera_mode + 1) % 2  # Toggle between 0 and 1
        if self.camera_mode == 1:
            self.enable_fpv_camera_effects()
        else:
            self.disable_fpv_camera_effects()

    def enable_fpv_camera_effects(self):
        # Enable FPV camera effects
        settings = [
            '/rtx/post/tvNoise/enableFilmGrain',
            '/rtx/post/tvNoise/enableRandomSplotches',
            '/rtx/post/tvNoise/enableVerticalLines',
            '/rtx/post/tvNoise/enableWaveDistortion',
            '/rtx/post/tvNoise/enableGhostFlickering',
            '/rtx/post/tvNoise/enableScrollBug',
            '/rtx/post/tvNoise/enableScanlines',
            '/rtx/post/tvNoise/enabled'
        ]
        for setting in settings:
            omni.kit.commands.execute('ChangeSetting', path=setting, value=True)
        print("FPV Camera Effects Enabled")

    def disable_fpv_camera_effects(self):
        # Disable FPV camera effects
        settings = [
            '/rtx/post/tvNoise/enableFilmGrain',
            '/rtx/post/tvNoise/enableRandomSplotches',
            '/rtx/post/tvNoise/enableVerticalLines',
            '/rtx/post/tvNoise/enableWaveDistortion',
            '/rtx/post/tvNoise/enableGhostFlickering',
            '/rtx/post/tvNoise/enableScrollBug',
            '/rtx/post/tvNoise/enableScanlines',
            '/rtx/post/tvNoise/enabled'
        ]
        for setting in settings:
            omni.kit.commands.execute('ChangeSetting', path=setting, value=False)
        print("FPV Camera Effects Disabled")

    def shutdown(self):
        # Disable effects during shutdown
        self.disable_fpv_camera_effects()

