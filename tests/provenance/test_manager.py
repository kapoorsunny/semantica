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

    def test_get_lineage_via_derived_from_metadata(self):
        """metadata['derived_from'] should link entities into the lineage chain
        even when they share a source URL rather than one being a known entity_id."""
        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(
            entity_id="doc:X",
            source="https://example.com/api",
            metadata={"content_type": "drug_label"},
        )
        prov_mgr.track_entity(
            entity_id="decision:Y",
            source="https://example.com/api",
            metadata={"derived_from": "doc:X"},
        )

        lineage = prov_mgr.get_lineage("decision:Y")

        assert lineage["entity_count"] == 2
        entity_ids = [e["entity_id"] for e in lineage["lineage_chain"]]
        assert "doc:X" in entity_ids
        assert "decision:Y" in entity_ids

    def test_derived_from_does_not_override_explicit_parent(self):
        """An explicit parent_entity_id kwarg should win over metadata['derived_from']."""
        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(entity_id="explicit_parent", source="doc_1")
        prov_mgr.track_entity(entity_id="ignored_parent", source="doc_1")
        entry = prov_mgr.track_entity(
            entity_id="child",
            source="doc_1",
            metadata={"derived_from": "ignored_parent"},
            parent_entity_id="explicit_parent",
        )

        assert entry.parent_entity_id == "explicit_parent"

    def test_derived_from_takes_precedence_over_source_as_entity_id(self):
        """If `source` happens to also be a known entity_id, an explicit
        metadata['derived_from'] should still win over that fallback linking."""
        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(entity_id="source_as_entity", source="doc_0")
        prov_mgr.track_entity(entity_id="real_parent", source="doc_0")
        entry = prov_mgr.track_entity(
            entity_id="child",
            source="source_as_entity",  # resolvable as an entity_id
            metadata={"derived_from": "real_parent"},
        )

        assert entry.parent_entity_id == "real_parent"

    def test_derived_from_nonexistent_entity_does_not_crash(self):
        """derived_from pointing at an entity that was never tracked should be
        stored as the parent link without raising, and lineage traversal should
        stop gracefully instead of erroring."""
        prov_mgr = ProvenanceManager()

        entry = prov_mgr.track_entity(
            entity_id="orphan_child",
            source="doc_1",
            metadata={"derived_from": "never_tracked"},
        )

        assert entry.parent_entity_id == "never_tracked"

        lineage = prov_mgr.get_lineage("orphan_child")
        entity_ids = [e["entity_id"] for e in lineage["lineage_chain"]]
        assert entity_ids == ["orphan_child"]

    def test_derived_from_non_string_is_ignored(self):
        """A non-string derived_from value (e.g. accidentally passing an int or
        list) should be ignored rather than raising or being used as a parent id."""
        prov_mgr = ProvenanceManager()

        entry = prov_mgr.track_entity(
            entity_id="entity_bad_derived_from",
            source="doc_1",
            metadata={"derived_from": 12345},
        )

        assert entry.parent_entity_id is None

    def test_derived_from_empty_string_is_ignored(self):
        """An empty-string derived_from is falsy and should not be treated as a parent link."""
        prov_mgr = ProvenanceManager()

        entry = prov_mgr.track_entity(
            entity_id="entity_empty_derived_from",
            source="doc_1",
            metadata={"derived_from": ""},
        )

        assert entry.parent_entity_id is None

    def test_derived_from_self_reference_does_not_infinite_loop(self):
        """An entity that (incorrectly) declares itself as its own derived_from
        parent should not cause get_lineage to hang or infinitely recurse."""
        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(
            entity_id="self_ref",
            source="doc_1",
            metadata={"derived_from": "self_ref"},
        )

        lineage = prov_mgr.get_lineage("self_ref")
        entity_ids = [e["entity_id"] for e in lineage["lineage_chain"]]
        assert entity_ids == ["self_ref"]

    def test_derived_from_multi_hop_chain(self):
        """derived_from links should chain transitively: A <- B <- C should
        all appear when tracing lineage from C."""
        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(entity_id="grandparent", source="doc_1")
        prov_mgr.track_entity(
            entity_id="parent",
            source="doc_1",
            metadata={"derived_from": "grandparent"},
        )
        prov_mgr.track_entity(
            entity_id="child",
            source="doc_1",
            metadata={"derived_from": "parent"},
        )

        lineage = prov_mgr.get_lineage("child")

        assert lineage["entity_count"] == 3
        entity_ids = {e["entity_id"] for e in lineage["lineage_chain"]}
        assert entity_ids == {"grandparent", "parent", "child"}

    def test_derived_from_without_metadata_dict_does_not_crash(self):
        """track_entity called with no metadata at all should behave as before
        (no parent link derived), exercising the `metadata and isinstance(...)` guard."""
        prov_mgr = ProvenanceManager()

        entry = prov_mgr.track_entity(entity_id="no_metadata_entity", source="doc_1")

        assert entry.parent_entity_id is None

    def test_get_lineage_metadata_prefers_queried_entity_over_ancestors(self):
        """Aggregated lineage metadata should let the queried entity's own
        values win over ancestor values on conflicting keys, matching the
        documented "most recent entry's metadata takes precedence" intent."""
        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(
            entity_id="ancestor",
            source="doc_1",
            metadata={"status": "draft", "shared_only_on_ancestor": True},
        )
        prov_mgr.track_entity(
            entity_id="descendant",
            source="doc_1",
            metadata={"status": "final", "derived_from": "ancestor"},
        )

        lineage = prov_mgr.get_lineage("descendant")

        assert lineage["metadata"]["status"] == "final"
        assert lineage["metadata"]["shared_only_on_ancestor"] is True

    def test_derived_from_accepts_non_dict_mapping(self):
        """metadata['derived_from'] should be honored for any Mapping
        implementation, not just a concrete dict (e.g. types.MappingProxyType
        or a custom collections.abc.Mapping)."""
        from types import MappingProxyType

        prov_mgr = ProvenanceManager()

        prov_mgr.track_entity(entity_id="mapping_parent", source="doc_1")
        entry = prov_mgr.track_entity(
            entity_id="mapping_child",
            source="doc_1",
            metadata=MappingProxyType({"derived_from": "mapping_parent"}),
        )

        assert entry.parent_entity_id == "mapping_parent"

        lineage = prov_mgr.get_lineage("mapping_child")
        assert lineage["entity_count"] == 2

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
