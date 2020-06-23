import argparse
parser = argparse.ArgumentParser()
parser.add_argument("CDFd", help="CDF Directory: Location of .cdf files to be processed \n")
parser.add_argument("NS", help="Name Split: Where to split .cdf file name \n")
parser.add_argument("P", help="Points: Number of points used to determine window size \n")
parser.add_argument("S", help="Scans: Number of scans to average for \n")
parser.add_argument("TP", help="Threshold percent: Minimum threshold percentage to be considered a peak \n")
parser.add_argument("NIN", help="Number of Ions: Minimum number of Ions required for peak consideration \n")
parser.add_argument("CSVd", help="CSV Directory: Location to save MS extraction .csv files \n")
parser.add_argument("EXPRd", help="EXPR Directory: Location to save the .expr files for alignment scripts \n")
args = parser.parse_args()
print args


