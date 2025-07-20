"""
Concrete implementation of BaseOntologyMapper for Concordia dataset.
"""

import sys
import os
from typing import Dict, List, Any
from rdflib import Graph, URIRef

# Add the parent directory to the path to import ontology_classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_mapper import BaseOntologyMapper
from .config import OntologyMappingConfig
from ontology_classes import (
    Building, Address, BuildingSpace, PhysicalObject, 
    Sensor, Gateway, Measurement, TimeInterval,
    get_feature_of_interest
)
from ontology_classes.namespaces import (
    s4bldg, vcard, saref, ssn, dcterms, schema, 
    time, s4watr, qudt, bigg
)
from rdflib.namespace import RDFS, RDF


class ConcordiaOntologyMapper(BaseOntologyMapper):
    """
    Concrete implementation for mapping Concordia data to ontology.
    """
    
    def create_building_objects(self, data: Dict[str, Any]) -> List[Any]:
        """Create building objects from the hierarchical data."""
        buildings = []
        address_lookup = self._create_address_lookup(data.get("addresses", []))
        
        for building_dict in data.get("buildings", []):
            building = Building(
                uri=building_dict["uri"],
                label=building_dict.get("label"),
                address=address_lookup.get(building_dict.get("address_uri")),
                spaces=[]
            )
            buildings.append(building)
        
        return buildings
    
    def create_address_objects(self, data: Dict[str, Any]) -> List[Any]:
        """Create address objects from the hierarchical data."""
        addresses = []
        
        for address_dict in data.get("addresses", []):
            address = Address(
                uri=address_dict["uri"],
                street_name=address_dict.get("street_name"),
                street_number=address_dict.get("street_number"),
                postal_code=address_dict.get("postal_code")
            )
            addresses.append(address)
        
        return addresses
    
    def create_spatial_objects(self, data: Dict[str, Any]) -> List[Any]:
        """Create spatial objects from the hierarchical data."""
        # This is handled in create_building_objects since desks 
        # (which are considered the only spatial objects in our structure)
        # are actually building objects. So, they are nested within buildings
        # in our structure.
        # This method (and other similar ones) is here for having a
        # complete implementation.
        return []
    
    def create_sensor_objects(self, data: Dict[str, Any]) -> List[Any]:
        """Create sensor objects from the hierarchical data."""
        # Sensors are created as part of the building hierarchy
        # This method is called separately for validation purposes
        return []
    
    def create_measurement_objects(self, data: Dict[str, Any]) -> List[Any]:
        """Create measurement objects from the hierarchical data."""
        # Measurements are created as part of sensor objects
        # This method is called separately for validation purposes
        return []
    
    def create_gateway_objects(self, data: Dict[str, Any]) -> List[Any]:
        """Create gateway objects from the hierarchical data."""
        # Gateways are created as part of the building hierarchy
        # This method is called separately for validation purposes
        return []
    
    def setup_namespaces(self, graph: Graph) -> None:
        """Set up ontology namespaces in the RDF graph."""
        graph.bind("s4bldg", s4bldg)
        graph.bind("vcard", vcard)
        graph.bind("rdfs", RDFS)
        graph.bind("rdf", RDF)
        graph.bind("saref", saref)
        graph.bind("ssn", ssn)
        graph.bind("dcterms", dcterms)
        graph.bind("schema", schema)
        graph.bind("time", time)
        graph.bind("s4watr", s4watr)
        graph.bind("qudt", qudt)
        graph.bind("bigg", bigg)
        
        # Add custom namespaces from config
        for prefix, namespace in self.config.custom_namespaces.items():
            graph.bind(prefix, namespace)
    
    def get_required_ontology_types(self) -> List[URIRef]:
        """Get list of required ontology types."""
        return [
            s4bldg.Building,
            s4bldg.BuildingSpace,
            s4bldg.PhysicalObject,
            saref.Device,
            saref.Sensor,
            saref.Measurement,
            ssn.System,
            time.TemporalEntity,
            time.ProperInterval,
            vcard.Address,
        ]
    
    def create_rdf_graph(self, data: Dict[str, Any]) -> Graph:
        """Create RDF graph from hierarchical data with proper object creation."""
        try:
            graph = Graph()
            
            # Setup namespaces
            self.setup_namespaces(graph)
            
            # Create address lookup
            address_lookup = self._create_address_lookup(data.get("addresses", []))
            
            # Create buildings with full hierarchy
            buildings = []
            for building_dict in data.get("buildings", []):
                building = Building(
                    uri=building_dict["uri"],
                    label=building_dict.get("label"),
                    address=address_lookup.get(building_dict.get("address_uri")),
                    spaces=[]
                )
                
                # Add floors and nested spaces
                for floor_dict in building_dict.get("spaces", []):
                    floor = self._create_building_space(floor_dict, building=building)
                    building.spaces.append(floor)
                
                buildings.append(building)
            
            # Add all buildings to graph
            for building in buildings:
                building.add_to_graph(graph)
            
            return graph
            
        except Exception as e:
            raise Exception(f"Failed to create RDF graph: {e}")
    
    def _create_address_lookup(self, addresses_list: List[Dict[str, Any]]) -> Dict[str, Address]:
        """Create address lookup dictionary."""
        lookup = {}
        for address_dict in addresses_list:
            address = Address(
                uri=address_dict["uri"],
                street_name=address_dict.get("street_name"),
                street_number=address_dict.get("street_number"),
                postal_code=address_dict.get("postal_code")
            )
            lookup[address_dict["uri"]] = address
        return lookup
    
    def _create_building_space(self, space_dict: Dict[str, Any], parent=None, building=None) -> BuildingSpace:
        """Create BuildingSpace with support for sensors and measurements."""
        # Only set .building for top-level spaces (floors)
        is_top_level = parent is None and building is not None
        space = BuildingSpace(
            uri=space_dict["uri"],
            label=space_dict.get("label"),
            parent_space=parent,
            building=building if is_top_level else None,
            spaces=[],
            building_object=[]
        )
        
        # Recursively add child spaces
        for child_space_dict in space_dict.get("spaces", []):
            child_space = self._create_building_space(child_space_dict, parent=space, building=building)
            space.spaces.append(child_space)
        
        # Add building objects (desks, sensors, and gateways)
        for obj_dict in space_dict.get("building_object", []):
            # Check if it's a sensor (has sensorType)
            if "sensorType" in obj_dict:
                # It's a sensor
                sensor = self._create_sensor(obj_dict, parent=space)
                space.building_object.append(sensor)
            # Check if it's a gateway (has gatewayUID)
            elif "gatewayUID" in obj_dict:
                # It's a gateway
                gateway = self._create_gateway(obj_dict, parent=space)
                space.building_object.append(gateway)
            else:
                # It's a desk or other physical object
                obj = self._create_physical_object(obj_dict, parent=space)
                space.building_object.append(obj)
        
        return space
    
    def _create_sensor(self, sensor_dict: Dict[str, Any], parent=None) -> Sensor:
        """Create Sensor object from sensor dictionary."""
        sensor = Sensor(
            uri=sensor_dict["uri"],
            sensorUID=sensor_dict.get("sensorUID"),
            sensorId=sensor_dict.get("sensorId"),
            vendorName=sensor_dict.get("vendorName"),
            installationDate=sensor_dict.get("installationDate"),
            contained_in=parent
        )
        
        # Set gateway connection if present
        if "gateway_connection" in sensor_dict:
            sensor.gateway_connection = URIRef(sensor_dict["gateway_connection"])
        
        # Build measurement if present
        if "measurement" in sensor_dict:
            measurement = self._create_measurement(sensor_dict["measurement"], sensor_dict["uri"])
            sensor.has_measurement = measurement
        
        return sensor
    
    def _create_gateway(self, gateway_dict: Dict[str, Any], parent=None) -> Gateway:
        """Create Gateway object from gateway dictionary."""
        return Gateway(
            uri=gateway_dict["uri"],
            gatewayUID=gateway_dict.get("gatewayUID"),
            label=gateway_dict.get("label"),
            contained_in=parent
        )
    
    def _create_physical_object(self, obj_dict: Dict[str, Any], parent=None) -> PhysicalObject:
        """Create PhysicalObject (desk) with nested sensors."""
        obj = PhysicalObject(
            uri=obj_dict["uri"],
            label=obj_dict.get("label"),
            contained_in=parent,
            deskDescription=obj_dict.get("deskDescription")
        )
        
        # Handle nested sensors in desks
        if "contains" in obj_dict:
            for sensor_dict in obj_dict["contains"]:
                sensor = self._create_sensor(sensor_dict, parent=obj)
                obj.contains.append(sensor)
        
        return obj
    
    def _create_measurement(self, measurement_dict: Dict[str, Any], sensor_uri: str) -> Measurement:
        """Create Measurement object from measurement dictionary."""
        if not measurement_dict:
            return None
        
        # Create measurement URI if not provided
        measurement_uri = measurement_dict.get("uri")
        if not measurement_uri:
            measurement_uri = f"{sensor_uri}_measurement"
        
        # Get feature of interest from sensor type
        sensor_type = measurement_dict.get("sensor_type")
        measured_property = measurement_dict.get("measured_property")
        if measured_property and not isinstance(measured_property, URIRef):
            measured_property = URIRef(measured_property)
        elif not measured_property and sensor_type:
            measured_property = get_feature_of_interest(sensor_type)
            if measured_property and not isinstance(measured_property, URIRef):
                measured_property = URIRef(measured_property)
        
        # Build time interval if available
        time_interval = None
        if "time_interval" in measurement_dict:
            time_interval = self._create_time_interval(measurement_dict["time_interval"])
        
        return Measurement(
            uri=measurement_uri,
            time_interval=time_interval,
            measured_property=measured_property,
            unit=measurement_dict.get("unit"),
            sensor_type=sensor_type
        )
    
    def _create_time_interval(self, time_interval_str: str) -> TimeInterval:
        """Create TimeInterval object from time interval string."""
        if not time_interval_str:
            return None
        
        # Create URI for time interval
        time_interval_uri = f"http://concordia.ca/timeInterval/{time_interval_str}"
        return TimeInterval(
            uri=time_interval_uri,
            time_interval=float(time_interval_str) if time_interval_str else None
        ) 