import os
import sys
import x32

from channel import ChannelStrip
import database
import videorouter

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "videohub_emulator":
        videorouter.emulator()
    else:
        x32_address = os.environ.get("X32_ADDRESS", "")
        x32_port = int(os.environ.get("X32_PORT", "10300"))
        verbose = os.environ.get("VERBOSE", "false").lower() == "true"
        if not x32_address:
            sys.exit("You must provide an ip address of an x32 as X32_ADDRESS")
        board = x32.BehringerX32(x32_address, x32_port, verbose)
        
        vhub_address = os.environ.get("VHUB_ADDRESS", "")
        vhub_port = int(os.environ.get("VHUB_PORT", "9990"))
        if not vhub_address:
            sys.exit("You must provide an ip address of a videohub router as VHUB_ADDRESS")
        router = videorouter.VideoHub(vhub_address, vhub_port)
        router.start()
        
        mapping_string = os.environ.get("CHANNEL_MAPPING", "")
        if not mapping_string:
            sys.exit("You must provide a channel mapping in the form 0.0:1,0.1:2,etc where 0.1:14 maps video router output 0 audio channel 1 to x32 channel 14")
        channel_map = {}
        for mapping in mapping_string.split(","):
            src, dest = mapping.split(":")
            vhub_output, sdi_audio = src.split(".")
            vhub_output = int(vhub_output)
            sdi_audio = int(sdi_audio)
            if not vhub_output in channel_map:
                channel_map[vhub_output] = {}
            channel_map[vhub_output][sdi_audio] = int(dest)
        
        print("Channel Mappings:")
        for vhub_output, mapping in channel_map.items():
            for sdi_audio, x32_channel in mapping.items():
                print(f" {vhub_output}.{sdi_audio} -> {x32_channel}")
                
        input_string = os.environ.get("INPUT_LIST", "")
        channels = {}
        for input_name in input_string.strip().split(","):
            vhub_input, audio_channel = input_name.split(".")
            vhub_input = int(vhub_input)
            audio_channel = int(audio_channel)
            if not vhub_input in channels:
                channels[vhub_input] = {}
            channels[vhub_input][audio_channel] = ChannelStrip(board, vhub_input, audio_channel)

        def x32_message(setting, value):
            for input, channelstrips in channels.items():
                for channel_name, channelstrip in channelstrips.items():
                    channelstrip.handle_update(setting, value)
                
        board.register_callback(x32_message)

        current_x32_map = {}
        
        while True:
            operation, *args = router.queue.get()
            if operation == "VIDEO OUTPUT ROUTING":
                output, input = args
                if not output in channel_map:
                    continue
                mappings = channel_map[output]
                for sdi_channel, x32_channel in mappings.items():
                    print(f"Remapping {input}.{sdi_channel} to {x32_channel}")
                    input_channel = f"{input}.{sdi_channel}"
                    if x32_channel in current_x32_map:
                        old_input, old_sdi_channel = current_x32_map[x32_channel].split(".")
                        old_channelstrip = channels.get(int(old_input), {}).get(int(old_sdi_channel), None)
                        if old_channelstrip:
                            old_channelstrip.remove_channel(x32_channel)
                    new_channelstrip = channels.get(int(input), {}).get(int(sdi_channel), None)
                    if new_channelstrip:
                        new_channelstrip.add_channel(x32_channel)
                    current_x32_map[x32_channel] = input_channel
            elif operation == "INPUT LABELS":
                input, label = args
                print(f"Updating label for {input} to {label}")
                for sdi_channel, channelstrip in channels.get(int(input), {}).items():
                    channelstrip.set_name(f"{label} {sdi_channel}")