# Module for input and output of HomologSet objects
from __future__ import absolute_import

from . import base
from .formats import fasta, csv, json, entrez_xml

class Write(base.Write):
    """Object for writing out the metadata of a HomologSet object.

    There are two basic output data-structures for the HomologSet.
    """
    def __init__(self, HomologSet):
        self._HomologSet = HomologSet

    def _object_to_sequences(self, tags=["id"]):
        """ Convert alignment data to sequence data type """
        sequences = []
        for h, homolog in self._HomologSet.homologs.items():
            data = homolog.get(*tags)
            sequences.append(([data[t] for t in tags], getattr(homolog, "sequence")))
        return sequences

    def _object_to_data(self, tags=[]):
        """ Write alignment data to metadata format.
        """
        data = []
        for h, homolog in self._HomologSet.homologs.items():
            data.append(homolog.get(*tags))
        return data

    @base.write_to_file
    def fasta(self, tags=["id"]):
        """ Return string in fasta format for the set."""
        sequence_data = self._object_to_sequences(tags=tags)
        output = fasta.write(sequence_data)
        return output

    @base.write_to_file
    def pickle(self):
        """ Return pickle string of homolog set. """
        return pickle.write(self._object_to_data())

    @base.write_to_file
    def json(self):
        """Return json string for HomologSet object.
        """
        return json.write(self._object_to_data())

    @base.write_to_file
    def csv(self, tags=["id"], delimiter=","):
        """ Return csv string. """
        sequence_metadata = self._object_to_data(tags=tags)
        output = csv.write(sequence_metadata, delimiter=delimiter)
        return output


class Read(base.Read):
    """Object bound to HomologSets for reading homolog set data.

    Parameters
    ----------
    HomologSet : phylogenetics.homolog.HomologSet object
        HomologSet to which the reading object will be bound.

    Examples
    --------

    """
    def __init__(self, HomologSet):
        self._HomologSet = HomologSet

    def _sequences_to_object(self, data, tags=["id"]):
        """ Add sequence_data to alignment
        """
        # Check for ids in alignment
        try:
            index = tags.index("id")
        except ValueError:
            raise Exception(""" One tag in alignment must be `id`. """)

        # Iterate through the sequence data
        for pair in data:
            attributes = pair[0]
            sequence = pair[1]

            # Get ID from attributes list.
            id = attributes[index]

            # Check that attribute list and tag list are the same length.
            if len(attributes) != len(tags):
                raise Exception(""" Number of attributes do not match number of tags given. """)

            # Update homologs that are already in the Set.
            if hasattr(self._HomologSet, id):
                # Get Homolog object
                Homolog = getattr(self._HomologSet, id)
            # otherwise, add a new Homolog object
            else:
                # Import the Homolog Object locally and construct it.
                from phylogenetics import homologs
                Homolog = homologs.Homolog(id)
                self._HomologSet.add(Homolog)

            # Add updated attributes
            for i in range(len(tags)):
                Homolog.addattr(tags[i], attributes[i])

            Homolog.addattr("sequence", sequence)

        return self._HomologSet


    def _data_to_object(self, sequence_metadata):
        """ Add sequence_metadata to alignment.
        """
        for s in sequence_metadata:
            # If an id is already present in the metadata, use that.
            if "id" in s:
                # See if that id already exists.
                try:
                    Homolog = getattr(self._HomologSet, s["id"])
                except:
                    from phylogenetics import homologs
                    Homolog = homologs.Homolog(s["id"])
                    self._HomologSet.add(Homolog)

            # Check if a sequence with same accession already exists in HomologSet,
            # If so, just update attributes with new metadata
            elif "accver" in s and s["accver"] in mapping:
                # Get the Homolog with that accession number
                # Try to get a map if HomologSet exists.
                mapping = self._HomologSet.map("accver", "id")
                Homolog = getattr(self._HomologSet, mapping[s["accver"]])

            # otherwise, add a new Homolog object
            else:
                id = "XX%08d" % int(self._HomologSet.max_id + 1)
                # Import the Homolog Object locally and construct it.
                from phylogenetics import homologs
                Homolog = homologs.Homolog(id)
                self._HomologSet.add(Homolog)

            # Iterate over attributes in s and add to homolog.
            for key, value in s.items():
                Homolog.addattr(key, value)

        return self._HomologSet

    @base.read_from_file
    def fasta(self, data, tags=["defline"]):
        """ Add sequence data from fasta to HomologSet. """
        sequences = fasta.read(data, tags)
        self._data_to_object(sequences)
        return self._HomologSet

    @base.read_from_file
    def pickle(self, data):
        """Read in HomologSet data from pickle object.
        """
        data = pickle.read(data)
        self._data_to_object(data)
        return self._HomologSet

    @base.read_from_file
    def json(self, data):
        """Read in HomologSet data from json string.
        """
        data = json.read(data)
        self._data_to_object(data)
        return self._HomologSet

    @base.read_from_file
    def csv(self, data):
        """ Add csv data to HomologSet. """
        sequence_metadata = csv.read(data)
        self._data_to_object(sequence_metadata)
        return self._HomologSet

    @base.read_from_file
    def entrez_xml(self, data):
        """ Add entrez xml output to homolog. """
        sequence_metadata = entrez_xml.read(data)
        self._data_to_object(sequence_metadata)
        return self._HomologSet
