from rdflib import URIRef, Namespace, Literal, Graph, RDF, RDFS
from .namespaces import s4bldg

class BuildingSpace:
    def __init__(
            self, uri, label=None, building=None, spaces=None, building_object=None, parent_space=None
    ):
        self.uri = URIRef(uri)
        self.label = label
        self.building = building  # Building object or URI
        self.spaces = spaces or []  # List of BuildingSpace objects
        self.building_object = building_object or []  # List of URIs (PhysicalObjects)
        self.parent_space = parent_space  # Parent BuildingSpace object or URI
    
    def add_to_graph(self, g: Graph):
        g.add((self.uri, RDF.type, s4bldg.BuildingSpace))

        if self.label:
            g.add((self.uri, RDFS.label, Literal(self.label)))
        
        # Add building relationship if available
        if self.building:
            g.add((self.uri, s4bldg.isSpaceOf, self.building.uri if hasattr(self.building, 'uri') else self.building))
            g.add(((self.building.uri if hasattr(self.building, 'uri') else self.building), s4bldg.hasSpace, self.uri))

        # Add parent space relationship if available
        if self.parent_space:
            g.add((self.uri, s4bldg.isSpaceOf, self.parent_space.uri if hasattr(self.parent_space, 'uri') else self.parent_space))
            g.add(((self.parent_space.uri if hasattr(self.parent_space, 'uri') else self.parent_space), s4bldg.hasSpace, self.uri))

        # Add contained physical objects
        for obj in self.building_object:
            # Add the physical object to the graph (includes type declaration)
            obj.add_to_graph(g)
            # Note: relationships are now handled in obj.add_to_graph()

        # Add nested spaces
        for space in self.spaces:
            # Set parent_space for child if not already set
            if getattr(space, 'parent_space', None) is None:
                space.parent_space = self
            space.add_to_graph(g)
            # Relationships are handled in the child's add_to_graph

    def __str__(self):
        return f"BuildingSpace(uri={self.uri}, label={self.label}, building={self.building}, spaces={self.spaces}, building_object={self.building_object}, parent_space={self.parent_space})"
    
    def __repr__(self):
        return self.__str__()
        