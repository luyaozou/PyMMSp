#! encoding = utf-8

""" Unit test of synthesizer API """

import unittest
from importlib.resources import files
from time import sleep
from PyMMSp.inst.base import Handles
from PyMMSp.inst.synthesizer import DynamicSynAPI



class BaseTest(unittest.TestCase):
    api = None
    h = None

    def test_get_inst_name(self):
        stat, name = self.api.get_inst_name(self.h.h_syn)
        self.assertTrue(stat)
        self.assertIsInstance(name, str)

    def test_power_stat(self):
        test_state = True
        stat = self.api.set_power_stat(self.h.h_syn, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_power_stat(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)
        test_state = False
        stat = self.api.set_power_stat(self.h.h_syn, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_power_stat(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)

    def test_power_level(self):
        test_level = -20
        stat = self.api.set_power_level(self.h.h_syn, test_level, 'dBm')
        self.assertTrue(stat)
        stat, set_level = self.api.get_power_level(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(test_level, set_level)

    def test_cw_freq(self):
        test_freq = 1e9     # 1 GHz
        stat = self.api.set_cw_freq(self.h.h_syn, test_freq, 'Hz')
        self.assertTrue(stat)
        stat, set_freq = self.api.get_cw_freq(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(test_freq, set_freq)

        test_freq = 1e3
        stat = self.api.set_cw_freq(self.h.h_syn, test_freq, 'MHz')
        self.assertTrue(stat)
        stat, set_freq = self.api.get_cw_freq(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(test_freq, set_freq*1e6)

    def test_modu_stat(self):
        test_state = True
        stat = self.api.set_modu_stat(self.h.h_syn, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_modu_stat(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)
        test_state = False
        stat = self.api.set_modu_stat(self.h.h_syn, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_modu_stat(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)

    def test_am_stat(self):
        test_state = True
        stat = self.api.set_am_stat(self.h.h_syn, 1, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_am_stat(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)
        test_state = False
        stat = self.api.set_am_stat(self.h.h_syn, 1, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_am_stat(self.h.h_syn, 1)
        self.assertTrue(stat)

    def test_am_source(self):
        test_source = 'INT'
        stat = self.api.set_am_source(self.h.h_syn, 1, test_source)
        self.assertTrue(stat)
        stat, source = self.api.get_am_source(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(source, test_source)
        test_source = 'EXT'
        stat = self.api.set_am_source(self.h.h_syn, 1, test_source)
        self.assertTrue(stat)
        stat, source = self.api.get_am_source(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(source, test_source)

    def test_am_waveform(self):
        test_wave = 'SIN'
        stat = self.api.set_am_waveform(self.h.h_syn, 1, test_wave)
        self.assertTrue(stat)
        stat, wave = self.api.get_am_waveform(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(wave, test_wave)
        test_wave = 'SQU'
        stat = self.api.set_am_waveform(self.h.h_syn, 1, test_wave)
        self.assertTrue(stat)
        stat, wave = self.api.get_am_waveform(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(wave, test_wave)

    def test_am_freq(self):
        test_freq = 1e3
        stat = self.api.set_am_freq(self.h.h_syn, 1, test_freq, 'Hz')
        self.assertTrue(stat)
        stat, freq = self.api.get_am_freq(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(freq, test_freq)
        test_freq = 1e3
        stat = self.api.set_am_freq(self.h.h_syn, 1, test_freq, 'kHz')
        self.assertTrue(stat)
        stat, freq = self.api.get_am_freq(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(freq*1e3, test_freq)

    def test_am_depth(self):
        test_depth = 0.1
        stat = self.api.set_am_depth(self.h.h_syn, 1, test_depth)
        self.assertTrue(stat)
        stat, depth = self.api.get_am_depth(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(depth, test_depth)
        stat, depth_db = self.api.get_am_depth_db(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(depth_db, -20)

    def test_fm_stat(self):
        test_state = True
        stat = self.api.set_fm_stat(self.h.h_syn, 1, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_fm_stat(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)
        test_state = False
        stat = self.api.set_fm_stat(self.h.h_syn, 1, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_fm_stat(self.h.h_syn, 1)
        self.assertTrue(stat, test_state)

    def test_fm_freq(self):
        test_freq = 1e3
        stat = self.api.set_fm_freq(self.h.h_syn, 1, test_freq, 'Hz')
        self.assertTrue(stat)
        stat, freq = self.api.get_fm_freq(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(freq, test_freq)
        test_freq = 1e3
        stat = self.api.set_fm_freq(self.h.h_syn, 1, test_freq, 'kHz')
        self.assertTrue(stat)
        stat, freq = self.api.get_fm_freq(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(freq*1e3, test_freq)

    def test_fm_dev(self):
        test_dev = 1e3
        stat = self.api.set_fm_dev(self.h.h_syn, 1, test_dev, 'Hz')
        self.assertTrue(stat)
        stat, dev = self.api.get_fm_dev(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(dev, test_dev)
        test_dev = 1e3
        stat = self.api.set_fm_dev(self.h.h_syn, 1, test_dev, 'kHz')
        self.assertTrue(stat)
        stat, dev = self.api.get_fm_dev(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(dev*1e3, test_dev)

    def test_fm_waveform(self):
        test_wave = 'SIN'
        stat = self.api.set_fm_waveform(self.h.h_syn, 1, test_wave)
        self.assertTrue(stat)
        stat, wave = self.api.get_fm_waveform(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(wave, test_wave)
        test_wave = 'SQU'
        stat = self.api.set_fm_waveform(self.h.h_syn, 1, test_wave)
        self.assertTrue(stat)
        stat, wave = self.api.get_fm_waveform(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(wave, test_wave)

    def test_pm_stat(self):
        test_state = True
        stat = self.api.set_pm_stat(self.h.h_syn, 1, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_pm_stat(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)
        test_state = False
        stat = self.api.set_pm_stat(self.h.h_syn, 1, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_pm_stat(self.h.h_syn, 1)
        self.assertTrue(stat, test_state)

    def test_pm_freq(self):
        test_freq = 1e3
        stat = self.api.set_pm_freq(self.h.h_syn, 1, test_freq, 'Hz')
        self.assertTrue(stat)
        stat, freq = self.api.get_pm_freq(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(freq, test_freq)
        test_freq = 1e3
        stat = self.api.set_pm_freq(self.h.h_syn, 1, test_freq, 'kHz')
        self.assertTrue(stat)
        stat, freq = self.api.get_pm_freq(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(freq*1e3, test_freq)

    def test_pm_dev(self):
        test_dev = 1e3
        stat = self.api.set_pm_dev(self.h.h_syn, 1, test_dev, 'Hz')
        self.assertTrue(stat)
        stat, dev = self.api.get_pm_dev(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(dev, test_dev)
        test_dev = 1e3
        stat = self.api.set_pm_dev(self.h.h_syn, 1, test_dev, 'kHz')
        self.assertTrue(stat)
        stat, dev = self.api.get_pm_dev(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(dev*1e3, test_dev)

    def test_pm_waveform(self):
        test_wave = 'SIN'
        stat = self.api.set_pm_waveform(self.h.h_syn, 1, test_wave)
        self.assertTrue(stat)
        stat, wave = self.api.get_pm_waveform(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(wave, test_wave)
        test_wave = 'SQU'
        stat = self.api.set_pm_waveform(self.h.h_syn, 1, test_wave)
        self.assertTrue(stat)
        stat, wave = self.api.get_pm_waveform(self.h.h_syn, 1)
        self.assertTrue(stat)
        self.assertEqual(wave, test_wave)

    def test_lfo_stat(self):
        test_state = True
        stat = self.api.set_lfo_stat(self.h.h_syn, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_lfo_stat(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(state, test_state)
        test_state = False
        stat = self.api.set_lfo_stat(self.h.h_syn, test_state)
        self.assertTrue(stat)
        stat, state = self.api.get_lfo_stat(self.h.h_syn)
        self.assertTrue(stat, test_state)

    def test_lfo_source(self):
        test_source = 'INT'
        stat = self.api.set_lfo_source(self.h.h_syn, test_source)
        self.assertTrue(stat)
        stat, source = self.api.get_lfo_source(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(source, test_source)
        test_source = 'EXT'
        stat = self.api.set_lfo_source(self.h.h_syn, test_source)
        self.assertTrue(stat)
        stat, source = self.api.get_lfo_source(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(source, test_source)

    def test_lfo_ampl(self):
        test_ampl = 1
        stat = self.api.set_lfo_ampl(self.h.h_syn, test_ampl, 'V')
        self.assertTrue(stat)
        stat, ampl = self.api.get_lfo_ampl(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(ampl, test_ampl)
        test_ampl = 10
        stat = self.api.set_lfo_ampl(self.h.h_syn, test_ampl, 'mV')
        self.assertTrue(stat)
        stat, ampl = self.api.get_lfo_ampl(self.h.h_syn)
        self.assertTrue(stat)
        self.assertEqual(ampl*1e2, test_ampl)

    def test_get_err(self):
        stat, msg = self.api.get_err(self.h.h_syn)
        self.assertTrue(stat)
        self.assertIsInstance(msg, str)

    def test_get_remote_disp_stat(self):
        stat, state = self.api.get_remote_disp_stat(self.h.h_syn)
        self.assertTrue(stat)
        self.assertIsInstance(state, bool)


class TestAgilent(BaseTest):

    def setUp(self):

        self.h = Handles()
        try:
            self.h.connect('Synthesizer', 'GPIB VISA', 'GPIB0::19::INSTR', 'Agilent E8257D')
            self.api = DynamicSynAPI(files('PyMMSp.inst').joinpath('API_MAP_Agilent_E8257D.yaml'))
        except ValueError:
            self.skipTest('Agilent synthesizer not found')

    def tearDown(self):
        self.h.close_all()


class TestSimAgilent(BaseTest):

    def setUp(self):

        self.h = Handles()
        self.h.connect('Synthesizer', 'GPIB VISA', 'GPIB0::19::INSTR', 'Agilent E8257D',
                       is_sim=True)
        self.api = DynamicSynAPI(files('PyMMSp.inst').joinpath('API_MAP_Agilent_E8257D.yaml'))

    def tearDown(self):
        self.h.close_all()


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in [TestAgilent, TestSimAgilent]:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


if __name__ == '__main__':
    unittest.main()
