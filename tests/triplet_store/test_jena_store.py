import unittest
from unittest.mock import patch, MagicMock
from rdflib import Graph, URIRef, Literal, Namespace
from semantica.triplet_store.jena_store import JenaStore
from semantica.semantic_extract.triplet_extractor import Triplet
from semantica.utils.exceptions import ValidationError
from semantica.triplet_store.construct_templates import execute_construct_template, ConstructTemplate

class TestJenaStoreExecuteSparqlConstructPath(unittest.TestCase):
    def setUp(self):
        self.store = JenaStore()
        # Ensure we use an in-memory graph
        self.store.graph = Graph()
        
    def test_construct_parses_triples_from_rdflib_natively(self):
        # Insert some test data
        self.store.graph.parse(data='<http://ex.org/s> <http://ex.org/p> <http://ex.org/o> .', format='nt')
        
        query = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"
        result = self.store.execute_sparql(query)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['bindings'], [])
        self.assertEqual(result['variables'], [])
        self.assertIn('triples', result)
        self.assertEqual(result['metadata']['result_format'], 'construct')
        
        triples = result['triples']
        self.assertEqual(len(triples), 1)
        s, p, o, meta = triples[0]
        self.assertEqual(s, 'http://ex.org/s')
        self.assertEqual(p, 'http://ex.org/p')
        self.assertEqual(o, 'http://ex.org/o')
        self.assertEqual(meta, {})

    def test_typed_literal_datatype_preserved_in_metadata(self):
        data = '<http://ex.org/s> <http://ex.org/age> "42"^^<http://www.w3.org/2001/XMLSchema#integer> .'
        self.store.graph.parse(data=data, format='nt')
        
        query = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"
        result = self.store.execute_sparql(query)
        
        triples = result['triples']
        self.assertEqual(len(triples), 1)
        s, p, o, meta = triples[0]
        self.assertEqual(o, '42')
        self.assertEqual(meta['datatype'], 'http://www.w3.org/2001/XMLSchema#integer')
        self.assertNotIn('language', meta)

    def test_language_tagged_literal_preserved_in_metadata(self):
        data = '<http://ex.org/s> <http://ex.org/label> "hello"@en .'
        self.store.graph.parse(data=data, format='nt')
        
        query = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"
        result = self.store.execute_sparql(query)
        
        triples = result['triples']
        self.assertEqual(len(triples), 1)
        s, p, o, meta = triples[0]
        self.assertEqual(o, 'hello')
        self.assertEqual(meta['language'], 'en')
        self.assertNotIn('datatype', meta)


class TestJenaStoreProperty9NonConstructUnchanged(unittest.TestCase):
    def setUp(self):
        self.store = JenaStore()
        self.store.graph = Graph()
        self.store.graph.parse(data='<http://ex.org/s> <http://ex.org/p> <http://ex.org/o> .', format='nt')
        
    def test_select_response_shape_unchanged(self):
        query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
        result = self.store.execute_sparql(query)
        
        self.assertTrue(result['success'])
        self.assertIn('bindings', result)
        self.assertEqual(len(result['bindings']), 1)
        self.assertNotIn('triples', result)
        self.assertEqual(result['metadata']['query'], query)
        
        binding = result['bindings'][0]
        self.assertEqual(binding['s']['value'], 'http://ex.org/s')
        self.assertEqual(binding['s']['type'], 'uri')

    def test_ask_uses_json_not_turtle_path(self):
        query = "ASK WHERE { ?s ?p ?o }"
        result = self.store.execute_sparql(query)
        
        self.assertTrue(result['success'])
        # For ASK in rdflib, results is a bool wrapped in SPARQLResult.
        # results.vars is None, so it returns empty bindings. This matches the byte-for-byte behavior.
        self.assertEqual(result['bindings'], [])
        self.assertNotIn('triples', result)

class TestExecuteConstructTemplateWithJenaBackend(unittest.TestCase):
    def setUp(self):
        self.store = JenaStore()
        self.store.graph = Graph()
        self.store.graph.parse(data='<http://ex.org/s> <http://ex.org/name> "Alice" .', format='nt')
        
    def test_end_to_end_with_jena_backend(self):
        template = ConstructTemplate(
            name="test",
            description="test",
            construct_query="""
        CONSTRUCT {
            ?s <http://ex.org/isPerson> "true"^^<http://www.w3.org/2001/XMLSchema#boolean> .
        } WHERE {
            ?s <http://ex.org/name> ?name .
        }
        """,
            parameters=[]
        )
        
        results = execute_construct_template(template, {}, self.store)
        self.assertEqual(len(results), 1)
        triplet = results[0]
        self.assertEqual(triplet.subject, 'http://ex.org/s')
        self.assertEqual(triplet.predicate, 'http://ex.org/isPerson')
        self.assertEqual(triplet.object, 'true')
        self.assertEqual(triplet.metadata.get('datatype'), 'http://www.w3.org/2001/XMLSchema#boolean')

