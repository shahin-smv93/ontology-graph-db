from rdflib import URIRef, Literal, Graph, RDF
from .namespaces import saref, time, s4watr, qudt

class Measurement:
    def __init__(self, uri, time_interval=None, measured_property=None, unit=None, sensor_type=None):
        self.uri = URIRef(uri)
        self.time_interval = time_interval
        self.measured_property = measured_property
        self.unit = unit
        self.sensor_type = sensor_type  # Store the original sensor type for reference

    def add_to_graph(self, g: Graph):
        g.add((self.uri, RDF.type, saref.Measurement))

        if self.measured_property:
            g.add((self.uri, saref.isMeasurementOf, self.measured_property))
        
        if self.unit:
            g.add((self.uri, saref.isMeasuredIn, URIRef(f"{qudt}{self.unit}")))


        if self.time_interval:
            time_interval_uri = self.time_interval.uri if hasattr(self.time_interval, 'uri') else self.time_interval
            g.add((self.uri, s4watr.hasPhenomenonTime, time_interval_uri))
    
    def __str__(self):
        return f"Measurement(uri={self.uri}, measured_property={self.measured_property}, unit={self.unit}, time_interval={self.time_interval})"
    
    def __repr__(self):
        return self.__str__()


class TimeInterval:
    def __init__(self, uri, time_interval=None):
        self.uri = URIRef(uri)
        self.time_interval = time_interval

    def add_to_graph(self, g):
        g.add((self.uri, RDF.type, time.Interval))
        g.add((self.uri, RDF.type, time.TemporalEntity))

        if self.time_interval:
            g.add((self.uri, time.hasDuration, Literal(self.time_interval, datatype="http://www.w3.org/2001/XMLSchema#float")))

    def __str__(self):
        return f"TemporalEntity(uri={self.uri}, time_interval={self.time_interval})"
    def __repr__(self):
        return self.__str__()
