__doc__ = """

Module for reading and writing fasta strings.

"""

import re

# Regular expression patter for matching in fasta.
REGEX = re.compile(">.+\n[A-Z\-\n]+")

def read(data):
    """ Read a fasta string.

        Returns a list of tuple pairs. First value is header tags. Second
        value is sequence.
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

        # Add tuple to tuples
        sequences.append((header, sequence))

    # If a list isn't necessary, just give me the sequence data
    #if len(sequences) == 1:
    #    sequences = sequences[0]

    return sequences

def write(sequences):
    """ Write a fasta string.

        Arguments:
        ---------

        sequences = [
            ((tag0, tag1,...), sequence),
            ...
        ]
    """
    if type(sequences) != list:
        sequences = [sequences]

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
