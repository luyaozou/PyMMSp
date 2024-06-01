#! encoding = utf-8

""" JPL LWA format handler """
import datetime
import re
import numpy as np

def _file_filter(file_list, pattern):
    """ Filter out file names with a given pattern """
    extract = []
    prog = re.compile(pattern)
    for file_name in file_list:
        if prog.search(file_name):
            extract.append(file_name)

    return extract


def _flatten(nested_list):
    """ flatten nested list """
    flat = []
    for x in nested_list:
         if isinstance(x, list):
             for x2 in flatten(x):
                flat.append(x2)
         else:
             flat.append(x)

    return flat


def scan_header(filename):
    """ Scan headers in the lwa file.
    Returns
        entry_settings: list of entry setting tuples. Scan # starts at 1.
        hd_line_num: start line number of each header in the file
    """

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

                # the following fields are newly introduced in PyMMSp
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


def export_lwa(id_list, hd_line_num, src='src.lwa', output='output.lwa'):
    """ Export partial LWA file to new LWA file,
        based on scan id (id starts at 0) """

    srcfile = open(src, 'r')
    outputfile = open(output, 'w')

    # get line number window to be copied
    hd_line_num.append(0)   # add 0 for the last one
    win = lambda id_, hd: list((hd[i], hd[i+1]-1) for i in id_)
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


def export_xy(id_list, hd_line_num, src='src.lwa', output_dir='export/'):
    """ Export partial LWA file to new xy files,
        based on scan id (id starts at 0) """

    global ylist, sens, x, out_name
    ylist = []

    # get line number window to be copied
    hd_line_num.append(0)   # add 0 for the last one
    win = lambda id_, hd: list((hd[i], hd[i+1]-1) for i in id_)
    line_num_win = win(id_list, hd_line_num)
    # reverse list order for pop ups
    line_num_win.reverse()

    line_num = 1
    srcfile = open(src, 'r')
    a_line = srcfile.readline()
    start, stop = line_num_win.pop()
    # start read source file
    while a_line:   # source file not EOF
        if (line_num >= start) and ((line_num <= stop) or (stop == -1)):
            if line_num == start: # get 1st header for sensitivity
                a_list = a_line.split()
                sens = float(a_list[9])
            elif line_num == start+1: # get comment and generate file name
                comment = a_line.split()[0]
                out_name = output_dir + '/' + 'Scan_{:d}_{:s}.csv'.format(len(line_num_win)+1, comment)
            elif line_num == start+2: # get 3rd header line for x array
                a_list = a_line.split()
                xstart = float(a_list[0])
                xstep = float(a_list[1])
                pts = int(a_list[2])
                x = np.linspace(xstart, xstart + xstep*pts, num=pts, endpoint=False)
            else:   # data lines, read data
                # add this line to y list
                ylist.append(a_line.split())
        elif line_num > stop and stop != -1:    # end of this scan entry
            # save this entry
            # column_stack array
            y = [i for j in ylist for i in j]
            np.savetxt(out_name,
                np.column_stack((x, np.asarray(y, dtype=float)*1e-4*sens)),
                delimiter=',', fmt=['%.3f', '%.6e'], comments='',
                header='Frequency(MHz),LockinInten(V)')
            # erase ylist
            ylist = []
            # pop the next line number window
            try:
                start, stop = line_num_win.pop()
            except IndexError:
                break
        # move to next line
        a_line = srcfile.readline()
        line_num += 1

    srcfile.close()

    if ylist:   # if the last one is not saved yet
        y = [i for j in ylist for i in j]
        np.savetxt(out_name,
            np.column_stack((x, np.asarray(y, dtype=float)*1e-4*sens)),
            delimiter=',', fmt=['%.3f', '%.6e'], comments='',
            header='Frequency(MHz),LockinInten(V)')
    else:
        pass


def preview(id_, hd_line_num, src='src.lwa'):
    """ Preview the scan #id.
        Returns np.array (x, y)
            x, frequency vector, unit in Hz
            y, intensity vector
    """

    srcfile = open(src, 'r')
    ylist = []

    # get line number window to be copied
    hd_line_num.append(0)   # add 0 for the last one
    line_num = 1
    start = hd_line_num[id_]
    stop = hd_line_num[id_+1] - 1

    # start reading
    a_line = srcfile.readline()
    while a_line:
        if (line_num >= start+3) and ((line_num <= stop) or (stop == -1)):
            # add this line to y list
            ylist.append(a_line.split())
        elif line_num == start: # get 1st header for sensitivity
            a_list = a_line.split()
            sens = float(a_list[9])
        elif line_num == start+2: # get 3rd header line for x array
            a_list = a_line.split()
            xstart = float(a_list[0])
            xstep = float(a_list[1])
            pts = int(a_list[2])
            x = np.linspace(xstart, xstart + xstep*pts, num=pts, endpoint=False)
            pass
        a_line = srcfile.readline()
        line_num += 1

    srcfile.close()

    # flatten ylist
    y = [i for j in ylist for i in j]

    return np.column_stack((x*1e6, np.asarray(y, dtype=float)*1e-4*sens))


def save_lwa(filename, y, h_info):
    """ Save lockin scan in the JPL .lwa format
        Arguments
            filename: str
            y: y data, np.array
            h_info: header information tuple
              (synmulti [int], itgtime [ms], sens [V], tc [sec],
               mod_freq [kHz], mod_depth/dev [%|kHz], mod_mode [str], lia_harm [int], lia_phase [float deg])
        Lwa header format:
            DATE mm-dd-year TIME hh:mm:ss SH %d IT %g SENS %g TAU %g MF %.3f MA %.3f MOD [NONE|AM|FM] HARM %d PHA %.2f
            [COMMENT]
            [START FREQ MHZ %.3f] [STEP MHZ %.6f] [PTS %d] [AVG %d] 1 1 1.887 0.000 0 0 START
    """

    d = datetime.datetime.today()
    synmulti, itgtime, sens, tc, mod_freq, mod_depth, mod_mode, lia_harm, lia_phase, start_freq, step, avg, comment = h_info
    # rescale y based on sensitivity, full scale is 1e4
    y = y / sens * 1e4

    with open(filename, 'a') as f:
        # write first line
        f.write('DATE ' + d.strftime('%m-%d-%Y'))
        f.write(' TIME ' + d.strftime('%H:%M:%S'))
        f.write(' SH {:d}'.format(synmulti))
        f.write(' IT {:.3g}'.format(itgtime))
        f.write(' SENS {:.3g}'.format(sens))
        f.write(' TAU {:.3g}'.format(tc))
        f.write(' MF {:.3f}'.format(mod_freq))
        f.write(' MA {:.3f}'.format(mod_depth))
        f.write(' MOD {:s}'.format(mod_mode))
        f.write(' HARM {:d}'.format(lia_harm))
        f.write(' PHA {:.2f}'.format(lia_phase))

        # write second line
        f.write('\n {:s}'.format(comment))

        # write third line
        f.write('\n {:.3f}   {:.6f}  {:d}'.format(start_freq, step, len(y)))
        f.write(' {:d} 1 1  1.887  0.000 0 0 START\n'.format(avg))

        # write y data
        fmt = '{:10.3f}'*10     # 10 numbers each row
        for i in range(len(y)//10):
            f.write(fmt.format(*y[i*10:(i+1)*10]))
            f.write('\n')
        # for the last row which may not have 10 numbers. Avoid index error
        for i in range(len(y) - len(y)//10*10):
            f.write('{:10.3f}'.format(y[len(y)//10*10+i]))
        f.write('\n')

    return None
