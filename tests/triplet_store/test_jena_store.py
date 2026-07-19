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

if __name__ == "__main__":
    unittest.main()
