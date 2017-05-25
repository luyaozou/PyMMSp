#! encoding = utf-8

''' LWA file parser '''

import re
import numpy as np

def _file_filter(file_list, pattern):
    ''' Filter out file names with a given pattern '''
    extract = []
    prog = re.compile(pattern)
    for file_name in file_list:
        if prog.search(file_name):
            extract.append(file_name)

    return extract


def _flatten(nested_list):
    ''' flatten nested list '''
    flat = []
    for x in nested_list:
         if isinstance(x, list):
             for x2 in flatten(x):
                flat.append(x2)
         else:
             flat.append(x)

    return flat


def scan_header(filename):
    ''' Scan headers in the lwa file.
    Returns
        entry_settings: list of entry setting tuples. Scan # starts at 1.
        hd_line_num: start line number of each header in the file
    '''

    if filename:
        re_header = re.compile('DATE')
        # header's line number list
        hd_line_num = []
        # entry setting list
        entry_settings = []

        # open file
        a_file = open(filename, 'r')
        a_line = a_file.readline()
        line_num = 1
        scan_num = 0
        while a_line:       # not EOF
            # this is the header
            if re_header.match(a_line):
                scan_num += 1
                hd_line_num.append(line_num)
                _temp_list = a_line.split()
                date = _temp_list[1]
                time = _temp_list[3]
                it = float(_temp_list[7])
                sens = float(_temp_list[9])
                tc = float(_temp_list[11])
                mf = float(_temp_list[13])
                ma = float(_temp_list[15])

                # the following fields are newly introduced in PySpec
                # make it compatible with old "standard" JPL LWA header
                try:
                    mmode = _temp_list[17]
                    harm = int(_temp_list[19])
                    phase = float(_temp_list[21])
                except IndexError:
                    mmode = 'UNKNOWN'
                    harm = 0
                    phase = 0

                # move to next line to read comment
                a_line = a_file.readline()
                line_num += 1
                comment = a_line.strip()    # remove the new line char

                # move to next line to read freqs
                a_line = a_file.readline()
                line_num += 1
                _temp_list = a_line.split()
                startf = float(_temp_list[0])
                step = float(_temp_list[1])
                pts = int(_temp_list[2])
                stopf = startf + step*pts
                avg = int(_temp_list[3])

                # append settings
                entry_settings.append((scan_num, comment, date, time,
                    it, sens, tc, mmode, mf, ma, startf, stopf,
                    step, pts, avg, harm, phase))
            else:
                a_line = a_file.readline()
                line_num += 1

        a_file.close()
        hd_line_num.sort()
    else:
        entry_settings = None
        hd_line_num = None

    return entry_settings, hd_line_num


def export(id_list, hd_line_num, src='src.lwa', output='output.lwa'):
    ''' Export partial LWA file based on scan id (id starts at 0) '''

    srcfile = open(src, 'r')
    outputfile = open(output, 'w')

    # get line number window to be copied
    hd_line_num.append(0)   # add 0 for the last one
    win = lambda id, hd: list((hd[i], hd[i+1]-1) for i in id)
    line_num_win = win(id_list, hd_line_num)
    # reverse list order for pop ups
    line_num_win.reverse()

    line_num = 1
    a_line = srcfile.readline()
    start, stop = line_num_win.pop()
    # start read source file
    while a_line:   # source file not EOF
        if (line_num >= start) and ((line_num <= stop) or (stop == -1)):
            # write this line to output file
            outputfile.write(a_line)
        elif line_num > stop and stop != -1:
            # pop the next line number window
            try:
                start, stop = line_num_win.pop()
            except IndexError:
                break
        # move to next line
        a_line = srcfile.readline()
        line_num += 1

    srcfile.close()
    outputfile.close()
