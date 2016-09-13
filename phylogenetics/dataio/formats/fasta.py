from __future__ import absolute_import

import re

# Regular expression patter for matching in fasta.
REGEX = re.compile(">.+\n[A-Z\-\n]+")

def read(data, tags=["defline"]):
    """Read a fasta string.

    Returns a list of tuple pairs. First value is header tags. Second
    value is sequence.

    Notes
    -----
    To read from file, replace the `data` arguemnt the keyword argument `fname`
    """
    # Match the pattern for fasta files
    matches = REGEX.findall(data)
    sequences = []
    for m in matches:
        index = m.find("\n")
        # pieces of sequence data.
        header = m[1:index].strip()
        header = tuple(header.split("|"))
        # Get sequence data
        sequence = m[index+1:].strip()
        sequence = sequence.replace("\n", "") # Remove any newlines in sequence
        homolog = {}
        for i in range(len(tags)):
            homolog[tags[i]] = header[i]
        # Add tuple to tuples
        homolog["sequence"] = sequence
        sequences.append(homolog)
    return sequences

def write(metadata):
    """Write a fasta string.

    Note: to write to file, replace the `data` arguemnt the keyword argument `fname`

    Parameters
    ----------
    metadata : list of dictionarys
        sequence metadata.
    """
    if type(metadata) != list:
        metadata = [metadata]
    data = ""
    for s in sequences:
        # Get the header data from tuple pair
        header = s[0]
        header_str = "|".join(header).strip()
        # Get sequence data
        sequence = s[1]
        # Add fasta string to data string
        data += ">%s\n%s\n" %(header_str, sequence)
    return data.strip()
