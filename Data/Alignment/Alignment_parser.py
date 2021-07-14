## The purpose of this script is to parse alignments made in Clustal Omega and whittle them down to just the regions of interest

# https://biopython.org/wiki/AlignIO
# https://stackoverflow.com/questions/54095661/trim-sequences-based-on-alignment

import re
import codecs
import sys
from Bio import AlignIO

input_file = sys.argv[1]

#print(file_name_split)
aln = AlignIO.read(input_file, "clustal")
for col in range(aln.get_alignment_length()):  # search into column
    res = list(aln[:,col])
    if not '-' in res:
        position = col                         # find start point
        print('First full column is {}'.format(col))
        break
#print(aln[:,position::])
#alignment = aln[:,position::]
alignment = aln[:,position:position+600]
print(alignment.format("fasta"))


## Now write into another fasta file
#input_handle = open("example.phy", "rU")
output_handle = open(input_file[:-4]+"_Trimmed.fasta", "w")

#alignments = AlignIO.parse(input_handle, "phylip")
AlignIO.write(alignment, output_handle, "fasta")

output_handle.close()
#input_handle.close()