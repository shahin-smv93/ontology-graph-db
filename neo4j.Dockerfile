FROM neo4j:5.20.0-community

ENV NEO4J_ACCEPT_LICENSE_AGREEMENT=yes

RUN apt-get update && apt-get install -y curl python3 python3-pip \
    && python3 -m pip install neo4j==5.20.0 \
    && apt-get clean && rm -rd /var/lib/apt/lists/*

# Copy configuration and plugins (these will be in named volumes)
COPY ./temp_config/neo4j.conf /var/lib/neo4j/conf/neo4j.conf
COPY ./temp_plugins/*.jar /var/lib/neo4j/plugins/

# Copy ontology files (these are static and don't need to be mounted as volumes)
COPY ./biggontology/ontology/ontology.ttl /var/lib/neo4j/import/
COPY ./ontology/dictionaries/bigg_enums/*.ttl /var/lib/neo4j/import/
COPY ./ontology/dictionaries/qudt.ttl /var/lib/neo4j/import/
COPY ./extensions.ttl /var/lib/neo4j/import/

EXPOSE 7474 7687 7473