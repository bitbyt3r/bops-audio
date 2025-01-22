import pathlib
import json

class ChannelStrip():
    def __init__(self, board, vhub_input, audio_channel):
        self.channels = set()
        self.board = board
        self.vhub_input = vhub_input
        self.audio_channel = audio_channel
        self.name = f"{vhub_input}.{audio_channel}"
        self.savefile = pathlib.Path("channels" / str(self.vhub_input) / str(self.audio_channel))
        if not self.savefile.parent.exists():
            self.savefile.parent.mkdir(parents=True)
        self.settings = {
            "/config/name": self.name,
            "/config/icon": None,
            "/config/color": "BL",
            #"/config/source": None,
            "/delay/on": None,
            "/delay/time": None,
            "/preamp/trim": None,
            "/preamp/invert": None,
            "/preamp/hpon": None,
            "/preamp/hpslope": None,
            "/preamp/hpf": None,
            "/gate/on": None,
            "/gate/mode": None,
            "/gate/thr": None,
            "/gate/range": None,
            "/gate/attack": None,
            "/gate/hold": None,
            "/gate/release": None,
            "/gate/keysrc": None,
            "/gate/filter/on": None,
            "/gate/filter/type": None,
            "/gate/filter/f": None,
            "/dyn/on": None,
            "/dyn/mode": None,
            "/dyn/det": None,
            "/dyn/env": None,
            "/dyn/thr": None,
            "/dyn/ratio": None,
            "/dyn/knee": None,
            "/dyn/mgain": None,
            "/dyn/attack": None,
            "/dyn/hold": None,
            "/dyn/pos": None,
            "/dyn/keysrc": None,
            "/dyn/filter/on": None,
            "/dyn/filter/type": None,
            "/dyn/filter/f": None,
            "/insert/on": None,
            "/insert/pos": None,
            "/insert/sel": None,
            "/eq/on": None,
            "/eq/1/type": None,
            "/eq/2/type": None,
            "/eq/3/type": None,
            "/eq/4/type": None,
            "/eq/1/f": None,
            "/eq/2/f": None,
            "/eq/3/f": None,
            "/eq/4/f": None,
            "/eq/1/g": None,
            "/eq/2/g": None,
            "/eq/3/g": None,
            "/eq/4/g": None,
            "/eq/1/q": None,
            "/eq/2/q": None,
            "/eq/3/q": None,
            "/eq/4/q": None,
            "/mix/on": None,
            "/mix/fader": None,
            "/mix/st": None,
            "/mix/pan": None,
            "/mix/mono": None,
            "/mix/mlevel": None,
            "/mix/01/on": None,
            "/mix/02/on": None,
            "/mix/03/on": None,
            "/mix/04/on": None,
            "/mix/05/on": None,
            "/mix/06/on": None,
            "/mix/07/on": None,
            "/mix/08/on": None,
            "/mix/09/on": None,
            "/mix/10/on": None,
            "/mix/11/on": None,
            "/mix/12/on": None,
            "/mix/13/on": None,
            "/mix/14/on": None,
            "/mix/15/on": None,
            "/mix/16/on": None,
            "/mix/01/level": None,
            "/mix/02/level": None,
            "/mix/03/level": None,
            "/mix/04/level": None,
            "/mix/05/level": None,
            "/mix/06/level": None,
            "/mix/07/level": None,
            "/mix/08/level": None,
            "/mix/09/level": None,
            "/mix/10/level": None,
            "/mix/11/level": None,
            "/mix/12/level": None,
            "/mix/13/level": None,
            "/mix/14/level": None,
            "/mix/15/level": None,
            "/mix/16/level": None,
            "/mix/01/pan": None,
            "/mix/01/type": None,
            "/mix/03/pan": None,
            "/mix/03/type": None,
            "/mix/05/pan": None,
            "/mix/05/type": None,
            "/mix/07/pan": None,
            "/mix/07/type": None,
            "/mix/09/pan": None,
            "/mix/09/type": None,
            "/mix/11/pan": None,
            "/mix/11/type": None,
            "/mix/13/pan": None,
            "/mix/13/type": None,
            "/mix/15/pan": None,
            "/mix/15/type": None,
            "/grp/dca": None,
            "/grp/mute": None
        }
        if self.savefile.exists():
            with open(self.savefile, "r") as savefile:
                self.settings.update(json.load(savefile))
                
    def save(self):
        with open(self.savefile, "w") as savefile:
            json.dump(self.settings, savefile, indent=2, sort_keys=True)
        
    def set_name(self, name):
        self.name = name
        self.settings["/config/name"] = name
        self.save()
        self.update_aliases()

    def update_aliases(self):
        if not self.channels:
            return
        first_channel = min(self.channels)
        for channel in self.channels:
            settings = dict(self.settings)
            if channel != first_channel:
                settings = {
                    "/config/name": f"@{self.name}",
                    "/config/color": "RD",
                    "/mix/on": "OFF"
                }
            for setting, value in settings.items():
                if not value is None:
                    self.board.set_value(f"/ch/{channel:02}{setting}", value)

    def add_channel(self, channel):
        if not channel in self.channels:
            if self.channels and channel == min(self.channels):
                self.settings["/min/on"] = "OFF"
            for setting, value in self.settings.items():
                if value is not None:
                    self.board.set_value(f"/ch/{channel:02}{setting}", value)
            self.channels.add(channel)
            self.update_aliases()
    
    def remove_channel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)
            self.board.set_value(f"/ch/{channel:02}/config/name", "")
            self.board.set_value(f"/ch/{channel:02}/config/color", "OFF")
            #self.board.set_value(f"/ch/{channel:02}/mix/fader", 0.0)
            self.board.set_value(f"/ch/{channel:02}/mix/on", "OFF")
            self.update_aliases()
            
    def handle_update(self, setting, value):
        if not self.channels:
            return
        dirty = False
        first_channel = min(self.channels)
        if setting.startswith(f"/ch/{first_channel:02}"):
            relative_setting = setting.split(f"/ch/{first_channel:02}", 1)[1]
            self.settings[relative_setting] = value
            dirty = True
            if not relative_setting in ["/mix/on", "/config/color", "/config/name"]:
                for channel in self.channels - {first_channel}:
                    print(f"Updating setting {setting} to {value}")
                    if value is not None:
                        self.board.set_value(f"/ch/{channel:02}{relative_setting}", value)
        if dirty:
            self.save()

        