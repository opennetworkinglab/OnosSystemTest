#!/usr/bin/env python
import time
import random

class Graph:
    """
    Graph class provides implementations of graph algorithms.
    The functions currently supported include:
    - Comparing two graphs with specified attributes for vertices and edges
    - Getting DFI (Depth First Index) and back edges during a DFS
    - Chain decomposition of a graph
    - Finding (non-)cut-edges and vertices
    """

    def __init__( self ):
        # We use a dictionary to store all information about the graph
        self.graphDict = {}
        # Depth-first index of each vertex
        self.DFI = {}
        self.currentDFI = 0
        # Parent vertex (and edge to that vertex) of each vertex in depth-first search tree
        self.parentVertexInDFS = {}
        self.parentEdgeInDFS = {}
        # Back edges of the graph generated during DFS
        self.backEdges = {}
        # All chains in chain decomposition algorithm
        self.chains = []

    def update( self, graphDict ):
        """
        Update the graph data. The current graph dictionary will be replaced by the
        new one.
        graphDict is in a dictionary which maps each vertex to a list of attributes.
        An example of graphDict:
        { vertex1: { 'edges': ..., 'name': ..., 'protocol': ... },
          vertex2: { 'edges': ..., 'name': ..., 'protocol': ... } }
        Each vertex should at least have an 'edges' attribute which describes the
        adjacency information. The value of 'edges' attribute is also represented by
        a dictionary, which maps each edge (identified by the neighbor vertex) to a
        list of attributes.
        An example of the edges dictionary:
        'edges': { vertex2: { 'port': ..., 'type': ... },
                   vertex3: { 'port': ..., 'type': ... } }
        """
        self.graphDict = graphDict
        return main.TRUE

    def compareGraphs( self, graphDictA, graphDictB, vertexAttributes=['edges'], edgeAttributes=['port'] ):
        """
        Compare two graphs.
        By default only the adjacency relationship, i.e. 'port' attribute in
        'edges' attribute for each vertex, is compared, To get other attributes
        included, attribute name needs to be specified in the args, e.g.
        vertexAttributes=[ 'edges', 'protocol' ] or
        edgeAttributes=[ 'port', 'type' ]
        Return main.TRUE if two graphs are equal, otherwise main.FALSE
        """
        try:
            result = main.TRUE
            for vertex in set( graphDictA ).difference( graphDictB ):
                result = main.FALSE
                main.log.warn( "Graph: graph B: vertex {} not found".format( vertex ) )
            for vertex in set( graphDictB ).difference( graphDictA ):
                result = main.FALSE
                main.log.warn( "Graph: graph A: vertex {} not found".format( vertex ) )
            for vertex in set( graphDictA ).intersection( graphDictB ):
                for vertexAttribute in vertexAttributes:
                    attributeFound = True
                    if vertexAttribute not in graphDictA[ vertex ]:
                        main.log.warn( "Graph: graph A -> vertex {}: attribute {} not found".format( vertex, vertexAttribute ) )
                        attributeFound = False
                    if vertexAttribute not in graphDictB[ vertex ]:
                        attributeFound = False
                        main.log.warn( "Graph: graph B -> vertex {}: attribute {} not found".format( vertex, vertexAttribute ) )
                    if not attributeFound:
                        result = main.FALSE
                        continue
                    else:
                        # Compare two attributes
                        attributeValueA = graphDictA[ vertex ][ vertexAttribute ]
                        attributeValueB = graphDictB[ vertex ][ vertexAttribute ]
                        # FIXME: the comparison may not work for (sub)attribute values that are of list type
                        # For attributes except for 'edges', we just rely on '==' for comparison
                        if not vertexAttribute == 'edges':
                            if not attributeValueA == attributeValueB:
                                result = main.FALSE
                                main.log.warn( "Graph: vertex {}: {} does not match: {} and {}".format( vertex,
                                                                                                        vertexAttribute,
                                                                                                        attributeValueA,
                                                                                                        attributeValueB ) )
                        # The structure of 'edges' is similar to that of graphs, so we use the same method for comparison
                        else:
                            edgeDictA = attributeValueA
                            edgeDictB = attributeValueB
                            for neighbor in set( edgeDictA ).difference( edgeDictB ):
                                result = main.FALSE
                                main.log.warn( "Graph: graph B -> vertex {}: neighbor {} not found".format( vertex, neighbor ) )
                            for neighbor in set( edgeDictB ).difference( edgeDictA ):
                                result = main.FALSE
                                main.log.warn( "Graph: graph A -> vertex {}: neighbor {} not found".format( vertex, neighbor ) )
                            for neighbor in set( edgeDictA ).intersection( edgeDictB ):
                                for edgeAttribute in edgeAttributes:
                                    attributeFound = True
                                    if edgeAttribute not in edgeDictA[ neighbor ]:
                                        attributeFound = False
                                        main.log.warn( "Graph: graph A -> vertex {} -> neighbor {}: attribute {} not found".format( vertex,
                                                                                                                                    neighbor,
                                                                                                                                    edgeAttribute ) )
                                    if edgeAttribute not in edgeDictB[ neighbor ]:
                                        attributeFound = False
                                        main.log.warn( "Graph: graph B -> vertex {} -> neighbor {}: attribute {} not found".format( vertex,
                                                                                                                                    neighbor,
                                                                                                                                    edgeAttribute ) )
                                    if not attributeFound:
                                        result = main.FALSE
                                        continue
                                    else:
                                        # Compare two attributes
                                        attributeValueA = edgeDictA[ neighbor ][ edgeAttribute ]
                                        attributeValueB = edgeDictB[ neighbor ][ edgeAttribute ]
                                        if not attributeValueA == attributeValueB:
                                            result = main.FALSE
                                            main.log.warn( "Graph: vertex {} -> neighbor {}: {} does not match: {} and {}".format( vertex,
                                                                                                                                   neighbor,
                                                                                                                                   edgeAttribute,
                                                                                                                                   attributeValueA,
                                                                                                                                   attributeValueB ) )
            if not result:
                main.log.debug( "Graph: graphDictA: {}".format( graphDictA ) )
                main.log.debug( "Graph: graphDictB: {}".format( graphDictB ) )
            return result
        except TypeError:
            main.log.exception( "Graph: TypeError exception found" )
            return main.ERROR
        except KeyError:
            main.log.exception( "Graph: KeyError exception found" )
            return main.ERROR
        except Exception:
            main.log.exception( "Graph: Uncaught exception" )
            return main.ERROR

    def getNonCutEdges( self ):
        """
        Get a list of non-cut-edges (non-bridges).
        The definition of a cut-edge (bridge) is: the deletion of a cut-edge will
        increase the number of connected component of a graph.
        The function is realized by impelementing Schmidt's algorithm based on
        chain decomposition.
        Returns a list of edges, e.g.
        [ [ vertex1, vertex2 ], [ vertex2, vertex3 ] ]
        """
        try:
            if not self.depthFirstSearch():
                return None
            if not self.findChains():
                return None
            nonCutEdges = []
            for chain in self.chains:
                for edge in chain:
                    nonCutEdges.append( edge )
            main.log.debug( 'Non-cut-edges: {}'.format( nonCutEdges ) )
            return nonCutEdges
        except Exception:
            main.log.exception( "Graph: Uncaught exception" )
            return None

    def getNonCutVertices( self ):
        """
        Get a list of non-cut-vertices.
        The definition of a cut-vertex is: the deletion of a cut-vertex will
        increase the number of connected component of a graph.
        The function is realized by impelementing Schmidt's algorithm based on
        chain decomposition.
        Returns a list of vertices, e.g. [ vertex1, vertex2, vertex3 ]
        """
        try:
            nonCutEdges = self.getNonCutEdges()
            # find all cycle chains
            cycleChains = []
            for chain in self.chains:
                # if the source vertex of the first chain equals to the destination vertex of the last
                # chain, the chain is a cycle chain
                if chain[ 0 ][ 0 ] == chain[ -1 ][ 1 ]:
                    cycleChains.append( chain )
            main.log.debug( 'Cycle chains: {}'.format( cycleChains ) )
            # Get a set of vertices which are the first vertices of a cycle chain (excluding the first
            # cycle chain), and these vertices are a subset of all cut-vertices
            subsetOfCutVertices = []
            if len( cycleChains ) > 1:
                for cycleChain in cycleChains[ 1: ]:
                    subsetOfCutVertices.append( cycleChain[ 0 ][ 0 ] )
            main.log.debug( 'Subset of cut vertices: {}'.format( subsetOfCutVertices ) )
            nonCutVertices = []
            assert nonCutEdges != None
            for vertex in self.graphDict.keys():
                if vertex in subsetOfCutVertices:
                    continue
                vertexIsNonCut = True
                for neighbor in self.graphDict[ vertex ][ 'edges' ].keys():
                    edge = [ vertex, neighbor ]
                    backwardEdge = [ neighbor, vertex ]
                    if not edge in nonCutEdges and not backwardEdge in nonCutEdges:
                        vertexIsNonCut = False
                        break
                if vertexIsNonCut:
                    nonCutVertices.append( vertex )
            main.log.debug( 'Non-cut-vertices: {}'.format( nonCutVertices ) )
            return nonCutVertices
        except KeyError:
            main.log.exception( "Graph: KeyError exception found" )
            return None
        except AssertionError:
            main.log.exception( "Graph: AssertionError exception found" )
            return None
        except Exception:
            main.log.exception( "Graph: Uncaught exception" )
            return None

    def depthFirstSearch( self ):
        """
        This function runs a depth-first search and gets DFI of each vertex as well
        as generates the back edges
        """
        try:
            assert self.graphDict != None and len( self.graphDict ) != 0
            for vertex in self.graphDict.keys():
                self.DFI[ vertex ] = -1
                self.parentVertexInDFS[ vertex ] = ''
                self.parentEdgeInDFS[ vertex ] = None
            firstVertex = self.graphDict.keys()[ 0 ]
            self.currentDFI = 0
            self.backEdges = {}
            if not self.depthFirstSearchRecursive( firstVertex ):
                return main.ERROR
            return main.TRUE
        except KeyError:
            main.log.exception( "Graph: KeyError exception found" )
            return main.ERROR
        except AssertionError:
            main.log.exception( "Graph: AssertionError exception found" )
            return main.ERROR
        except Exception:
            main.log.exception( "Graph: Uncaught exception" )
            return main.ERROR

    def depthFirstSearchRecursive( self, vertex ):
        """
        Recursive function for depth-first search
        """
        try:
            self.DFI[ vertex ] = self.currentDFI
            self.currentDFI += 1
            for neighbor in self.graphDict[ vertex ][ 'edges' ].keys():
                edge = [ vertex, neighbor ]
                backwardEdge = [ neighbor, vertex ]
                if neighbor == self.parentVertexInDFS[ vertex ]:
                    continue
                elif self.DFI[ neighbor ] == -1:
                    self.parentVertexInDFS[ neighbor ] = vertex
                    self.parentEdgeInDFS[ neighbor ] = backwardEdge
                    if not self.depthFirstSearchRecursive( neighbor ):
                        return main.ERROR
                else:
                    key = self.DFI[ neighbor ]
                    if key in self.backEdges.keys():
                        if not edge in self.backEdges[ key ] and\
                        not backwardEdge in self.backEdges[ key ]:
                            self.backEdges[ key ].append( backwardEdge )
                    else:
                        tempKey = self.DFI[ vertex ]
                        if tempKey in self.backEdges.keys():
                            if not edge in self.backEdges[ tempKey ] and\
                            not backwardEdge in self.backEdges[ tempKey ]:
                                self.backEdges[ key ] = [ backwardEdge ]
                        else:
                            self.backEdges[ key ] = [ backwardEdge ]
            return main.TRUE
        except KeyError:
            main.log.exception( "Graph: KeyError exception found" )
            return main.ERROR
        except Exception:
            main.log.exception( "Graph: Uncaught exception" )
            return main.ERROR

    def findChains( self ):
        """
        This function finds all the chains in chain-decomposition algorithm
        """
        keyList = self.backEdges.keys()
        keyList.sort()
        vertexIsVisited = {}
        self.chains = []
        for vertex in self.graphDict.keys():
            vertexIsVisited[ vertex ] = False
        try:
            for key in keyList:
                backEdgeList = self.backEdges[ key ]
                for edge in backEdgeList:
                    chain = []
                    currentEdge = edge
                    sourceVertex = edge[ 0 ]
                    while True:
                        currentVertex = currentEdge[ 0 ]
                        nextVertex = currentEdge[ 1 ]
                        vertexIsVisited[ currentVertex ] = True
                        chain.append( currentEdge )
                        if nextVertex == sourceVertex or vertexIsVisited[ nextVertex ] == True:
                            break
                        currentEdge = self.parentEdgeInDFS[ nextVertex ]
                    self.chains.append( chain )
            return main.TRUE
        except KeyError:
            main.log.exception( "Graph: KeyError exception found" )
            return main.ERROR
        except Exception:
            main.log.exception( "Graph: Uncaught exception" )
            return main.ERROR
