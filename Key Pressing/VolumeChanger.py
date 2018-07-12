import subprocess


class VolumeChanger:

    def __init__(self):
        self.VOLUME_DELTA = 6
        self.previous_volume = None
        return

    @staticmethod
    def get_volume():
        volume = int(subprocess.check_output(["osascript",
                                             "-e", "output volume of (get volume settings)"]))
        return volume

    @staticmethod
    def set_volume(new_volume):
        subprocess.Popen(["osascript", "-e", "set volume output volume " + str(new_volume)])
        return

    def mute(self):
        self.previous_volume = self.get_volume()
        self.set_volume(0)
        return

    def unmute(self):
        self.set_volume(self.previous_volume)
        return

    def increment_volume(self):
        current_volume = self.get_volume()
        new_volume = current_volume + self.VOLUME_DELTA
        self.set_volume(new_volume)
        return

    def decrement_volume(self):
        current_volume = self.get_volume()
        new_volume = current_volume - self.VOLUME_DELTA
        self.set_volume(new_volume)
        return

    def set_specific_volume(self, volume):
        if volume < 100:
            self.set_volume(volume)
        return
