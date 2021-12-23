import sys
import datetime
import numpy as np
import pandas as pd
from numpy import savetxt

## Hamming distance formula
# https://stackoverflow.com/questions/48799955/find-the-hamming-distance-between-two-dna-strings
def distance(str1, str2):
    if len(str1) != len(str2):
        raise ValueError("Strand lengths are not equal!")
    else:
        return sum(1 for (a, b) in zip(str1, str2) if a != b)

#### Below code is to time how long the entire script takes to run
# https://kite.com/python/answers/how-to-determine-the-execution-time-of-a-script-in-python#:~:text=to%20finish%20running.-,Use%20timeit.,string%20being%20run%20number%20times.
begin_time = datetime.datetime.now()


#### The below section will parse an alignment reported in .fasta format and put each entry into its own list
name_list = []
sequence_list = []

query_file = sys.argv[1] ##eg. "Bat_ACE2_aligned.fasta"

line_counter = 0
with open(query_file, 'r') as datafile:
    for line in datafile:
        line_counter += 1
#print(line_counter)

temp_sequence_variable = ""
header_identifier = 1
line_counter2 = 0
with open(query_file, 'r') as datafile:
    for line in datafile:
        if line[0] != ">":
            temp_sequence_variable = temp_sequence_variable + line.strip()
        if line[0] == ">":
            name_list.append(line.strip())
            if line_counter2 != 0:
                sequence_list.append(temp_sequence_variable)
                temp_sequence_variable = ""
        line_counter2 += 1
        if line_counter2 == line_counter:
            sequence_list.append(temp_sequence_variable)

if len(name_list) == len(sequence_list):
    print(str(len(name_list)) + " entries successfully imported")
            
#### Now that all of the entries are there, calculate the distance matrices of the identities between each pair of "words"
# https://stackoverflow.com/questions/37428973/string-distance-matrix-in-python
List1 = sequence_list
List2 = sequence_list
Matrix = np.zeros((len(List1),len(List2)),dtype=np.int)
for i in range(0,len(List1)):
  for j in range(0,len(List2)):
      #print(List1[i])
      #print(List2[j])
      print(str(i) + " x " + str(j))
      Matrix[i,j] = distance(List1[i],List2[j])
#print(Matrix)
# https://machinelearningmastery.com/how-to-save-a-numpy-array-to-file-for-machine-learning/#:~:text=You%20can%20save%20your%20NumPy,file%2C%20most%20commonly%20a%20comma.
savetxt(query_file[:-6] + "_identity_matrix.csv", Matrix, delimiter=',')

## Also write a tsv file that lists the sequence names and sequence
with open(query_file[:-6] + "_identity_matrix_items.tsv", 'w') as f:
    for x in range(0,len(name_list)):
        f.write("{}\t{}\n".format(name_list[x][1:], sequence_list[x]))


print(datetime.datetime.now() - begin_time)
