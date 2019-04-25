import csv


def import_data_from_file(fname):
    # Import a dataset from a CSV file.
    # :param fname [string] the name of the file contianing the data
    # :return [array<array<int>>] the CSV data can an aarray matrix of int values
    ret = []
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            new_row = []
            for x in row:
                new_row.append(int(x))
            ret.append(new_row)
    return ret
