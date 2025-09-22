"""
Knowledge Graph module for olKAN v2.0
Handles entity extraction and relationship mapping for datasets
"""

import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
import spacy
import networkx as nx
from dataclasses import dataclass
from datetime import datetime
import json
from app.core.config import settings


@dataclass
class Entity:
    """Represents an entity in the knowledge graph"""
    id: str
    name: str
    type: str  # PERSON, ORGANIZATION, LOCATION, CONCEPT, etc.
    confidence: float
    source_dataset: str
    metadata: Dict[str, Any] = None


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    id: str
    source_entity: str
    target_entity: str
    relationship_type: str  # RELATED_TO, PART_OF, LOCATED_IN, etc.
    confidence: float
    source_dataset: str
    metadata: Dict[str, Any] = None


class EntityExtractor:
    """Extracts entities from dataset metadata using NLP"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """Load the spaCy model"""
        try:
            self.nlp = spacy.load(self.model_name)
        except OSError:
            # Fallback to basic model if the specific model is not available
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Use blank model as last resort
                self.nlp = spacy.blank("en")
    
    def extract_entities(self, text: str, dataset_id: str) -> List[Entity]:
        """Extract entities from text"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity = Entity(
                id=f"{dataset_id}_{ent.text.lower().replace(' ', '_')}_{ent.label_}",
                name=ent.text,
                type=ent.label_,
                confidence=0.8,  # Default confidence
                source_dataset=dataset_id,
                metadata={
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                    "description": ent.description if hasattr(ent, 'description') else None
                }
            )
            entities.append(entity)
        
        return entities
    
    def extract_concepts(self, text: str, dataset_id: str) -> List[Entity]:
        """Extract domain-specific concepts from text"""
        # Simple keyword-based concept extraction
        # In a real implementation, this would use more sophisticated NLP
        concept_keywords = {
            "climate": ["temperature", "weather", "precipitation", "carbon", "emissions"],
            "economics": ["gdp", "inflation", "unemployment", "trade", "market"],
            "health": ["disease", "mortality", "healthcare", "medical", "treatment"],
            "education": ["students", "schools", "graduation", "literacy", "curriculum"],
            "technology": ["software", "hardware", "internet", "digital", "cyber"]
        }
        
        concepts = []
        text_lower = text.lower()
        
        for domain, keywords in concept_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    concept = Entity(
                        id=f"{dataset_id}_{domain}_{keyword}",
                        name=keyword,
                        type="CONCEPT",
                        confidence=0.7,
                        source_dataset=dataset_id,
                        metadata={"domain": domain, "keyword": keyword}
                    )
                    concepts.append(concept)
        
        return concepts


