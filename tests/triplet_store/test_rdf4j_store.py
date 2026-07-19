import os, sys, unittest
from unittest.mock import MagicMock, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from semantica.semantic_extract.triplet_extractor import Triplet
from semantica.triplet_store.rdf4j_store import RDF4JStore
from semantica.utils.exceptions import ProcessingError


def _make_connected_store():
    with patch.object(RDF4JStore, "_connect", autospec=True):
        store = RDF4JStore(
            endpoint="http://localhost:8080/rdf4j-server", repository_id="repo1"
        )
    store.connected = True
    return store


CONSTRUCT_QUERY = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"


class TestRDF4JStoreIsConstructQuery(unittest.TestCase):
    def test_detects_uppercase(self):
        self.assertTrue(_make_connected_store()._is_construct_query(
            "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"))
    def test_detects_lowercase(self):
        self.assertTrue(_make_connected_store()._is_construct_query(
            "construct { ?s ?p ?o } where { ?s ?p ?o }"))
    def test_detects_mixed_case(self):
        self.assertTrue(_make_connected_store()._is_construct_query(
            "Construct { ?s ?p ?o } Where { ?s ?p ?o }"))
    def test_detects_with_prefix_preamble(self):
        q = "PREFIX ex: <http://ex.org/>\nCONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"
        self.assertTrue(_make_connected_store()._is_construct_query(q))
    def test_detects_complex_preambles(self):
        s = _make_connected_store()
        cases = {
            "multiline_prefix": "PREFIX foaf:\n  <http://xmlns.com/foaf/0.1/>\nCONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
            "empty_prefix": "PREFIX : <http://ex.org/> CONSTRUCT { ?s ?p ?o }",
            "inline_comment": "PREFIX ex: <http://ex.org/>\n# comment\nCONSTRUCT { ?s ?p ?o }",
            "base_declaration": "BASE <http://ex.org/>\nCONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
        }
        for name, q in cases.items():
            with self.subTest(case=name):
                self.assertTrue(s._is_construct_query(q))
    def test_false_for_select(self):
        self.assertFalse(_make_connected_store()._is_construct_query(
            "SELECT ?s WHERE { ?s ?p ?o }"))
    def test_false_for_ask(self):
        self.assertFalse(_make_connected_store()._is_construct_query(
            "ASK { ?s ?p ?o }"))
    def test_no_false_positive_on_constructor_substring(self):
        self.assertFalse(_make_connected_store()._is_construct_query(
            'SELECT ?s WHERE { ?s <urn:p> "CONSTRUCTOR" }'))
    def test_no_false_positive_on_construct_in_string(self):
        self.assertFalse(_make_connected_store()._is_construct_query(
            'SELECT ?s WHERE { ?s <urn:p> "please CONSTRUCT this" }'))


