import json

class Database():
    def __init__(self):
        self.channel_info = {}
    
    def save(self, channel, setting, value):
        if not channel in self.channel_info:
            self.channel_info[channel] = {}
        self.channel_info[channel][setting] = value
#        
    def load(self, channel, setting):
        settings = self.channel_info.get(channel, {})
        return settings.get(setting)