from rdflib import URIRef, Namespace, Literal, Graph, RDF, RDFS
from .namespaces import s4bldg, vcard

class Building:
    def __init__(
            self, uri, label=None, address=None, spaces=None
    ):
        self.uri = URIRef(uri)
        self.label = label
        self.address = address
        self.spaces = spaces or []  # list of BuildingSpace objects
    
    def add_to_graph(self, g: Graph):
        g.add((self.uri, RDF.type, s4bldg.Building))

        if self.label:
            g.add((self.uri, RDFS.label, Literal(self.label)))
        
        # Add address if available
        if self.address:
            self.address.add_to_graph(g)
            g.add((self.uri, vcard.hasAddress, self.address.uri))

        # Add spaces if available
        for space in self.spaces:
            space.add_to_graph(g)
            g.add((self.uri, s4bldg.hasSpace, space.uri))

    def __str__(self):
        return f"Building(uri={self.uri}, label={self.label}, address={self.address}, spaces={self.spaces})"
    
    def __repr__(self):
        return self.__str__()