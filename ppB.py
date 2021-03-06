import sys
from pyms.GCMS.IO.ANDI.Function import ANDI_reader
from pyms.GCMS.Function import build_intensity_matrix
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.Baseline.TopHat import tophat
from pyms.Deconvolution.BillerBiemann.Function import BillerBiemann, rel_threshold, num_ions_threshold
from pyms.Peak.Class import Peak
from pyms.Peak.Function import peak_sum_area
from pyms.Experiment.Class import Experiment
from pyms.Experiment.IO import store_expr
import itertools
import fnmatch
import os
from pyms.Noise.Analysis import window_analyzer
import csv
import argparse

import re

from datetime import datetime



def glob(glob_pattern, directoryname, splitPattern):
    '''
    Walks through a directory and its subdirectories looking for files matching
    the glob_pattern and returns a list.

    :param directoryname: Any accessible folder name on the filesystem.
    :param glob_pattern: A string like "*.txt", which would find all text files.
    :return: A list of absolute filepaths matching the glob pattern.
    '''
    matches = []
    names = []
    for root, dirnames, filenames in os.walk(directoryname):
        for filename in fnmatch.filter(filenames, glob_pattern):
            absolute_filepath = os.path.join(root, filename)
            matches.append(absolute_filepath)

            name = filename.rsplit(splitPattern)[-1]
            names.append(name)

    print('n1', names)
    return matches, names


def matrix_from_cdf(cdffile, name):
    '''
    Intakes a .cdf file and produces an intensity matrix and a noise level .
    The noise level info is obtained by producing a tic and using the window_analyzer
    method to extract a noise approximation.

    @param cdffile: Absolutepath to a .cdf file to be processed
    @param name: file name associated with .cdf file
    @return: An intensity matrix and a corresponding noise level value
    '''
    data = ANDI_reader(cdffile)
    print(name)
    data.info()
    tic = data.get_tic()
    noise_lvl = window_analyzer(tic)
    print('nz=', noise_lvl)

    return build_intensity_matrix(data), noise_lvl


def Preprocess_IntensityMatrixes(matrixes):
    '''
    noise removal and baseline correction of Intensity Matricies
    input matrix list, outputs corrected/"cleansed" matrix list

    @param matrixes: List of matrixes generated by the matrix_from_cdf method
    @return: List of matrixes that have been 'cleansed'
    '''

    count = 1
    for im in matrixes:

        n_s, n_mz = im.get_size()
        count += 1

        for ii in range(n_mz):
            # print("Working on IC#", ii+1, " Unit", count)
            ic = im.get_ic_at_index(ii)
            ic_smoof = savitzky_golay(ic)
            ic_bc = tophat(ic_smoof, struct='1.5m')
            im.set_ic_at_index(ii, ic_bc)

    # print(matrixes)
    return (matrixes)  # save to file