class TestRDF4JStoreExecuteSparqlConstructPath(unittest.TestCase):
    def test_construct_sends_turtle_accept_header(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.content = b'@prefix ex: <http://ex.org/> .\nex:s1 ex:p1 "v" .\n'
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.execute_sparql(CONSTRUCT_QUERY)
        _, kw = mp.call_args
        self.assertEqual(kw["headers"]["Accept"], "text/turtle")
        self.assertEqual(kw["headers"]["Content-Type"], "application/x-www-form-urlencoded")

    def test_construct_parses_triples_from_turtle_fixture(self):
        store = _make_connected_store()
        fixture = (
            b'@prefix ex: <http://ex.org/> .\n'
            b'ex:s1 ex:p1 "value1" .\n'
            b'ex:s1 ex:p2 ex:o2 .\n'
        )
        mock_resp = MagicMock()
        mock_resp.content = fixture
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post", return_value=mock_resp):
            result = store.execute_sparql(CONSTRUCT_QUERY)
        self.assertTrue(result["success"])
        self.assertEqual(result["bindings"], [])
        self.assertEqual(result["variables"], [])
        self.assertEqual(result["metadata"]["result_format"], "construct")
        triples = {(s, p, o) for s, p, o, _m in result["triples"]}
        self.assertIn(("http://ex.org/s1", "http://ex.org/p1", "value1"), triples)
        self.assertIn(("http://ex.org/s1", "http://ex.org/p2", "http://ex.org/o2"), triples)
        self.assertEqual(len(result["triples"]), 2)
        for _s, _p, _o, meta in result["triples"]:
            self.assertEqual(meta, {})

    def test_result_format_construct_forces_construct_path(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.content = b'@prefix ex: <http://ex.org/> .\nex:s1 ex:p1 "v" .\n'
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            result = store.execute_sparql("SELECT ?s WHERE { ?s ?p ?o }", result_format="construct")
        _, kw = mp.call_args
        self.assertEqual(kw["headers"]["Accept"], "text/turtle")
        self.assertIn("triples", result)

    def test_malformed_turtle_raises_processing_error(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.content = b"this is { not [ valid turtle at all !!!"
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post", return_value=mock_resp):
            with self.assertRaises(ProcessingError) as ctx:
                store.execute_sparql(CONSTRUCT_QUERY)
        self.assertIsInstance(ctx.exception, ProcessingError)
        self.assertNotIsInstance(ctx.exception, (SyntaxError, ValueError))

    def test_typed_literal_datatype_preserved_in_metadata(self):
        store = _make_connected_store()
        fixture = (
            b'@prefix ex: <http://ex.org/> .\n'
            b'@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n'
            b'ex:s1 ex:p_age 42 .\n'
        )
        mock_resp = MagicMock()
        mock_resp.content = fixture
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post", return_value=mock_resp):
            result = store.execute_sparql(CONSTRUCT_QUERY)
        self.assertEqual(len(result["triples"]), 1)
        _s, _p, o, meta = result["triples"][0]
        self.assertEqual(o, "42")
        self.assertEqual(meta.get("datatype"), "http://www.w3.org/2001/XMLSchema#integer")
        self.assertNotIn("language", meta)

    def test_language_tagged_literal_preserved_in_metadata(self):
        store = _make_connected_store()
        fixture = b'@prefix ex: <http://ex.org/> .\nex:s2 ex:p_label "hello"@en .\n'
        mock_resp = MagicMock()
        mock_resp.content = fixture
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post", return_value=mock_resp):
            result = store.execute_sparql(CONSTRUCT_QUERY)
        self.assertEqual(len(result["triples"]), 1)
        _s, _p, o, meta = result["triples"][0]
        self.assertEqual(o, "hello")
        self.assertEqual(meta.get("language"), "en")
        self.assertNotIn("datatype", meta)

    def test_literal_with_braces_parsed_correctly(self):
        store = _make_connected_store()
        fixture = b'@prefix ex: <http://ex.org/> .\nex:s1 ex:p1 "text with { and } braces inside" .\n'
        mock_resp = MagicMock()
        mock_resp.content = fixture
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post", return_value=mock_resp):
            result = store.execute_sparql(CONSTRUCT_QUERY)
        self.assertEqual(len(result["triples"]), 1)
        _s, _p, obj, meta = result["triples"][0]
        self.assertEqual(obj, "text with { and } braces inside")
        self.assertEqual(meta, {})


class TestRDF4JStoreProperty9NonConstructUnchanged(unittest.TestCase):
    # RDF4J had Accept: application/sparql-results+json on non-CONSTRUCT before feat/754.
    # That header is preserved exactly. NOT aligned with Blazegraph headerless path.

    def test_select_response_shape_unchanged(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "head": {"vars": ["s", "p", "o"]},
            "results": {"bindings": [
                {"s": {"type": "uri", "value": "http://ex.org/s1"},
                 "p": {"type": "uri", "value": "http://ex.org/p1"},
                 "o": {"type": "literal", "value": "v1"}}]},
        }
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            result = store.execute_sparql("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
        _, kw = mp.call_args
        self.assertEqual(kw["headers"], {"Accept": "application/sparql-results+json"})
        self.assertNotIn("Content-Type", kw["headers"])
        self.assertEqual(result, {
            "success": True,
            "bindings": mock_resp.json.return_value["results"]["bindings"],
            "variables": ["s", "p", "o"],
            "metadata": {"query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o }",
                         "endpoint": store._get_sparql_endpoint()},
        })
        self.assertNotIn("triples", result)

    def test_select_does_not_send_turtle_accept(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"head": {"vars": []}, "results": {"bindings": []}}
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.execute_sparql("SELECT ?s WHERE { ?s ?p ?o }")
        _, kw = mp.call_args
        self.assertNotEqual(kw["headers"].get("Accept"), "text/turtle")

    def test_ask_uses_json_not_turtle_path(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"head": {}, "boolean": True}
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.execute_sparql("ASK { ?s ?p ?o }")
        _, kw = mp.call_args
        self.assertEqual(kw["headers"].get("Accept"), "application/sparql-results+json")

    def test_non_construct_result_has_no_triples_key(self):
        store = _make_connected_store()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"head": {"vars": []}, "results": {"bindings": []}}
        mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post", return_value=mock_resp):
            result = store.execute_sparql("SELECT ?s WHERE { ?s ?p ?o }")
        self.assertNotIn("triples", result)


class TestRDF4JStoreAddTripletsContextParameter(unittest.TestCase):
    def _t(self):
        return Triplet(subject="http://ex.org/s1", predicate="http://ex.org/p", object="http://ex.org/o1")

    def test_graph_present_sends_context_param(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()], graph="http://ex.org/mygraph")
        _, kw = mp.call_args
        self.assertIsNotNone(kw.get("params"))
        self.assertIn("context", kw["params"])

    def test_graph_present_encodes_as_angle_bracket_wrapped_iri(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()], graph="http://ex.org/mygraph")
        _, kw = mp.call_args
        self.assertEqual(kw["params"]["context"], "<http://ex.org/mygraph>")
        self.assertNotEqual(kw["params"]["context"], "http://ex.org/mygraph")

    def test_graph_none_sends_no_context_param(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()], graph=None)
        _, kw = mp.call_args
        self.assertIsNone(kw.get("params"))

    def test_graph_omitted_sends_no_context_param(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()])
        _, kw = mp.call_args
        self.assertIsNone(kw.get("params"))

    def test_graph_none_does_not_send_context_null(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()], graph=None)
        _, kw = mp.call_args
        params = kw.get("params")
        if params is not None:
            self.assertNotIn("context", params)

    def test_context_encoding_matches_confirmed_rdf4j_protocol(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        graph_uri = "http://ex.org/mygraph"
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()], graph=graph_uri)
        _, kw = mp.call_args
        ctx = kw["params"]["context"]
        self.assertEqual(ctx, f"<{graph_uri}>")
        self.assertTrue(ctx.startswith("<"))
        self.assertTrue(ctx.endswith(">"))

    def test_graph_present_posts_to_statements_endpoint_not_modified_url(self):
        store = _make_connected_store()
        mock_resp = MagicMock(); mock_resp.raise_for_status = MagicMock()
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp) as mp:
            store.add_triplets([self._t()], graph="http://ex.org/g")
        call_url = mp.call_args[0][0]
        self.assertEqual(call_url, store._get_update_endpoint())
        self.assertNotIn("context", call_url)


