PyMMSp is an interactive controller for millimeter-wave absorption spectrometer.
PyMMSp is developed solely in Python, and uses third-party C-wrappers for National Instrument drivers (if applicable).

The standard application scenario is to control multiplier-chain-based millimeter-wave sources and detectors,
using step-by-step frequency scan and lock-in detection. 
Additional apparatus such as pressure gauge, power supply (to apply bias voltage to the source or / and detector),
electronically controlled dosing valves, temperature controller, and so on,
can also be controlled by PyMMSp.

Requires:
* pyniscope from [Bernardo Kyotoku](https://github.com/bernardokyotoku/pyniscope "target=_blank"): provides API for National Instrument Digitizer Card. Requires National Instrument NISCOPE C library.

Documentation includes a user guide and a developer's guide.
They are in the 'doc' directory, and are written in the `MarkDown` language.
`MarkDown` syntax can be easily converted to html.
Modern text editors such Atom also provides built-in extensions to directly provide `MarkDown` preview.
For more information about `MarkDown`, see http://daringfireball.net/projects/markdown/