class TestJenaStoreRemoteEndpointUsesUpdateStore(unittest.TestCase):
    """
    Tests for the SPARQLStore → SPARQLUpdateStore fix.

    Bug: _initialize_graph bound a read-only SPARQLStore for remote endpoints,
    causing every add_triplets() call to silently fail (TypeError swallowed,
    success=True/added=0 returned).

    Fix: SPARQLUpdateStore is now used, configured with both
    query_endpoint (<base>/query) and update_endpoint (<base>/update)
    per standard Apache Jena Fuseki REST API conventions.
    """

    _BASE = "http://localhost:3030/ds"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_remote_store(self):
        """Return a JenaStore wired to a fake remote endpoint."""
        from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

        with patch(
            "semantica.triplet_store.jena_store.SPARQLUpdateStore",
        ) as MockUpdateStore:
            # SPARQLUpdateStore.__init__ would normally try to contact the
            # server; the mock prevents any network I/O during init.
            mock_store_instance = MagicMock(spec=SPARQLUpdateStore)
            MockUpdateStore.return_value = mock_store_instance

            with patch("semantica.triplet_store.jena_store.Graph") as MockGraph:
                mock_graph_instance = MagicMock(spec=Graph)
                MockGraph.return_value = mock_graph_instance

                store = JenaStore(endpoint=self._BASE)
                return store, MockUpdateStore, MockGraph, mock_graph_instance

    # ------------------------------------------------------------------
    # Test 1 – correct class is instantiated
    # ------------------------------------------------------------------

    def test_remote_endpoint_instantiates_sparql_update_store_not_sparql_store(self):
        """
        _initialize_graph must use SPARQLUpdateStore, never the read-only SPARQLStore.
        """
        from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

        with patch(
            "semantica.triplet_store.jena_store.SPARQLUpdateStore"
        ) as MockUpdateStore, patch(
            "semantica.triplet_store.jena_store.SPARQLStore"
        ) as MockReadOnlyStore:
            MockUpdateStore.return_value = MagicMock()
            with patch("semantica.triplet_store.jena_store.Graph"):
                JenaStore(endpoint=self._BASE)

            MockUpdateStore.assert_called_once()
            MockReadOnlyStore.assert_not_called()

    # ------------------------------------------------------------------
    # Test 2 – correct Fuseki sub-paths are derived from base URL
    # ------------------------------------------------------------------

    def test_remote_endpoint_derives_fuseki_query_and_update_sub_paths(self):
        """
        Standard Fuseki datasets expose /query and /update under the dataset
        base URL.  The store must pass both to SPARQLUpdateStore.
        """
        with patch(
            "semantica.triplet_store.jena_store.SPARQLUpdateStore"
        ) as MockUpdateStore, patch("semantica.triplet_store.jena_store.Graph"):
            MockUpdateStore.return_value = MagicMock()

            JenaStore(endpoint=self._BASE)

            call_kwargs = MockUpdateStore.call_args
            # Accept both positional and keyword argument forms
            args, kwargs = call_kwargs
            passed = {**kwargs}
            if len(args) >= 1:
                passed.setdefault("query_endpoint", args[0])
            if len(args) >= 2:
                passed.setdefault("update_endpoint", args[1])

            self.assertEqual(
                passed.get("query_endpoint"),
                "http://localhost:3030/ds/query",
                "query_endpoint must be <base>/query",
            )
            self.assertEqual(
                passed.get("update_endpoint"),
                "http://localhost:3030/ds/update",
                "update_endpoint must be <base>/update",
            )

    def test_remote_endpoint_trailing_slash_is_normalised(self):
        """A trailing slash on the supplied endpoint must not produce double-slashes."""
        with patch(
            "semantica.triplet_store.jena_store.SPARQLUpdateStore"
        ) as MockUpdateStore, patch("semantica.triplet_store.jena_store.Graph"):
            MockUpdateStore.return_value = MagicMock()

            JenaStore(endpoint="http://localhost:3030/ds/")

            _, kwargs = MockUpdateStore.call_args
            self.assertNotIn(
                "//query",
                kwargs.get("query_endpoint", ""),
                "Trailing slash must be stripped before appending /query",
            )
            self.assertEqual(kwargs.get("query_endpoint"), "http://localhost:3030/ds/query")
            self.assertEqual(kwargs.get("update_endpoint"), "http://localhost:3030/ds/update")

    # ------------------------------------------------------------------
    # Test 3 – end-to-end write path: add_triplets fires INSERT DATA POST
    # ------------------------------------------------------------------

    def test_add_triplets_remote_endpoint_fires_insert_data_via_update_store(self):
        """
        End-to-end mock: add_triplets() against a remote-endpoint JenaStore must
        call graph.add() (which SPARQLUpdateStore maps to INSERT DATA).  We verify
        that graph.add() is actually invoked with the correct (subject, predicate,
        object) triple and that add_triplets returns success=True/added=1.

        This is distinct from the class-instantiation tests above: it confirms
        the write path works all the way through add_triplets(), not just that
        the right class gets constructed.

        After the Dataset migration the remote path creates Dataset(store=...),
        so we patch Dataset rather than Graph to intercept the construction.
        """
        from rdflib import Dataset, URIRef

        triplet = Triplet(
            subject="http://example.org/Alice",
            predicate="http://example.org/knows",
            object="http://example.org/Bob",
        )

        with patch(
            "semantica.triplet_store.jena_store.SPARQLUpdateStore"
        ) as MockUpdateStore, patch(
            "semantica.triplet_store.jena_store.Dataset"
        ) as MockDataset:
            mock_store_instance = MagicMock()
            MockUpdateStore.return_value = mock_store_instance

            mock_dataset_instance = MagicMock(spec=Dataset)
            # graph.add() must not raise — simulate a successful INSERT DATA
            mock_dataset_instance.add.return_value = None
            # graph.graph() is called to resolve named-graph context when graph=
            # is supplied.  It is NOT called in this test (no graph= option).
            MockDataset.return_value = mock_dataset_instance

            store = JenaStore(endpoint=self._BASE)
            result = store.add_triplets([triplet])

        # add_triplets must report success
        self.assertTrue(result["success"])
        self.assertEqual(result["added"], 1)
        self.assertEqual(result["total"], 1)

        # graph.add() must have been called exactly once with the 3-tuple
        # (no graph= option → default graph path → 3-tuple, no context arg)
        mock_dataset_instance.add.assert_called_once_with(
            (
                URIRef("http://example.org/Alice"),
                URIRef("http://example.org/knows"),
                URIRef("http://example.org/Bob"),
            )
        )


