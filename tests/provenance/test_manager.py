"""
Test Unified Provenance Manager

Tests for ProvenanceManager functionality including entity tracking,
chunk tracking, source tracking, and lineage tracing.
"""

import pytest
from semantica.provenance import ProvenanceManager, SourceReference


class TestProvenanceManager:
    """Test ProvenanceManager functionality."""
    
    def test_initialization(self):
        """Test manager initialization."""
        prov_mgr = ProvenanceManager()
        
        assert prov_mgr is not None
        assert prov_mgr.storage is not None
    
    def test_track_entity(self):
        """Test tracking entity provenance."""
        prov_mgr = ProvenanceManager()
        
        entry = prov_mgr.track_entity(
            entity_id="entity_1",
            source="doc_1",
            metadata={"confidence": 0.9}
        )
        
        assert entry is not None
        assert entry.entity_id == "entity_1"
        assert entry.source_document == "doc_1"
        assert entry.checksum is not None
    
    def test_track_relationship(self):
        """Test tracking relationship provenance."""
        prov_mgr = ProvenanceManager()
        
        entry = prov_mgr.track_relationship(
            relationship_id="rel_1",
            source="doc_1",
            metadata={"type": "founded"}
        )
        
        assert entry is not None
        assert entry.entity_id == "rel_1"
        assert entry.entity_type == "relationship"
    
    def test_track_chunk(self):
        """Test tracking chunk provenance."""
        prov_mgr = ProvenanceManager()
        
        entry = prov_mgr.track_chunk(
            chunk_id="chunk_1",
            source_document="doc_1",
            source_path="/path/to/doc.pdf",
            start_index=0,
            end_index=500
        )
        
        assert entry is not None
        assert entry.entity_id == "chunk_1"
        assert entry.entity_type == "chunk"
        assert entry.start_index == 0
        assert entry.end_index == 500
    
    def test_track_property_source(self):
        """Test tracking property source."""
        prov_mgr = ProvenanceManager()
        
        source = SourceReference(
            document="DOI:10.1038/...",
            page=4,
            confidence=0.92
        )
        
        entry = prov_mgr.track_property_source(
            entity_id="entity_1",
            property_name="biomass_increase",
            value="463%",
            source=source
        )
        
        assert entry is not None
        assert entry.entity_type == "property"
        assert entry.metadata["property_name"] == "biomass_increase"
    
    def test_get_lineage(self):
        """Test getting complete lineage."""
        prov_mgr = ProvenanceManager()
        
        # Create lineage chain
        prov_mgr.track_entity("entity_1", "doc_1")
        prov_mgr.track_chunk(
            chunk_id="chunk_1",
            source_document="doc_1",
            parent_chunk_id="entity_1"
        )
        
        lineage = prov_mgr.get_lineage("chunk_1")
        
        assert lineage is not None
        assert "lineage_chain" in lineage
        assert len(lineage["lineage_chain"]) > 0
    
    def test_batch_entity_tracking(self):
        """Test batch entity tracking."""
        prov_mgr = ProvenanceManager()
        
        entities = [
            {"id": "entity_1", "confidence": 0.9},
            {"id": "entity_2", "confidence": 0.85}
        ]
        
        count = prov_mgr.track_entities_batch(entities, "doc_1")
        
        assert count == 2
    
    def test_batch_chunk_tracking(self):
        """Test batch chunk tracking."""
        prov_mgr = ProvenanceManager()
        
        chunks = [
            {"id": "chunk_1", "start_index": 0, "end_index": 100},
            {"id": "chunk_2", "start_index": 100, "end_index": 200}
        ]
        
        count = prov_mgr.track_chunks_batch(chunks, "doc_1")
        
        assert count == 2
    
    def test_get_statistics(self):
        """Test getting provenance statistics."""
        prov_mgr = ProvenanceManager()
        
        prov_mgr.track_entity("entity_1", "doc_1")
        prov_mgr.track_chunk("chunk_1", "doc_1")
        
        stats = prov_mgr.get_statistics()
        
        assert stats["total_entries"] == 2
        assert "entity_types" in stats
    
    def test_clear(self):
        """Test clearing provenance data."""
        prov_mgr = ProvenanceManager()
        
        prov_mgr.track_entity("entity_1", "doc_1")
        count = prov_mgr.clear()
        
        assert count == 1
        
        lineage = prov_mgr.get_lineage("entity_1")
        assert lineage == {}

    def test_retrack_with_explicit_parent_overrides_history_link(self):
        """#742 — re-tracking an entity with an explicit parent_entity_id must
        honor the new value, not silently replace it with an auto-generated
        history pointer."""
        prov_mgr = ProvenanceManager()

        e1 = prov_mgr.track_entity("X", source="doc_1", parent_entity_id="parent_v1")
        e2 = prov_mgr.track_entity("X", source="doc_1", parent_entity_id="parent_v2")

        assert e1.parent_entity_id == "parent_v1"
        assert e2.parent_entity_id == "parent_v2"

    def test_retrack_without_explicit_parent_still_uses_history_link(self):
        """#742 — when NO explicit parent is given on a re-track call, the
        auto-generated history link (Y:v:<timestamp>) should still be used,
        preserving pre-existing behavior for callers that don't supply a parent."""
        prov_mgr = ProvenanceManager()

        y1 = prov_mgr.track_entity("Y", source="doc_1")
        y2 = prov_mgr.track_entity("Y", source="doc_1")

        assert y1.parent_entity_id is None
        assert y2.parent_entity_id is not None
        assert y2.parent_entity_id.startswith("Y:v:")
