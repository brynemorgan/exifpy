import rdflib

# from rdflib import Graph


class XMP:

    def __init__(self, xmp_bytes : bytes):

        self.bytes = xmp_bytes
        self.str = xmp_bytes.decode("utf-8")
        # Get RDF XML
        # NOTE: This seems to work for  a few different test files, but there may
        # very well be images out there with XMP metatdata not in RDF format.
        # self.rdf_str = ''.join(self.str.splitlines()[1:-1]).strip()
        self.rdf_str = self.str

        self.graph = self._create_rdfgraph()

        self.root = self.get_root()

        self.tags = self.get_nodes_as_dict(self.graph, self.root)

    def _create_rdfgraph(self):
        return rdflib.graph.Graph().parse(data=self.rdf_str, format='xml')

    def get_root(self):
        """
        Get the root of a graph. Note that this is based on MicaSense RDF graphs, 
        and probably isn't the best way to do this.

        Returns the regular (non-blank) subjects of a graph.

        Parameters
        ----------
        graph : rdflib.graph.Graph

        Returns
        -------
        node
            Root node(s) of the graph.
        """
        nodes = self._get_unique_nodes()

        for node in nodes:
            if isinstance(node,rdflib.term.URIRef):
                return node

    def _get_unique_nodes(self):
        """
        Get the unique nodes of from the subjects of a graph.

        Parameters
        ----------
        graph : rdflib.graph.Graph

        Returns
        -------
        subs : set
        """

        subs = set([s for s in self.graph.subjects()])

        return subs

    def get_nodes_as_dict(self, graph: rdflib.graph.Graph, root: rdflib.term.URIRef):
        """
        Get the nodes for the root of an RDF graph and return as a dictionary.

        Parameters
        ----------
        graph : rdflib.graph.Graph
            RDF graph 
        root : rdflib.term.URIRef
            The root of the RDF graph for which to retrieve the nodes.

        Returns
        -------
        nodes : dict
            Contains the predicates of the root as keys and their objects as values.
        """
        nodes = {}
        # Iterate through nodes in the root
        for pred,obj in graph[root]:
            # Get the prefix of the predicate (prettier than the URL)
            key = self._get_rdf_prefix(graph, pred)[1]
            # Object
            if isinstance(obj, rdflib.term.BNode):
                # If the object is a reference to a blank node, go get that node's 
                # objects
                val = self._get_bnode_objects(graph, obj)
            # Otherwise, the object should be am rdf.term.Literal, which can be formatted.        
            # elif isinstance(obj, rdflib.term.Literal):
            else:
                val = self.format_object(obj)
            # Add node to dictionary
            nodes[key] = val

        return nodes

    def _get_rdf_prefix(self, graph : rdflib.graph.Graph, uri: rdflib.term.URIRef):
        """
        Returns the RDF prefix for a given URI reference. 

        Basically, this returns the formatted value of the URI reference, which is an
        ugly URL.

        Parameters
        ----------
        graph : rdflib.graph.Graph
            RDF Graph containing the URI reference.
        uri : rdflib.term.URIRef
            URI reference.

        Returns
        -------
        Tuple of tags corresponding to the RDF prefix. The first value is the namespace
        and the second is the tag (sub-category of the namespace). For now, we only 
        want the tags, but this allows for retrieval of the namespace for future implementation.
        """
        # Query the graph for the prefix + separate root from tag
        tags = graph.qname(uri).split(':')

        return tags[0],tags[1]



    @staticmethod
    def extract_literal(val):
        """
        Attempts to convert a variable to a float. If this fails, returns a string.

        Parameters
        ----------
        val : any, intended for use with rdflib.term.Literal
            Variable to be converted

        Returns
        -------
        float or str
            Input value as float or str.
        """
        try: 
            return float(val)
        except:
            return str(val)

    # @staticmethod
    # def format_object(obj):
    #     """
    #     Format the object of a graph. If the object is a single value, it will be
    #     converted to a float or str. If it has multiple values, it will become a 
    #     list of values.

    #     Parameters
    #     ----------
    #     obj : rdflib.term.Literal
    #         Object of an RDF graph.

    #     Returns
    #     -------
    #     new_obj : str, float, list
    #         Returns str or float if single value, otherwise a list of str and/or floats.
    #     """
        
    #     new_obj = XMP.extract_literal(obj)
    #     # Check if list
    #     if isinstance(new_obj,str) and ',' in new_obj:
    #         new_obj = [XMP.extract_literal(o) for o in new_obj.split(',')]

    #     return new_obj

    @staticmethod
    def format_object(obj):
        """
        Format the object of a graph. If the object is a single value, it will be
        converted to a float or str. If it has multiple values, it will become a 
        list of values.

        Parameters
        ----------
        obj : rdflib.term.Literal
            Object of an RDF graph.

        Returns
        -------
        new_obj : str, float, list
            Returns str or float if single value, otherwise a list of str and/or floats.
        """
        if isinstance(obj,list):
            new_obj = [XMP.extract_literal(o) for o in obj]
        else:
            new_obj = XMP.extract_literal(obj)
            # Check if list
            if isinstance(new_obj,str) and ',' in new_obj:
                new_obj = [XMP.extract_literal(o) for o in new_obj.split(',')]

        return new_obj

    def _get_bnode_objects(self, graph: rdflib.graph.Graph, bnode : rdflib.term.BNode):
        """
        Retrieve the objects from a blank node.

        Parameters
        ----------
        graph : rdflib.graph.Graph
            
        bnode : rdflib.term.BNode
            Blank node from which to retrieve the objects

        Returns
        -------
        blank_objects : list
            Contains the formatted objects of a blank node as a list.
        """
        blank_objects = [self.extract_literal(o) for o in graph.objects(bnode) if type(o) != rdflib.term.URIRef]

        return blank_objects

    def _get_blank_subjects(self, graph: rdflib.graph.Graph):
        """
        Get blank nodes that are subjects of a graph. Blank nodes have no URI or literal.

        Parameters
        ----------
        graph : rdflib.graph.Graph

        Returns
        -------
        list
            List of rdflib.term.BNode objects that are subjects in the graph.
        """

        return [s for s in graph.subjects() if isinstance(s,rdflib.term.BNode)]


    def _get_bnodes_as_dict(self, graph: rdflib.graph.Graph):
        """
        Get blank nodes of a graph as a dictionary. Blank nodes have no URI or literal.

        For MicaSense metadata, these represent structured objects corresponding to 
        predicates in the root graph.

        Parameters
        ----------
        graph : rdflib.graph.Graph

        Returns
        -------
        bnodes : dict
            Dictionary containing blank subjects from root graph (as keys) and blank
            objects from root graph (as values). Predicates are omitted for now, as 
            they are just numbers corresponding to each object.
        """
        # Get blank subjects
        blank_subjects = self._get_blank_subjects(graph)
        # Initialize empty dictionary for blank nodes
        bnodes = dict([self._get_bnode_objects(graph, bnode) for bnode in blank_subjects])

        return bnodes