class TestJenaStoreDatasetMigration(unittest.TestCase):
    """
    Tests confirming the Graph → Dataset(default_union=False) migration.

    These tests specifically exercise _initialize_graph's real, unmodified
    path (no store.graph injection) to confirm the migration is in effect —
    unlike the existing test classes, which inject a plain Graph() directly
    and therefore don't exercise the initialization path at all.
    """

    # ------------------------------------------------------------------
    # Test 1 — unmodified _initialize_graph produces Dataset, not Graph
    # ------------------------------------------------------------------

    def test_initialize_graph_produces_dataset_not_graph(self):
        """
        The in-memory path of _initialize_graph must produce a Dataset instance,
        not a plain Graph.  This is the direct regression guard for the migration:
        if someone reverts the Dataset construction back to Graph() this test fails.
        """
        from rdflib import Dataset

        store = JenaStore()  # no endpoint → in-memory path

        self.assertIsInstance(
            store.graph,
            Dataset,
            "_initialize_graph must produce a Dataset, not a Graph",
        )

    def test_initialize_graph_dataset_has_default_union_false(self):
        """
        default_union must be explicitly False so that queries without a named
        graph scope see only the default graph, not a union across all graphs.
        """
        from rdflib import Dataset

        store = JenaStore()

        self.assertIsInstance(store.graph, Dataset)
        self.assertFalse(
            store.graph.default_union,
            "Dataset.default_union must be False (named-graph isolation)",
        )

    # ------------------------------------------------------------------
    # Test 2 — add_triplets with graph= writes to named graph, not default
    # ------------------------------------------------------------------

    def test_add_triplets_with_graph_option_writes_to_named_graph(self):
        """
        add_triplets(triplets, graph="http://example.org/g") must write triples
        to the specified named graph, not to the default graph.
        """
        from rdflib import Dataset, URIRef

        store = JenaStore()
        self.assertIsInstance(store.graph, Dataset)

        named_graph_uri = "http://example.org/named-graph"
        triplet = Triplet(
            subject="http://example.org/Alice",
            predicate="http://example.org/knows",
            object="http://example.org/Bob",
        )

        result = store.add_triplets([triplet], graph=named_graph_uri)

        self.assertTrue(result["success"])
        self.assertEqual(result["added"], 1)

        # Confirm the named graph now contains the triple
        named_ctx = store.graph.graph(URIRef(named_graph_uri))
        self.assertEqual(len(named_ctx), 1, "Named graph must hold the added triple")

        # Confirm the default graph does NOT contain it
        self.assertEqual(
            len(store.graph.default_graph),
            0,
            "Default graph must be empty when graph= option is used",
        )

    def test_add_triplets_without_graph_option_writes_to_default_graph(self):
        """
        When graph= is omitted (the common path), triples must go to the default
        graph — preserving pre-migration semantics exactly.
        """
        from rdflib import Dataset, URIRef

        store = JenaStore()

        triplet = Triplet(
            subject="http://example.org/Alice",
            predicate="http://example.org/knows",
            object="http://example.org/Bob",
        )

        result = store.add_triplets([triplet])  # no graph= option

        self.assertTrue(result["success"])
        self.assertEqual(result["added"], 1)

        # Triple is in the default graph
        self.assertEqual(
            len(store.graph.default_graph),
            1,
            "Triple without graph= must go to the default graph",
        )

    def test_add_triplets_named_graph_isolated_from_default_query(self):
        """
        A triple added to a named graph must NOT appear in a plain SELECT query
        (which, with default_union=False, sees only the default graph).
        This confirms the isolation guarantee end-to-end.
        """
        from rdflib import URIRef

        store = JenaStore()

        # Add to named graph
        store.add_triplets(
            [Triplet(
                subject="http://example.org/Named",
                predicate="http://example.org/type",
                object="http://example.org/Thing",
            )],
            graph="http://example.org/isolated",
        )

        # Also add to default graph so we can confirm query returns that one
        store.add_triplets([
            Triplet(
                subject="http://example.org/Default",
                predicate="http://example.org/type",
                object="http://example.org/Other",
            )
        ])

        # Plain SPARQL query (no FROM / GRAPH clause) should see only default
        result = store.execute_sparql("SELECT ?s WHERE { ?s ?p ?o }")
        subjects = [b["s"]["value"] for b in result["bindings"]]

        self.assertIn("http://example.org/Default", subjects)
        self.assertNotIn(
            "http://example.org/Named",
            subjects,
            "Named-graph triple must not appear in a default-graph-scoped query",
        )

    # ------------------------------------------------------------------
    # Test 3 — serialize() logs a warning when named-graph content is present
    # ------------------------------------------------------------------

    def test_serialize_logs_warning_when_named_graph_content_present(self):
        """
        serialize(format='turtle') serializes only the default graph.  When
        named-graph triples are also present, a WARNING must be logged so the
        data loss is not silent.
        """
        from unittest.mock import patch

        store = JenaStore()

        # Put one triple in each location
        store.add_triplets([
            Triplet(
                subject="http://example.org/S",
                predicate="http://example.org/P",
                object="default_val",
            )
        ])
        store.add_triplets(
            [Triplet(
                subject="http://example.org/S2",
                predicate="http://example.org/P",
                object="named_val",
            )],
            graph="http://example.org/ng",
        )

        with patch.object(store.logger, "warning") as mock_warn:
            output = store.serialize(format="turtle")

        # serialize must have returned something (the default graph)
        self.assertIsInstance(output, str)
        self.assertIn("default_val", output)
        self.assertNotIn("named_val", output)

        # Warning must have been logged
        mock_warn.assert_called_once()
        warn_msg = mock_warn.call_args[0][0]
        self.assertIn("named-graph", warn_msg.lower().replace("-", "-"))
        self.assertIn("trig", warn_msg.lower())

    def test_serialize_no_warning_when_only_default_graph_used(self):
        """
        serialize() must NOT log a warning when no named-graph content exists —
        this avoids noise for the common case where named graphs are not used.
        """
        from unittest.mock import patch

        store = JenaStore()
        store.add_triplets([
            Triplet(
                subject="http://example.org/S",
                predicate="http://example.org/P",
                object="default_only",
            )
        ])

        with patch.object(store.logger, "warning") as mock_warn:
            output = store.serialize(format="turtle")

        self.assertIn("default_only", output)
        mock_warn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
