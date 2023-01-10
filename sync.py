# Synchronizes weight measured by a Polar Balance scale to Garmin Connect
# Author: S. Post, http://www.sydspost.nl
# Version: 1.0
# Date: 10 januari 2023
# Thanks to: Bastien Adabie for garmin_uploader https://github.com/La0/garmin-uploader
#            Matt Tucker for Fit-tool https://pypi.org/project/fit-tool/
#            Polar Electro for AccessLink https://github.com/polarofficial/accesslink-example-python

import datetime
import json
import subprocess
import sys
import platform
import garmin_uploader

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.weight_scale_message import WeightScaleMessage
from fit_tool.profile.profile_type import Manufacturer, FileType

from utils import load_config, pretty_print_json
from accesslink import AccessLink


# Provide Client id and secret
CONFIG_FILENAME = "config.yml"

# Define PolarAccessLink class, snippet out of accesslink-example-python https://github.com/polarofficial/accesslink-example-python/blob/master/accesslink/accesslink.py
class PolarAccessLink(object):
    weight = 0
    registration_date = ""

    def __init__(self):
        self.config = load_config(CONFIG_FILENAME)

        if "access_token" not in self.config:
            print("[Error] Authorization is required. Run authorization.py first.")
            return

        self.accesslink = AccessLink(client_id=self.config["client_id"],
                                     client_secret=self.config["client_secret"])

        self.running = True
        self.get_user_information()

    def get_user_information(self):
        print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] Try to login on Polar AccessLink...")
        user_info = self.accesslink.users.get_information(user_id=self.config["user_id"], 
                                     access_token=self.config["access_token"])
        print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] Get last weight measurement")
        self.weight = user_info["weight"]
        self.registration_date = user_info["registration-date"]

    def exit(self):
        self.running = False

# Calculates Time in seconds from epoch "01-01-1970 00:00"
def time_in_seconds(dt):
    epoch = datetime.datetime.strptime("00:00 Jan 01 1970", '%H:%M %b %d %Y')
    delta = dt - epoch
    return delta.total_seconds() - 3600      # Timezone correction of 3600 sec., adjust according to your Timezone

# The magic happens here
def main():
    # Get last weight information for Polar Flow
    info = PolarAccessLink()

    # Check of there is a previous weight measurement present, if so, open file
    try:
        f = open('weight.json', 'r')
        fileOpened = True
        print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] Previous weight measurement present")
    except OSError:
        fileOpened = False
        newData = True
        print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] No Previous weight measurement present")

    # If file opened succesful, read json content
    if fileOpened:
        data = json.load(f)
        # Check if this is a new weight measure
        if data['timestamp'] == info.registration_date:
            newData = False
            print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] No new weight measurement present")
        else:
            newData = True
            print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] New weight measurement present")
        f.close()

    # If there is a new weight measure, continue, else exit program without doing anything
    if newData:

	# Define FIT header
        file_id_message = FileIdMessage()
        file_id_message.type = FileType.WEIGHT
        file_id_message.manufacturer = Manufacturer.DEVELOPMENT.value
        file_id_message.product = 0
        file_id_message.serial_number = 0x12345678
        file_id_message.time_created = round(datetime.datetime.now().timestamp() * 1000)
        file_id_message.number = 0

	# Define FIT weightscale message
        weightscale_message = WeightScaleMessage()
        weightscale_message.weight = info.weight
        weightscale_message.timestamp = time_in_seconds(datetime.datetime.strptime(info.registration_date[:19], '%Y-%m-%dT%H:%M:%S')) * 1000

        # Build FIT file based on header and weightscale message
        builder = FitFileBuilder(auto_define=True, min_string_size=50)
        builder.add(file_id_message)
        builder.add(weightscale_message)

        fit_file = builder.build()

        # Write to FIT file
        fit_file.to_file('weight.fit')
        print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] Wrote weight.fit file to disk")

        # Build JSON string to save new weight measure
        weight = {}
        weight['timestamp'] = info.registration_date
        weight['weight'] = info.weight

        # Save JSON string to file
        with open('weight.json', 'w') as f:
            json.dump(weight, f)

        f.close()
        print(datetime.datetime.now().isoformat(timespec='milliseconds') + " [INFO] Save new weight measurement to file weight.json")

        # load FIT file up to https://connect.garmin.com/
        cli = garmin_uploader.__path__[0] + "/cli.py"
        subprocess.call(["python", cli, "weight.fit"])


if __name__ == "__main__":
    main()