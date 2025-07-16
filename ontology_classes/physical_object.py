from rdflib import URIRef, Literal, Graph, RDF, RDFS
from .namespaces import s4bldg

class PhysicalObject:
    def __init__(self, uri, label=None, contained_in=None, contains=None):
        self.uri = URIRef(uri)
        self.label = label
        self.contained_in = contained_in  # BuildingSpace or PhysicalObject or URI
        self.contains = contains or []    # List of PhysicalObject objects

    def add_to_graph(self, g: Graph):
        g.add((self.uri, RDF.type, s4bldg.PhysicalObject))
        if self.label:
            g.add((self.uri, RDFS.label, Literal(self.label)))
        # Add isContainedIn relationship
        if self.contained_in:
            parent_uri = self.contained_in.uri if hasattr(self.contained_in, 'uri') else self.contained_in
            g.add((self.uri, s4bldg.isContainedIn, parent_uri))
            g.add((parent_uri, s4bldg.contains, self.uri))
        # Add contained objects
        for obj in self.contains:
            if getattr(obj, 'contained_in', None) is None:
                obj.contained_in = self
            obj.add_to_graph(g)
            # Relationships are handled in the child's add_to_graph

    def __str__(self):
        return f"PhysicalObject(uri={self.uri}, label={self.label}, contained_in={self.contained_in}, contains={self.contains})"
    
    def __repr__(self):
        return self.__str__() 