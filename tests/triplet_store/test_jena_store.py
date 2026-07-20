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
        """
        triplet = Triplet(
            subject="http://example.org/Alice",
            predicate="http://example.org/knows",
            object="http://example.org/Bob",
        )

        with patch(
            "semantica.triplet_store.jena_store.SPARQLUpdateStore"
        ) as MockUpdateStore, patch(
            "semantica.triplet_store.jena_store.Graph"
        ) as MockGraph:
            mock_store_instance = MagicMock()
            MockUpdateStore.return_value = mock_store_instance

            mock_graph_instance = MagicMock(spec=Graph)
            # graph.add() must not raise – simulate a successful INSERT DATA
            mock_graph_instance.add.return_value = None
            MockGraph.return_value = mock_graph_instance

            store = JenaStore(endpoint=self._BASE)
            result = store.add_triplets([triplet])

        # add_triplets must report success
        self.assertTrue(result["success"])
        self.assertEqual(result["added"], 1)
        self.assertEqual(result["total"], 1)

        # graph.add() must have been called exactly once with the right triple
        from rdflib import URIRef
        mock_graph_instance.add.assert_called_once_with(
            (
                URIRef("http://example.org/Alice"),
                URIRef("http://example.org/knows"),
                URIRef("http://example.org/Bob"),
            )
        )


if __name__ == "__main__":
    unittest.main()
