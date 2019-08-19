__description__ = \
"""
Tools for editing sequences in phylopandas dataframes.
"""
__author__ = "Michael J. Harms (harmsm@gmail.com)"
__date__ = "2019-08-16"

import phylopandas as phy
import pandas as pd
import numpy as np

import random, string, os

def _check_uid(df,uid):
    """
    Make sure uid is in dataframe and is unique.
    """

    num_hits = np.sum(df.uid == uid)
    if num_hits == 0:
        err = "uid '{}' not in data frame.\n".format(uid)
        raise ValueError(err)
    elif num_hits > 1:
        err = "uid '{}' found multiple times in data frame.\n".format(uid)
        raise ValueError(err)
    else:
        pass


def trim_sequence(df,uid,start=0,end=None):
    """
    Trim a sequence at specified indexes.

    uid: unique phylopandas identifier for sequence.
    start: slice start
    end: slice end

    returns: copy of dataframe with trimmed sequence replacing current
             sequence
    """

    _check_uid(df,uid)

    new_df = df.copy()

    new_sequence = new_df[new_df.uid == uid].sequence.tolist()[0][start:end]
    i = new_df[new_df.uid == uid].index[0]
    new_df.at[i,"sequence"] = new_sequence

    return new_df

def split_sequence(df,uid,split_site):
    """
    Split a sequence in half, creating a new entry.  If a tree has already
    been loaded, this will create a polytomy at the new position.
    """

    _check_uid(df,uid)

    # Grab sequence to split
    sequence_to_split = df[df.uid == uid].sequence.tolist()[0]
    s1 = sequence_to_split[:split_site]
    s2 = sequence_to_split[split_site:]

    # Place to split frame
    i = np.where(df.uid == uid)[0][0]

    # Split frame
    df1 = df.iloc[:i].copy()
    df2 = df.iloc[np.array((i,i))].copy()
    df3 = df.iloc[(i+1):].copy()

    # Create new uid for new sequence
    uid_size = len(df.iloc[i].uid)
    new_uid = "".join([random.choice(string.ascii_letters)
                       for i in range(uid_size)])
    # Update entries with splits and new id
    df2 = df2.reset_index(drop=True)
    df2.at[0,"sequence"] = s1
    df2.at[1,"sequence"] = s2
    df2.at[1,"uid"] = new_uid

    # Concatenate and reindex
    new_df = pd.concat([df1,df2,df3],ignore_index=True,axis=0)
    new_df = new_df.reset_index(drop=True)

    return new_df

def to_external(out_file,df,id_col=None,out_type=None,overwrite=False):
    """
    Write a phylopandas data frame out to an external file.  If the user does
    not edit the sequence ids in the extenral file, whatever edits the user
    makes to the alignment or tree can be read back into the source data frame
    using the from_external function.

    out_file: output file.
    df: phylopandas dataframe
    id_col: id column to use as the id for each sequence
    out_type: what type of file to write.  if None, try to figure out from the
              file extension of the output file
    overwrite: overwrite an existing output file.
    """

    out_methods = {'fasta':phy.seqio.write.to_fasta,
                   'phylip':phy.seqio.write.to_phylip,
                   'clustal':phy.seqio.write.to_clustal,
                   'embl':phy.seqio.write.to_embl,
                   'nexus_seq':phy.seqio.write.to_nexus_seq,
                   'swiss':phy.seqio.write.to_swiss,
                   'fastq':phy.seqio.write.to_fastq,
                   'newick':phy.treeio.write.to_newick,
                   'nexml':phy.treeio.write.to_nexml,
                   'nexus_tree':phy.treeio.write.to_nexus_tree}

    file_extension_synonym = {"fa":"fasta",
                              "fna":"fasta",
                              "ffn":"fasta",
                              "faa":"fasta",
                              "fa":"fasta",
                              "frn":"fasta",
                              "aln":"clustal",
                              "phy":"phylip"}

    # See if the output file exists
    if os.path.isfile(out_file) and not overwrite:
        err = "out_file '{}' already exists.\n".format(out_file)
        raise FileExistsError(err)

    if out_type is None:

        out_type = out_file.split(".")[-1].lower()

        try:
            out_type = file_extension_synonym[out_type]
        except KeyError:
            pass

        try:
            out_method = out_methods[out_type]
        except KeyError:
            err = "\nCould not recognize output type from file extension.\n"
            err += "Specify type in out_type.\n"
            raise ValueError(err)

    try:
        out_method = out_methods[out_type]
    except KeyError:
        err = "\n\nout_type '{}' not recognized. Must be one of:\n"

        to_show = out_methods.keys()
        to_show.sort()
        for m in to_show:
            err += "    {}\n".format(m)

        raise ValueError(err)

    if id_col is None:
        id_col = "uid"

    df_to_write = df.copy()
    to_write_col = df[id_col]
    if id_col != "uid":
        to_write_col = ["{}_{}".format(df_to_write.uid[i],to_write_col[i])
                        for i in range(len(to_write_col))]
    df_to_write["to_write_col"] = to_write_col

    out_method(df_to_write,id_col="to_write_col",filename=out_file)


