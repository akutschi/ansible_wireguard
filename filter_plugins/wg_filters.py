#!/usr/bin/python
class FilterModule(object):
    def filters(self):
        return {
            'hex_id': self.hex_id,
        }

    def hex_id(self, unique_id):
        hex_value = hex(unique_id).lstrip("0x")
        return hex_value
