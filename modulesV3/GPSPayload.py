import struct
import math
from modules.Quaternion import Quaternion

class GPSPayloadV3:
    fields = ['date', 'time', 'longitude', 'latitude','velN','velE','velD','vel'
    ]
    _type = 2096
    payload = []
    data = {}

    def __init__(self, payload):
        self.payload = payload
        self.data = self.parse(self.payload)

    def convertpos(self, pos):
        # convert position from radians to degrees
        return math.degrees(pos)

    def mtoft(self, meter):
        # convert meters to feet
        return (meter * 3.2808)

    def parse(self, payload):
        #temp_file.write('packet has GPS\n')
        data = {}
        data['date'] = struct.unpack('I', payload[0:4])[0]

        data['time'] = struct.unpack('I', payload[4:8])[0]

        data['longitude'] = struct.unpack('f', payload[8:12])[0]  / 10**7   # parse double (float) longitude
        #data['longitude'] = self.convertpos(longitude)      # convert radians to degrees

        data['latitude'] = struct.unpack('f', payload[12:16])[0]  / 10**7   # parse double (float) latitude
        #data['latitude'] = self.convertpos(latitude)        # convert radians to degrees

        data['velN'] = struct.unpack('f', payload[20:24])[0] / 100
        data['velE'] = struct.unpack('f', payload[24:28])[0] / 100
        data['velD'] = struct.unpack('f', payload[28:32])[0] / 100
        data['vel'] = float(math.sqrt(math.pow(data['velN'],2) + math.pow(data['velE'],2) + math.pow(data['velD'],2)))

        # only output legitimate location data
        #if data['latitude'] == 0 or data['longitude'] == 0 or abs(data['latitude']) <= 0.0175 or abs(data['longitude']) <= 0.0175:
        #    data['longitude'] = ''
        #    data['latitude'] = ''
        return data