def from_external(input_file,df,input_type=None):
    """
    Read a phylopandas data frame out to an external file.  If the user wrote
    the external file out using to_external and did not edit the sequence ids
    in the extenral file, whatever edits the user made to the alignment or tree
    can be read back into the source data frame using this function.

    input_file: input file.
    df: phylopandas dataframe (or copy) used to generate the external file
    input_type: what type of file to read.  if None, try to figure out from the
                file extension of the input file
    """
    in_methods_seq = {'fasta':phy.seqio.read.read_fasta,
                      'phylip':phy.seqio.read.read_phylip,
                      'clustal':phy.seqio.read.read_clustal,
                      'embl':phy.seqio.read.read_embl,
                      'nexus_seq':phy.seqio.read.read_nexus_seq,
                      'swiss':phy.seqio.read.read_swiss,
                      'fastq':phy.seqio.read.read_fastq}

    in_methods_tree = {'newick':phy.treeio.read.read_newick,
                       'nexml':phy.treeio.read.read_nexml,
                       'nexus_tree':phy.treeio.read.read_nexus_tree}

    file_extension_synonym = {"fa":"fasta",
                              "fna":"fasta",
                              "ffn":"fasta",
                              "faa":"fasta",
                              "fa":"fasta",
                              "frn":"fasta",
                              "aln":"clustal",
                              "phy":"phylip"}

    if input_type is None:

        input_type = input_file.split(".")[-1].lower()

        try:
            input_type = file_extension_synonym[input_type]
        except KeyError:
            pass

        try:
            in_method = in_methods_seq[input_type]
        except KeyError:

            try:
                in_method = in_methods_tree[input_type]
            except KeyError:
                err = "\nCould not recognize output type from file extension.\n"
                err += "Specify type in out_type.\n"
                raise ValueError(err)

    try:
        in_method = in_methods_seq[input_type]
        input_class = "sequence"
    except KeyError:
        try:
            in_method = in_methods_tree[input_type]
            input_class = "parent"
        except KeyError:

            err = "\n\ninput_type '{}' not recognized. Must be one of:\n"

            to_show = in_methods.keys()
            to_show.sort()
            for m in to_show:
                err += "    {}\n".format(m)

            raise ValueError(err)



    new_data = in_method(input_file)
    uid = [entry.split("_")[0] for entry in new_data.id]

    new_data = pd.DataFrame({"uid":uid,
                             input_class:new_data[input_class]})

    # Drop the old information from the original frame
    to_merge = df.copy()
    to_merge = to_merge.drop(labels=[input_class],axis=1)

    # Merge sequence information back in, this time aligned.
    output = pd.merge(to_merge, new_data, on=['uid'], how='left')

    return output