def Peak_detector(pp_im, noise, name, points, scans, percent, ni, name_tag, sdir):
    # Peak detection and filtering and selection
    peakz = []
    # counter = 1
    savePath = sdir
    ms_data_files = []

    print("len pp_im", len(list(pp_im)))
    print("len noise", len(noise))
    print("len name", len(name), name)

    for im, n, na in itertools.izip(list(pp_im), noise, name):

        ms_data = []

        # print(na)
        poss_peaks = BillerBiemann(im, points=points, scans=scans)  # increase scan #
        pi = rel_threshold(poss_peaks, percent=percent)
        nin = num_ions_threshold(pi, n=ni, cutoff=n)

        completeName = os.path.join(savePath, na + name_tag + "ms_data.csv")
        with open(completeName, 'w') as f:
            w = csv.writer(f)
            # head = [35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0, 80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0, 126.0, 127.0, 128.0, 129.0, 130.0, 131.0, 132.0, 133.0, 134.0, 135.0, 136.0, 137.0, 138.0, 139.0, 140.0, 141.0, 142.0, 143.0, 144.0, 145.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0, 162.0, 163.0, 164.0, 165.0, 166.0, 167.0, 168.0, 169.0, 170.0, 171.0, 172.0, 173.0, 174.0, 175.0, 176.0, 177.0, 178.0, 179.0, 180.0, 181.0, 182.0, 183.0, 184.0, 185.0, 186.0, 187.0, 188.0, 189.0, 190.0, 191.0, 192.0, 193.0, 194.0, 195.0, 196.0, 197.0, 198.0, 199.0, 200.0, 201.0, 202.0, 203.0, 204.0, 205.0, 206.0, 207.0, 208.0, 209.0, 210.0, 211.0, 212.0, 213.0, 214.0, 215.0, 216.0, 217.0, 218.0, 219.0, 220.0]
            head = ['Area', 'RTs', 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0,
                    49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0,
                    65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0, 80.0,
                    81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0,
                    97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0,
                    111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0,
                    125.0, 126.0, 127.0, 128.0, 129.0, 130.0, 131.0, 132.0, 133.0, 134.0, 135.0, 136.0, 137.0, 138.0,
                    139.0, 140.0, 141.0, 142.0, 143.0, 144.0, 145.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0,
                    153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0, 162.0, 163.0, 164.0, 165.0, 166.0,
                    167.0, 168.0, 169.0, 170.0, 171.0, 172.0, 173.0, 174.0, 175.0, 176.0, 177.0, 178.0, 179.0, 180.0,
                    181.0, 182.0, 183.0, 184.0, 185.0, 186.0, 187.0, 188.0, 189.0, 190.0, 191.0, 192.0, 193.0, 194.0,
                    195.0, 196.0, 197.0, 198.0, 199.0, 200.0, 201.0, 202.0, 203.0, 204.0, 205.0, 206.0, 207.0, 208.0,
                    209.0, 210.0, 211.0, 212.0, 213.0, 214.0, 215.0, 216.0, 217.0, 218.0, 219.0, 220.0]

            w.writerow(head)
            for peak in nin:

                area = peak_sum_area(im, peak)
                # print('area:', area)
                peak.set_area(area)
                ms = peak.get_mass_spectrum()
                # print("Peaks rt: ", peak.get_rt())
                # print("Peaks ms_list: ", ms.mass_list)
                # print("Peaks ms_spec: ", list(ms.mass_spec))
                p_rt = peak.get_rt()
                its = []
                items = list(ms.mass_spec)
                for i in items:
                    x = float(i)
                    its.append(x)

                ms_d = ([area] + [p_rt] + its)
                # ms_d = its
                # print('ms_d', ms_d)
                w.writerow(ms_d)

            f.close()

        peakz.append(nin)
        # #print("...", counter)
        # counter += 1
        ms_data_files.append(completeName)
    print('ms_data_files:', ms_data_files)

    return [peakz, ms_data_files]


def MS_process(file_list):
    '''
    @param file_list:
    @return:
    '''

    ratio_set = []
    print(file_list)

    for n in file_list:
        peaks = []
        areas = []
        print('n=', n)
        print("-------------11------------------------------------")
        with open(n, 'r') as f:
            next(f)
            for line in f:
                sline = line.split(',')
                a = sline[0]
                p = sline[1]
                # p2 = sline[2]
                # p3 = sline[3]
                # print('sline=', sline)
                # print('are2a=', a)
                # print('peak rt2=', p)

                sline.pop(0)
                sline.pop(0)
                peaks.append(p)
                areas.append(a)

                ratios = []
                maxi = max(map(float, sline))
                # print('maxi=', maxi)
                # loc = sline.index(str(maxi))

                c = 34.0
                for i in sline:
                    r = float(i) / float(maxi)
                    rx = int(r * 999)
                    ratios.append([c, rx])
                    c += 1

                ratio_set.append(ratios)
            # print('peaks=', peaks)
            # print('areas=', areas)

            print("----------22--------------------------------------")
            name1 = n.rsplit('ms_data.csv')
            name2 = name1[0] + '.txt'
            print('n2=', name2)
            # ms_name = os.path.join()
            # print('ms', name1)

            pp = open(name2, "w+")
            for ratios, p, a in zip(ratio_set, peaks, areas):
                # print('ratios=', ratios)
                rs = sorted(ratios, key=lambda t: t[1], reverse=True)[:10]

                # print('rs=', rs)
                ll = 'Name:', p, 'Area-', a
                ll = str(ll).replace("'", "").replace(",", "").replace("(", "").replace(")", "")
                # print('ll=', ll)
                pp.write(ll + "\n")

                nn = 'Num Peaks:', 10
                nn = str(nn).replace("'", "").replace(",", "").replace("(", "").replace(")", "")
                # print('nn=', nn)
                pp.write(nn + "\n")
                for i in rs:
                    ss = str(i).replace('[', '').replace(']', '').replace(',', '')
                    # print('ss=', ss)
                    pp.write(ss + "\n")
                # print('\n')
                pp.write("\n")
            pp.close()

            # nameFil = name1[0] + '.FIL'
            # ff = open(nameFil, "w+")
            # nameMSD = "C:\mymsds\data\be-31a1.MSD"
            # # ff.write(name2 + " OVERWRITE")
            # ff.write(name2 + " APPEND")
            #
            # ff.close()


