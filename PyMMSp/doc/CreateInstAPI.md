# Guide for Creating Instrument API in PyMMSp

`.` represent the root directory of the PyMMSp package

## Step 1

Create a `yaml` file in the directory `./inst/` with the name `API_MAP_<instrument>.yaml`.
`<instrument>` is the name of the instrument, e.g., `Agilent_E8257D`. 
Replace any blank space with underscore '_' in the name and avoid any possible illegal characters
to avoid problems. 

Add this instrument name to the `INST_MODELS` default tuple at the start of the `./inst/<instrument>.py` file.

## Step 2
Fill the `yaml` file with the following format:

```
presets:
  <preset_name1>:
    <key1>: <index1 (integer)>
    <key2>: <index2 (integer)>
    ...
  <preset_name2>:
    ...
functions:
  - name: <api_func_name>
    args: ['<arg1>', '<arg2>', ...]
    kwargs: ['<kwarg1>', '<kwarg2>', ...]
    cmd: <command_string_to_send_to_instrument (python string formatter)>
    channel: <True/False>
    attribute: <attribute_in_Info_object>
    dtype: <data_type: str/int/float>
    unit: (optional)
      base: <unit_base>
      prefix:
        <prefix1>: <value1>
        <prefix2>: <value2>
        ...
    link_presets: <preset_name> (optional)
```

Things in the `<>` are to be replaced with the actual values.
Please make reference to the example `API_MAP_Agilent_E8257D.yaml` in the `./inst/` directory.

### Explanation of the fields

* `presets`

Presets store the mapping of string names and indices in the instrument. 
For example, a synthesizer or an oscilloscope may have a list of preset waveforms settings,
like `'sine'`, `'square'`, `'ramp'`, etc. To set them, however, one needs to input corresponding integers,
instead of the string literal. This is where the presets come in handy. 
In the example case, we define 
```
presets:
  waveform:
    sine: 1
    square: 2
    ramp: 3
```

* `functions`

Functions store the API functions that can be called to communicate with the instrument.
Each function has the following fields:

  * `name`: The name of the function. 
The name should start with either `get_`, `set_`, or other valid Python function names.
`get_` functions are value getters that request information from the instrument, 
and `set_` functions are value setters that set parameters to the instrument.
Any other function names are considered as 'actions' whose behavior is currently not defined 
and is left for future development when necessary.
  * `args`: A list of argument names that the function takes
  * `kwargs`: A list of keyword argument names that the function takes (currently not really used)
  * `cmd`: The command string to send to the instrument. 
    The command string is a python string formatter, e.g., `'{:s} {:s}'.format('FUNC', 'SIN')`
  * `channel`: A boolean value indicating whether the function is channel-specific
  * `attribute`: The attribute in the `Info` object that the function is associated with.
The `Info` object is a class that stores the information of the instrument define in
`./inst/<instrument>.py`. 
  * `dtype`: The data type of the return value. 
Note that this is the data type of the original input argument or final return value, 
not the variable passed into the string formatter.
For example, if the preset dictionary is used, the data type is `str`, 
but in the `cmd` one should expect to use integer formatter `{:d}`.
  * `unit`: The unit of the value. It can be omitted if no unit is involved. 
    The unit is a dictionary with the following fields:
      * `base`: The base unit string
      * `prefix`: A dictionary of prefixes and their corresponding values
  * `link_presets`: The preset name that is involved in the function call.
The preset name should match one of the names defined in the `presets` section.

What the API function does is that it takes the arguments and `cmd` string, 
formats the string as `cmd.format(*args)`, and then sends this string to the instrument.
If it is a getter function, it only sends the string to the instrument. 
If it is a setter function, it queries the instrument with the formatted string 
(that is to send the string and the ask for the value back).

## Step 3 (Optional)

Verify the API functions defined in the Python file `./inst/<instrument>.py`.
There is a `<Inst>API` class that defines the arbitrary API functions with type hints
to allow the IDE to provide auto-completion and type checking.
Note that the first argument should always be `handle` which is the instrument handle.
The following argument names should match the `args` and `kwargs` defined in the `yaml` file.

Even without the `<Inst>API` class, 
the API functions defined in the `.yaml` file can still function,
but IDE features will be lost because IDE cannot find the link to these dynamic functions defined
in the external file.

## Step 4

Create test classes for the instrument API in the `./test/test_<instrument>.py` directory.
Define two test classes, one for real instrument communication `TestReal_<instrument_model>` 
and the other for simulator communication `TestSim_<instrument_model>`.
Then add these test cases into the `load_tests`, in the 
`for test_class in [...]:` list.

If the test file does not exist, then one needs to write the test cases.
Test cases should cover all the API functions defined in the `yaml` file.

Run the test file to verify the API functions.
If no real instrument is connected, the real test class will be skipped.


## Step 5

Write a simulator decoder in the corresponding `./inst/<instrument>.py` file if necessary.




