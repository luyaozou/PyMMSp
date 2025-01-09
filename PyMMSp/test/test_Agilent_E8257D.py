#! encoding = utf-8

""" Unit test of synthesizer API """

import unittest
from PyMMSp.inst.base import Handles


class BaseTest(unittest.TestCase):
    h = None

    def test_get_inst_name(self):
        name = self.h.api_syn.get_inst_name(self.h.h_syn)
        self.assertTrue(name, 'Agilent_E8257D')

    def test_power_stat(self):
        test_stat = True
        self.h.api_syn.set_power_stat(self.h.h_syn, test_stat)
        stat = self.h.api_syn.get_power_stat(self.h.h_syn)
        self.assertEqual(stat, test_stat)
        test_stat = False
        self.h.api_syn.set_power_stat(self.h.h_syn, test_stat)
        stat = self.h.api_syn.get_power_stat(self.h.h_syn)
        self.assertEqual(stat, test_stat)

    def test_power_level(self):
        test_level = -20
        self.h.api_syn.set_power_level(self.h.h_syn, test_level, 'dBm')
        set_level = self.h.api_syn.get_power_level(self.h.h_syn)
        self.assertEqual(test_level, set_level)

    def test_cw_freq(self):
        test_freq = 1e9     # 1 GHz
        self.h.api_syn.set_cw_freq(self.h.h_syn, test_freq, 'Hz')
        set_freq = self.h.api_syn.get_cw_freq(self.h.h_syn)
        self.assertEqual(test_freq, set_freq)

        test_freq = 1e3
        self.h.api_syn.set_cw_freq(self.h.h_syn, test_freq, 'MHz')
        set_freq = self.h.api_syn.get_cw_freq(self.h.h_syn)
        self.assertEqual(test_freq*1e6, set_freq)

    def test_modu_stat(self):
        test_stat = True
        self.h.api_syn.set_modu_stat(self.h.h_syn, test_stat)
        state = self.h.api_syn.get_modu_stat(self.h.h_syn)
        self.assertEqual(state, test_stat)
        test_stat = False
        self.h.api_syn.set_modu_stat(self.h.h_syn, test_stat)
        state = self.h.api_syn.get_modu_stat(self.h.h_syn)
        self.assertEqual(state, test_stat)

    def test_am_stat(self):
        test_stat = True
        self.h.api_syn.set_am_stat(self.h.h_syn, 1, test_stat)
        stat = self.h.api_syn.get_am_stat(self.h.h_syn, 1)
        self.assertEqual(stat, test_stat)
        test_stat = False
        self.h.api_syn.set_am_stat(self.h.h_syn, 1, test_stat)
        stat = self.h.api_syn.get_am_stat(self.h.h_syn, 1)
        self.assertEqual(stat, test_stat)

    def test_am_source(self):
        test_source = 'INT'
        self.h.api_syn.set_am_source(self.h.h_syn, 1, test_source)
        source = self.h.api_syn.get_am_source(self.h.h_syn, 1)
        self.assertEqual(source, test_source)
        test_source = 'EXT'
        self.h.api_syn.set_am_source(self.h.h_syn, 1, test_source)
        source = self.h.api_syn.get_am_source(self.h.h_syn, 1)
        self.assertEqual(source, test_source)

    def test_am_waveform(self):
        test_wave = 'SIN'
        self.h.api_syn.set_am_waveform(self.h.h_syn, 1, test_wave)
        wave = self.h.api_syn.get_am_waveform(self.h.h_syn, 1)
        self.assertEqual(wave, test_wave)
        test_wave = 'SQU'
        self.h.api_syn.set_am_waveform(self.h.h_syn, 1, test_wave)
        wave = self.h.api_syn.get_am_waveform(self.h.h_syn, 1)
        self.assertEqual(wave, test_wave)

    def test_am_freq(self):
        test_freq = 1e3
        self.h.api_syn.set_am_freq(self.h.h_syn, 1, test_freq, 'Hz')
        freq = self.h.api_syn.get_am_freq(self.h.h_syn, 1)
        self.assertEqual(freq, test_freq)
        test_freq = 1e3
        self.h.api_syn.set_am_freq(self.h.h_syn, 1, test_freq, 'kHz')
        freq = self.h.api_syn.get_am_freq(self.h.h_syn, 1)
        self.assertEqual(freq, test_freq*1e3)

    def test_am_depth(self):
        test_depth = 0.1
        self.h.api_syn.set_am_depth_pct(self.h.h_syn, 1, test_depth)
        depth = self.h.api_syn.get_am_depth_pct(self.h.h_syn, 1)
        self.assertEqual(depth, test_depth)
        depth_db = self.h.api_syn.get_am_depth_db(self.h.h_syn, 1)
        self.assertEqual(depth_db, -20)

    def test_fm_stat(self):
        test_stat = True
        self.h.api_syn.set_fm_stat(self.h.h_syn, 1, test_stat)
        stat = self.h.api_syn.get_fm_stat(self.h.h_syn, 1)
        self.assertEqual(stat, test_stat)
        test_stat = False
        self.h.api_syn.set_fm_stat(self.h.h_syn, 1, test_stat)
        stat = self.h.api_syn.get_fm_stat(self.h.h_syn, 1)
        self.assertEqual(stat, test_stat)

    def test_fm_freq(self):
        test_freq = 1e3
        self.h.api_syn.set_fm_freq(self.h.h_syn, 1, test_freq, 'Hz')
        freq = self.h.api_syn.get_fm_freq(self.h.h_syn, 1)
        self.assertEqual(freq, test_freq)
        test_freq = 1e3
        self.h.api_syn.set_fm_freq(self.h.h_syn, 1, test_freq, 'kHz')
        freq = self.h.api_syn.get_fm_freq(self.h.h_syn, 1)
        self.assertEqual(freq, test_freq*1e3)

    def test_fm_dev(self):
        test_dev = 1e3
        self.h.api_syn.set_fm_dev(self.h.h_syn, 1, test_dev, 'Hz')
        dev = self.h.api_syn.get_fm_dev(self.h.h_syn, 1)
        self.assertEqual(dev, test_dev)
        test_dev = 1e3
        self.h.api_syn.set_fm_dev(self.h.h_syn, 1, test_dev, 'kHz')
        dev = self.h.api_syn.get_fm_dev(self.h.h_syn, 1)
        self.assertEqual(dev, test_dev*1e3)

    def test_fm_waveform(self):
        test_wave = 'SIN'
        self.h.api_syn.set_fm_waveform(self.h.h_syn, 1, test_wave)
        wave = self.h.api_syn.get_fm_waveform(self.h.h_syn, 1)
        self.assertEqual(wave, test_wave)
        test_wave = 'SQU'
        self.h.api_syn.set_fm_waveform(self.h.h_syn, 1, test_wave)
        wave = self.h.api_syn.get_fm_waveform(self.h.h_syn, 1)
        self.assertEqual(wave, test_wave)

    def test_pm_stat(self):
        test_stat = True
        self.h.api_syn.set_pm_stat(self.h.h_syn, 1, test_stat)
        stat = self.h.api_syn.get_pm_stat(self.h.h_syn, 1)
        self.assertEqual(stat, test_stat)
        test_stat = False
        self.h.api_syn.set_pm_stat(self.h.h_syn, 1, test_stat)
        stat = self.h.api_syn.get_pm_stat(self.h.h_syn, 1)
        self.assertEqual(stat, test_stat)

    def test_pm_freq(self):
        test_freq = 1e3
        self.h.api_syn.set_pm_freq(self.h.h_syn, 1, test_freq, 'Hz')
        freq = self.h.api_syn.get_pm_freq(self.h.h_syn, 1)
        self.assertEqual(freq, test_freq)
        test_freq = 1e3
        self.h.api_syn.set_pm_freq(self.h.h_syn, 1, test_freq, 'kHz')
        freq = self.h.api_syn.get_pm_freq(self.h.h_syn, 1)
        self.assertEqual(freq, test_freq*1e3)

    def test_pm_dev(self):
        test_dev = 1e3
        self.h.api_syn.set_pm_dev(self.h.h_syn, 1, test_dev, 'Hz')
        dev = self.h.api_syn.get_pm_dev(self.h.h_syn, 1)
        self.assertEqual(dev, test_dev)
        test_dev = 1e3
        self.h.api_syn.set_pm_dev(self.h.h_syn, 1, test_dev, 'kHz')
        dev = self.h.api_syn.get_pm_dev(self.h.h_syn, 1)
        self.assertEqual(dev, test_dev*1e3)

    def test_pm_waveform(self):
        test_wave = 'SIN'
        self.h.api_syn.set_pm_waveform(self.h.h_syn, 1, test_wave)
        wave = self.h.api_syn.get_pm_waveform(self.h.h_syn, 1)
        self.assertEqual(wave, test_wave)
        test_wave = 'SQU'
        self.h.api_syn.set_pm_waveform(self.h.h_syn, 1, test_wave)
        wave = self.h.api_syn.get_pm_waveform(self.h.h_syn, 1)
        self.assertEqual(wave, test_wave)

    def test_lfo_stat(self):
        test_stat = True
        self.h.api_syn.set_lfo_stat(self.h.h_syn, test_stat)
        stat = self.h.api_syn.get_lfo_stat(self.h.h_syn)
        self.assertEqual(stat, test_stat)
        test_stat = False
        self.h.api_syn.set_lfo_stat(self.h.h_syn, test_stat)
        stat = self.h.api_syn.get_lfo_stat(self.h.h_syn)
        self.assertEqual(stat, test_stat)

    def test_lfo_source(self):
        test_source = 'INT'
        self.h.api_syn.set_lfo_source(self.h.h_syn, test_source)
        source = self.h.api_syn.get_lfo_source(self.h.h_syn)
        self.assertEqual(source, test_source)
        test_source = 'EXT'
        self.h.api_syn.set_lfo_source(self.h.h_syn, test_source)
        source = self.h.api_syn.get_lfo_source(self.h.h_syn)
        self.assertEqual(source, test_source)

    def test_lfo_ampl(self):
        test_ampl = 1
        self.h.api_syn.set_lfo_ampl(self.h.h_syn, test_ampl, 'VP')
        ampl = self.h.api_syn.get_lfo_ampl(self.h.h_syn)
        self.assertEqual(ampl, test_ampl)
        test_ampl = 10
        self.h.api_syn.set_lfo_ampl(self.h.h_syn, test_ampl, 'mVP')
        ampl = self.h.api_syn.get_lfo_ampl(self.h.h_syn)
        self.assertEqual(ampl, test_ampl*1e-3)

    def test_get_err(self):
        msg = self.h.api_syn.get_err(self.h.h_syn)
        self.assertIsInstance(msg, str)

    def test_get_remote_disp_stat(self):
        stat = self.h.api_syn.get_remote_disp_stat(self.h.h_syn)
        self.assertTrue(stat)


class TestReal(BaseTest):

    def setUp(self):

        self.h = Handles()
        try:
            self.h.connect('Synthesizer', 'GPIB VISA', 'GPIB0::19::INSTR', 'Agilent_E8257D')
        except ValueError:
            self.skipTest('Agilent synthesizer not found')

    def tearDown(self):
        self.h.close_all()


class TestSim(BaseTest):

    def setUp(self):

        self.h = Handles()
        self.h.connect('Synthesizer', 'GPIB VISA', 'GPIB0::19::INSTR', 'Agilent_E8257D',
                       is_sim=True)

    def tearDown(self):
        self.h.close_all()


def load_tests(loader):
    suite = unittest.TestSuite()
    for test_class in [TestReal, TestSim]:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


if __name__ == '__main__':
    unittest.main()
