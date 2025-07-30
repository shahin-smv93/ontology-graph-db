import utils.utils
from neo4j import GraphDatabase
import settings
import rdflib
config = utils.utils.read_config(settings.conf_file)

files = [
    ('ontology/dictionaries/qudt.ttl', 'Turtle'),
    ('ontology/dictionaries/bigg_enums/AreaType.ttl', 'Turtle'),
    ('ontology/dictionaries/bigg_enums/MainUses.ttl', 'Turtle'),
    ('ontology/dictionaries/bigg_enums/MeasuredProperty.ttl', 'Turtle'),
    ('ontology/dictionaries/bigg_enums/electricity_sector.ttl', 'Turtle'),
    ('ontology/dictionaries/bigg_enums/MeasurementUnit.ttl', 'Turtle')
]
neo = GraphDatabase.driver(**config['neo4j'])
for n in files:
    with open(n[0]) as f:
        content = f.read()
    content = content.replace('\\"', "&apos;")
    content = content.replace("'", "&apos;")
    with neo.session() as s:
        response = s.run(f"""CALL n10s.rdf.import.inline('{content}','{n[1]}')""")
        print(response.single())


