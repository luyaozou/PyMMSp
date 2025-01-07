# Guide for Creating Instrument API in PyMMSp

`.` represent the root directory of the PyMMSp package

## Step 1

Create a `yaml` file in the directory `./inst/` with the name `API_MAP_<instrument>.yaml`.
`<instrument>` is the name of the instrument, e.g., `Agilent_E8257D`. 
Replace any blank space with underscore '_' in the name.

## Step 2
Fill the `yaml` file with the following format:

```
- name: <api_func_name>
  args: []
  kwargs: []
  cmd: <command_string_to_send_to_instrument>
  channel: <True/False>
  attribute: <attribute_in_Info_object>
  dtype: <data_type: str/int/float>
  unit: (optional)
    base: <unit_base: str>
    prefix: <unit_prefix: str>
```

## Step 3
Create a test file for the instrument API


