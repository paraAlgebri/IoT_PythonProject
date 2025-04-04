from marshmallow import Schema, fields

from src.shema.accelerometer_schema import AccelerometerSchema
from src.shema.gps_schema import GpsSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    time = fields.DateTime('iso')