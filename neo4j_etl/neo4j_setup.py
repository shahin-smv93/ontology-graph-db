from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def neo4j_setup():
    env_neo4j = os.getenv('NEO4J_AUTH')
    if not env_neo4j:
        raise ValueError("NEO4J_AUTH is not defined in the env file")
    username, password = env_neo4j.split('/')

    neo4j_uri = 'bolt://neo4j:7687'

    ttl_files = [
        ('file:///var/lib/neo4j/import/ontology.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/qudt.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/AreaType.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/MainUses.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/MeasuredProperty.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/electricity_sector.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/MeasurementUnit.ttl', 'Turtle'),
        ('file:///var/lib/neo4j/import/extensions.ttl', 'Turtle')
    ]

    queries = [
        """
        CALL n10s.graphconfig.init({
            keepLangTag: true,
            handleMultival: "ARRAY",
            multivalPropList: [
                "http://bigg-project.eu/ontology#kpiType",
                "http://bigg-project.eu/ontology#shortName",
                "http://www.w3.org/2000/01/rdf-schema#label",
                "http://www.w3.org/2000/01/rdf-schema#comment",
                "http://www.geonames.org/ontology#officialName"
            ]
        });
        """,
        """
        CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS
          FOR (r:Resource)
          REQUIRE r.uri IS UNIQUE;
        """,
        # set namespace prefixes
        'CALL n10s.nsprefixes.add("schema","https://schema.org/");',
        'CALL n10s.nsprefixes.add("qudt", "http://qudt.org/vocab/unit/");',
        'CALL n10s.nsprefixes.add("vaem","http://www.linkedmodel.org/schema/vaem#");',
        'CALL n10s.nsprefixes.add("s4city","https://saref.etsi.org/saref4city/");',
        'CALL n10s.nsprefixes.add("owl","http://www.w3.org/2002/07/owl#");',
        'CALL n10s.nsprefixes.add("s4bldg","https://saref.etsi.org/saref4bldg/");',
        'CALL n10s.nsprefixes.add("gn","https://www.geonames.org/ontology#");',
        'CALL n10s.nsprefixes.add("saref","https://saref.etsi.org/core/");',
        'CALL n10s.nsprefixes.add("skos","http://www.w3.org/2004/02/skos/core#");',
        'CALL n10s.nsprefixes.add("bigg","http://bigg-project.eu/ontology#");',
        'CALL n10s.nsprefixes.add("rdfs","http://www.w3.org/2000/01/rdf-schema#");',
        'CALL n10s.nsprefixes.add("purl","http://purl.org/dc/terms/");',
        'CALL n10s.nsprefixes.add("vcard","http://www.w3.org/2006/vcard/ns#");',
        'CALL n10s.nsprefixes.add("ssn","http://www.w3.org/ns/ssn/");',
        'CALL n10s.nsprefixes.add("geo","http://www.w3.org/2003/01/geo/wgs84_pos#");',
        'CALL n10s.nsprefixes.add("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#");',
        'CALL n10s.nsprefixes.add("geosp","http://www.opengis.net/ont/geosparql#");',
        'CALL n10s.nsprefixes.add("s4syst","https://saref.etsi.org/saref4syst/");',
        'CALL n10s.nsprefixes.add("s4agri","https://saref.etsi.org/saref4agri/");',
        'CALL n10s.nsprefixes.add("time","http://www.w3.org/2006/time#");',
        'CALL n10s.nsprefixes.add("foaf","http://xmlns.com/foaf/0.1/");',
        'CALL n10s.nsprefixes.add("xsd","http://www.w3.org/2001/XMLSchema#");',
        'CALL n10s.nsprefixes.add("s4watr","https://saref.etsi.org/saref4watr/");'
    ]

    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        with driver.session() as session:
            for query in queries:
                try:
                    session.run(query=query)
                    logging.info(f"Executed query: {query.strip()}")
                except Exception as e:
                    logging.error(f"Error executing query {query.strip()}: {e}")
            for file_path, rdf_format in ttl_files:
                try:
                    load_query = f"CALL n10s.rdf.import.fetch('{file_path}', '{rdf_format}');"
                    session.run(load_query)
                    logging.info(f"TTL file {file_path} loaded")
                except Exception as e:
                    logging.error(f"Error loading TTL file {file_path}: {e}")
    except Exception as e:
        logging.error(f"Failed to connect to Neo4j: {e}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    neo4j_setup()