class TestExecuteConstructTemplateWithRDF4JBackend(unittest.TestCase):

    def test_end_to_end_with_rdf4j_backend(self):
        from semantica.triplet_store.construct_templates import (
            ConstructTemplate, ParameterDescriptor, execute_construct_template,
        )
        fixture = b'@prefix ex: <http://ex.org/> .\nex:s1 ex:p1 "Alice" .\n'
        mock_resp = MagicMock()
        mock_resp.content = fixture
        mock_resp.raise_for_status = MagicMock()
        store = _make_connected_store()
        calls = []
        store.add_triplets = (
            lambda triplets, **opts:
            (calls.append((triplets, opts)) or None) or {"success": True}
        )
        template = ConstructTemplate(
            name="rdf4j_e2e",
            description="e2e test",
            construct_query=(
                "CONSTRUCT { <http://ex.org/s1> <http://ex.org/p1> {{value}} } "
                "WHERE { <http://ex.org/s1> <http://ex.org/p1> {{value}} }"
            ),
            parameters=[ParameterDescriptor(name="value", type="literal", required=True)],
            target_graph="http://ex.org/rdf4j_graph",
        )
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp):
            result = execute_construct_template(
                template, params={"value": "Alice"}, store_backend=store)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(calls), 1)
        _, opts = calls[0]
        self.assertEqual(opts.get("graph"), "http://ex.org/rdf4j_graph")

    def test_literal_metadata_round_trips_through_rdf4j_backend(self):
        from semantica.triplet_store.construct_templates import (
            ConstructTemplate, ParameterDescriptor, execute_construct_template,
        )
        fixture = (
            b'@prefix ex: <http://ex.org/> .\n'
            b'@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n'
            b'ex:s1 ex:p_age 42 .\n'
            b'ex:s2 ex:p_label "hello"@en .\n'
        )
        mock_resp = MagicMock()
        mock_resp.content = fixture
        mock_resp.raise_for_status = MagicMock()
        store = _make_connected_store()
        store.add_triplets = lambda triplets, **opts: {"success": True}
        template = ConstructTemplate(
            name="rdf4j_roundtrip",
            description="round-trip test",
            construct_query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
            parameters=[ParameterDescriptor(name="value", type="literal", required=True)],
        )
        with patch("semantica.triplet_store.rdf4j_store.requests.post",
                   return_value=mock_resp):
            result = execute_construct_template(
                template, params={"value": "x"}, store_backend=store)
        by_subject = {t.subject: t for t in result}
        age_t = by_subject["http://ex.org/s1"]
        self.assertEqual(age_t.object, "42")
        self.assertEqual(age_t.metadata.get("datatype"),
                         "http://www.w3.org/2001/XMLSchema#integer")
        label_t = by_subject["http://ex.org/s2"]
        self.assertEqual(label_t.object, "hello")
        self.assertEqual(label_t.metadata.get("lang"), "en")


if __name__ == "__main__":
    unittest.main()
