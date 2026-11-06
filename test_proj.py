# This is provided to you so that you can test your bst.py file with a particular tracefile.

import argparse
import csv
import proj

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-tf', '--tracefile')
    args = parser.parse_args()
    tracefile = args.tracefile

    t = None
    with open(tracefile, "r") as f:
        reader = csv.reader(f)
        lines = [l for l in reader]
        for l in lines:
            if l[0] == 'initialize':
                t = proj.EKDtree(l[1],int(l[2]))
            if l[0] == 'insert_standard':
                datum = proj.Datum(proj.Point(x = int(l[1]),y = int(l[2])),l[3])
                t.insert_standard(datum)
            if l[0] == 'insert_nonstandard':
                datum = proj.Datum(proj.Point(x = int(l[1]),y = int(l[2])),l[3])
                t.insert_nonstandard(datum)
            if l[0] == 'delete':
                t.delete(proj.Point(x = int(l[1]),y = int(l[2])))
            if l[0] == 'knn_query':
                print(t.knn_query(proj.Point(x = int(l[1]),y = int(l[2])),int(l[3])))
            if l[0] == 'dump':
                t.customdump()
            if l[0] == 'plot':
                print(t.plotit())