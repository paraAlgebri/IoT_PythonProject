from marshmallow import Schema, fields

from lab1.src.shema.accelerometer_schema import AccelerometerSchema
from lab1.src.shema.gps_schema import GpsSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    time = fields.DateTime('iso')