class RelationshipExtractor:
    """Extracts relationships between entities"""
    
    def __init__(self):
        self.relationship_patterns = {
            "LOCATED_IN": ["in", "at", "located", "based"],
            "PART_OF": ["part of", "belongs to", "member of"],
            "RELATED_TO": ["related to", "associated with", "connected to"],
            "CREATED_BY": ["created by", "developed by", "authored by"],
            "USES": ["uses", "utilizes", "employs", "applies"]
        }
    
    def extract_relationships(
        self, 
        entities: List[Entity], 
        text: str, 
        dataset_id: str
    ) -> List[Relationship]:
        """Extract relationships between entities"""
        relationships = []
        text_lower = text.lower()
        
        # Simple co-occurrence based relationship extraction
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Check if entities appear close to each other in text
                if self._entities_are_related(entity1, entity2, text_lower):
                    relationship = Relationship(
                        id=f"{dataset_id}_{entity1.id}_{entity2.id}_related",
                        source_entity=entity1.id,
                        target_entity=entity2.id,
                        relationship_type="RELATED_TO",
                        confidence=0.6,
                        source_dataset=dataset_id,
                        metadata={"extraction_method": "co_occurrence"}
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _entities_are_related(self, entity1: Entity, entity2: Entity, text: str) -> bool:
        """Check if two entities are related based on text proximity"""
        # Simple implementation - check if entities appear within 50 characters
        entity1_pos = text.find(entity1.name.lower())
        entity2_pos = text.find(entity2.name.lower())
        
        if entity1_pos == -1 or entity2_pos == -1:
            return False
        
        return abs(entity1_pos - entity2_pos) < 50


class KnowledgeGraph:
    """Main knowledge graph class that manages entities and relationships"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
    
    async def process_dataset(
        self, 
        dataset_id: str, 
        title: str, 
        description: str, 
        tags: List[str]
    ) -> Dict[str, Any]:
        """Process a dataset and extract entities and relationships"""
        # Combine text for processing
        text = f"{title} {description} {' '.join(tags)}"
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(text, dataset_id)
        concepts = self.entity_extractor.extract_concepts(text, dataset_id)
        all_entities = entities + concepts
        
        # Extract relationships
        relationships = self.relationship_extractor.extract_relationships(
            all_entities, text, dataset_id
        )
        
        # Add to knowledge graph
        for entity in all_entities:
            self.add_entity(entity)
        
        for relationship in relationships:
            self.add_relationship(relationship)
        
        return {
            "entities": [self._entity_to_dict(e) for e in all_entities],
            "relationships": [self._relationship_to_dict(r) for r in relationships],
            "total_entities": len(all_entities),
            "total_relationships": len(relationships)
        }
    
    def add_entity(self, entity: Entity):
        """Add an entity to the knowledge graph"""
        self.entities[entity.id] = entity
        self.graph.add_node(
            entity.id,
            name=entity.name,
            type=entity.type,
            confidence=entity.confidence,
            source_dataset=entity.source_dataset,
            metadata=entity.metadata
        )
    
    def add_relationship(self, relationship: Relationship):
        """Add a relationship to the knowledge graph"""
        self.relationships[relationship.id] = relationship
        self.graph.add_edge(
            relationship.source_entity,
            relationship.target_entity,
            relationship_type=relationship.relationship_type,
            confidence=relationship.confidence,
            source_dataset=relationship.source_dataset,
            metadata=relationship.metadata
        )
    
    def find_related_datasets(
        self, 
        dataset_id: str, 
        relationship_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Find datasets related to a given dataset through entities"""
        related_datasets = set()
        
        # Find entities from the source dataset
        source_entities = [
            entity_id for entity_id, entity in self.entities.items()
            if entity.source_dataset == dataset_id
        ]
        
        # Find related entities
        for entity_id in source_entities:
            # Get neighbors in the graph
            neighbors = list(self.graph.neighbors(entity_id))
            
            for neighbor_id in neighbors:
                neighbor_entity = self.entities.get(neighbor_id)
                if neighbor_entity and neighbor_entity.source_dataset != dataset_id:
                    # Check relationship type filter
                    if relationship_types:
                        edge_data = self.graph.get_edge_data(entity_id, neighbor_id)
                        if edge_data and edge_data.get('relationship_type') in relationship_types:
                            related_datasets.add(neighbor_entity.source_dataset)
                    else:
                        related_datasets.add(neighbor_entity.source_dataset)
        
        # Get dataset information
        result = []
        for related_dataset_id in related_datasets:
            dataset_entities = [
                self._entity_to_dict(entity) for entity in self.entities.values()
                if entity.source_dataset == related_dataset_id
            ]
            
            result.append({
                "dataset_id": related_dataset_id,
                "related_entities": dataset_entities,
                "relationship_strength": len(dataset_entities)
            })
        
        return sorted(result, key=lambda x: x["relationship_strength"], reverse=True)
    
    def get_entity_network(self, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get the network of entities around a given entity"""
        if entity_id not in self.entities:
            return {"error": "Entity not found"}
        
        # Get subgraph around the entity
        subgraph = nx.ego_graph(self.graph, entity_id, radius=depth)
        
        nodes = []
        edges = []
        
        for node_id in subgraph.nodes():
            entity = self.entities.get(node_id)
            if entity:
                nodes.append(self._entity_to_dict(entity))
        
        for source, target, data in subgraph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "relationship_type": data.get("relationship_type"),
                "confidence": data.get("confidence")
            })
        
        return {
            "entity": self._entity_to_dict(self.entities[entity_id]),
            "network": {
                "nodes": nodes,
                "edges": edges
            },
            "statistics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get overall knowledge graph statistics"""
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "total_datasets": len(set(entity.source_dataset for entity in self.entities.values())),
            "entity_types": {
                entity_type: len([e for e in self.entities.values() if e.type == entity_type])
                for entity_type in set(entity.type for entity in self.entities.values())
            },
            "relationship_types": {
                rel_type: len([r for r in self.relationships.values() if r.relationship_type == rel_type])
                for rel_type in set(rel.relationship_type for rel in self.relationships.values())
            },
            "graph_density": nx.density(self.graph),
            "connected_components": nx.number_connected_components(self.graph.to_undirected())
        }
    
    def export_graph(self, format: str = "json") -> str:
        """Export the knowledge graph in various formats"""
        if format == "json":
            return json.dumps({
                "entities": [self._entity_to_dict(e) for e in self.entities.values()],
                "relationships": [self._relationship_to_dict(r) for r in self.relationships.values()],
                "statistics": self.get_graph_statistics(),
                "exported_at": datetime.utcnow().isoformat()
            }, indent=2)
        elif format == "graphml":
            return "\n".join(nx.generate_graphml(self.graph))
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _entity_to_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.type,
            "confidence": entity.confidence,
            "source_dataset": entity.source_dataset,
            "metadata": entity.metadata
        }
    
    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        return {
            "id": relationship.id,
            "source_entity": relationship.source_entity,
            "target_entity": relationship.target_entity,
            "relationship_type": relationship.relationship_type,
            "confidence": relationship.confidence,
            "source_dataset": relationship.source_dataset,
            "metadata": relationship.metadata
        }


# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()
