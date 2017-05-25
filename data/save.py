#! encoding = utf-8

''' Save data '''


import numpy as np
import datetime


def save_lwa(filename, y, h_info):
    ''' Save lockin scan in the JPL .lwa format
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
    '''

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
        for i in range(len(y)//10 + 1):
            f.write(fmt.format(*y[i:i+10]))
            f.write('\n')

    return None
