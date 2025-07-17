from rdflib import URIRef, Literal, Graph, RDF, RDFS
from .namespaces import s4bldg, saref, ssn, dcterms, schema
from .physical_object import PhysicalObject
from .measurement import Measurement

class Sensor(PhysicalObject):
    def __init__(
            self, uri, sensorUID=None, sensorId=None, vendorName=None, 
            installationDate=None, gateway_connection=None, contained_in=None, has_measurement=None
    ):
        # Initialize as PhysicalObject first
        super().__init__(uri=uri, contained_in=contained_in)
        
        # Sensor-specific properties
        self.sensorUID = sensorUID
        self.sensorId = sensorId
        self.vendorName = vendorName
        self.installationDate = installationDate
        self.gateway_connection = gateway_connection  # Gateway object or URI
        self.has_measurement = has_measurement  # Measurement object or URI

    def add_to_graph(self, g: Graph):
        # Add PhysicalObject properties (type, label, containment)
        super().add_to_graph(g)
        
        # Add Sensor-specific types
        g.add((self.uri, RDF.type, saref.Sensor))
        g.add((self.uri, RDF.type, saref.Device))
        g.add((self.uri, RDF.type, ssn.System))

        # Add Sensor properties
        if self.sensorUID:
            g.add((self.uri, dcterms.identifier, Literal(self.sensorUID)))
        
        if self.sensorId:
            g.add((self.uri, schema.serialNumber, Literal(self.sensorId)))
        
        if self.vendorName:
            g.add((self.uri, RDFS.label, Literal(self.vendorName)))

        if self.installationDate:
            g.add((self.uri, dcterms.created, Literal(self.installationDate)))
        
        # Add gateway connection (bidirectional)
        if self.gateway_connection:
            gateway_uri = self.gateway_connection.uri if hasattr(self.gateway_connection, 'uri') else self.gateway_connection
            g.add((gateway_uri, ssn.hasSubSystem, self.uri))
            g.add((self.uri, ssn.isSubSystemOf, gateway_uri))
        
        if self.has_measurement:
            measurement_uri = self.has_measurement.uri if hasattr(self.has_measurement, 'uri') else self.has_measurement
            g.add((self.uri, saref.makesMeasurement, measurement_uri))
            # Add the measurement to the graph
            self.has_measurement.add_to_graph(g)
    
    def __str__(self):
        return f"Sensor(uri={self.uri}, sensorUID={self.sensorUID}, sensorId={self.sensorId}, vendorName={self.vendorName}, contained_in={self.contained_in})"
    
    def __repr__(self):
        return self.__str__()


class Gateway(PhysicalObject):
    def __init__(self, uri, gatewayUID=None, label=None, contained_in=None):
        # Initialize as PhysicalObject first
        super().__init__(uri=uri, contained_in=contained_in)
        
        # Gateway-specific properties
        self.gatewayUID = gatewayUID
        self.label = label

    def add_to_graph(self, g: Graph):
        # Add PhysicalObject properties (type, label, containment)
        super().add_to_graph(g)
        
        # Add Gateway-specific types
        g.add((self.uri, RDF.type, saref.Device))
        g.add((self.uri, RDF.type, ssn.System))

        # Add Gateway properties
        if self.gatewayUID:
            g.add((self.uri, dcterms.identifier, Literal(self.gatewayUID)))
        
        if self.label:
            g.add((self.uri, RDFS.label, Literal(self.label)))

    def __str__(self):
        return f"Gateway(uri={self.uri}, gatewayUID={self.gatewayUID}, label={self.label}, contained_in={self.contained_in})"
    
    def __repr__(self):
        return self.__str__()