def Experiment_store(names, peakz, name_tag, sdir2):
    for n, p in itertools.izip(names, peakz):
        expr = Experiment(n, p)
        expr.sele_rt_range(["1m", "50m"])
        store_expr(sdir2 + n + name_tag + ".expr", expr)
        print(n, "checked")


def main():
    parser = argparse.ArgumentParser(description="Preprocessing & Peak detection tool for GC-MS data")

    parser.add_argument("-f",
                        "--CDFs",
                        action="store",
                        dest="dirc",
                        nargs="?",
                        type=str,
                        default="tmp/",
                        help="CDF Directory: Location of .cdf files to be processed \n")

    parser.add_argument("-n",
                        "--name",
                        action="store",
                        nargs="?",
                        type=str,
                        #default="",
                        help="Name Split: Where to split .cdf file name \n",
                        dest="name"
                        )

    parser.add_argument("-p",
                        "--points",
                        action="store",
                        nargs="?",
                        # action='store_const',
                        const=1,
                        type=int,
                        default=140,
                        help="Points: Number of points used to determine window size \n",
                        dest="points",
                        )

    parser.add_argument("-s",
                        "--scans",
                        action="store",
                        dest="scans",
                        nargs="?",
                        const=1,
                        type=int,
                        default=25,
                        help="Scans: Number of scans to average for \n")

    parser.add_argument("-t",
                        "--threshold",
                        action="store",
                        dest="threshold",
                        nargs="?",
                        const=1,
                        type=int,
                        default=3,
                        help="Threshold percent: Minimum threshold percentage to be considered a peak \n")

    parser.add_argument("-i",
                        "--ion",
                        action="store",
                        dest="ion",
                        nargs="?",
                        const=1,
                        type=int,
                        default=3,
                        help="Number of Ions: Minimum number of Ions required for peak consideration \n")

    parser.add_argument("-c",
                        "--CSVdir",
                        action="store",
                        dest="sdir",
                        nargs="?",
                        type=str,
                        help="CSV Directory: Location to save MS extraction .csv files \n")

    parser.add_argument("-e",
                        "--EXPRdir",
                        action="store",
                        dest="sdir2",
                        help="EXPR Directory: Location to save the .expr files for alignment scripts \n")
    args = parser.parse_args()

    dirc = args.dirc
    sp = args.name
    points = args.points
    scans = args.scans
    percent = args.threshold
    nin = args.ion
    sdir = args.sdir
    sdir2 = args.sdir2
    print(args)



    name_tag = str('p' + str(points) + 's' + str(scans) + '%' + str(percent) + 'n' + str(nin))

    print("CDF file directory:", dirc)
    print("split:", sp)
    print("Points:", points)
    print("Scans:", scans)
    print("Percent:", percent)
    print("num. of ions:", nin)
    print("Name_tag:", name_tag)
    print("Storage directory (csv):", sdir)
    print("Storage dir (expr):", sdir2)

    matrixes = []
    noise = []

    startTime = datetime.now()

    # Glob command used to locate .cdf files and create a list of the files
    list_of_cdffiles, names = glob(glob_pattern='*.cdf', directoryname=dirc, splitPattern=sp)

    for cdffile, name in itertools.izip(list_of_cdffiles, names):
        print('name=', name)
        # names.append(name)
        m_c = matrix_from_cdf(cdffile, name)
        matrixes.append(m_c[0])
        noise.append(m_c[1])

    print('names=', names)

    pp_im = Preprocess_IntensityMatrixes(matrixes)
    # for i, n in itertools.izip(pp_im, noise):
    #     print(i, n)
    peak_m = Peak_detector(pp_im, noise, names, points, scans, percent, nin, name_tag, sdir)
    Experiment_store(names, peak_m[0], name_tag, sdir2)

    print('p1=', peak_m[1])
    MS_process(peak_m[1])

    print("runtime=", (datetime.now() - startTime))

    # print(dirc, points)


if __name__ == "__main__":
    main()
