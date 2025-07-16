from rdflib import URIRef, Literal, Graph, RDF
from .namespaces import vcard

class Address:
    """
    Represents a vCard Address entity for RDF mapping.
    Supports street_name, street_number, and postal_code.
    """
    def __init__(
            self, uri, street_name: str = None,
            street_number: str = None, postal_code: str = None,
    ):
        self.uri = URIRef(uri)
        self.street_name = street_name
        self.street_number = street_number
        self.postal_code = postal_code

    def add_to_graph(self, g: Graph):
        g.add((self.uri, RDF.type, vcard.Address))

        # Add street-address if available
        if self.street_name or self.street_number:
            street_address = ""
            if self.street_number:
                street_address += str(self.street_number) + " "
            if self.street_name:
                street_address += self.street_name
            street_address = street_address.strip()
            if street_address:
                g.add((self.uri, vcard['street-address'], Literal(street_address)))

        # Add postal-code if available
        if self.postal_code:
            g.add((self.uri, vcard['postal-code'], Literal(self.postal_code)))

    def __str__(self):
        return f"Address(uri={self.uri}, street_name={self.street_name}, street_number={self.street_number}, postal_code={self.postal_code})"
    
    def __repr__(self):
        return self.__str__()