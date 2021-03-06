[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/) [![Build Status](https://travis-ci.org/nest/nestml.svg?branch=master)](https://travis-ci.org/kperun/nestml)

# PyNestML - The NEST Modelling Language @Python

NestML is a domain specific language that supports the specification of neuron models
in a precise and concise syntax, based on the syntax of Python. Model equations
can either be given as a simple string of mathematical notation or as an algorithm written
in the built-in procedural language. The equations are analyzed by NESTML to compute
an exact solution if possible or use an appropriate numeric solver otherwise.

## Directory structure

`models` - Example neuron models in NestML format.

`pynestml` - The source code of PyNestML.

`tests` - A collection of tests for testing of the toolchains behavior.

`doc` - The documentation of the modeling language NestML as well as processing toolchain PyNestML.

## Installing and running NESTML

In order to execute the language tool-chain, Python in version 2 or 3 is required. A setup file is provided and can be installed by 

```
python2 setup.py install --user
```

For Python in version 3, respectively:

```
python3 setup.py install --user
```

Correct installation can be tested by 

```
python2 setup.py test
\# respectively python3 setup.py test 
```

In order to ensure correct installation and resolving of dependencies, Python's package manager [pip](https://pip.pypa.io/en/stable/installing/), the distribution tool [setuptools](https://packaging.python.org/tutorials/installing-packages/) as well as the python-dev package are required and should be installed in advance. The setup file additionally installs the following components:

* [SymPy in the version >= 1.1.1](http://www.sympy.org/en/index.html)

* [NumPy in the version >=1.8.2](http://www.numpy.org/)

* [Antlr4 runtime environment in the version >= 4.7](https://github.com/antlr/antlr4/blob/master/doc/python-target.md)

In the case that no 'enum' package is found, additionally, enum34 has to be updated by

```
pip install --upgrade pip enum34
```

All requirements are stored in the requirements.txt and can be installed in one step by pip

```
pip install -r requirements.txt
```

After the installation, the toolchain can be executed by the following command.

```
python PyNestML.py -ARGUMENTS
```

where arguments are:<a name="table_args"></a>

| Command       | Description |
|---            |---          |
| -h or --help  | Print help message.|
| -path         | Path to the source file or directory containing the model.|
| -target       | (Optional) Path to target directory where models will be generated to. Default is /target .| 
| -dry          | (Optional) Executes the analysis of the model without generating target code. Default is OFF.|
| -logging_level| (Optional) Sets the logging level, i.e., which level of messages should be printed. Default is ERROR, available are [INFO, WARNING, ERROR, NO] |
| -module_name  | (Optional) Sets the name of the module which shall be generated. Default is the name of the directory containing the models. |
| -store_log    | (Optional) Stores a log.txt containing all messages in JSON notation. Default is OFF.|
| -dev          | (Optional) Executes the toolchain in the development mode where errors in models are ignored. Default is OFF.|


Generated artifacts are copied to the selected target directory (default is /target). In order to install 
the models into NEST, the following commands have to be executed:
```
cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
make all
make install
```
where _nest\_install\_dir_ points to the installation directory of NEST (e.g. work/nest-install). Subsequently, PyNEST can be used to set up and execute a simulation.

PyNestML is also available as a component and can therefore be used from within 
other Python tools and scripts. After the PyNestML has been installed,
the following modules have to be imported:
```
from pynestml.frontend.pynestml_frontend import to_nest,install_nest
```
Subsequently, it is possible to call PyNestML from other Python tools and scripts via:

```
to_nest(path, target, dry, logging_level, module_name, store_log, dev)    
```
This operation expects the same set of arguments as in the case of the shell/CMD call,
with the following default values being used, where only the __path__ is mandatory:

| Argument | Type | Default |
|---       |---   | --- |
| path     | string | -no default- |  
| target   | string | None |
| dry      | boolean | False |
| logging_level | string | 'ERROR' |
| module_name | string | None |
| store_log | boolean | False |
| dev | boolean | False |

where no values provided indicates the same behavior as listed for default values 
in arguments [table](#table_args).
If no errors occur, the output will be generated to the specified target directory. In order 
to avoid an execution of all required module-installation routines by hand, PyNestML
features a function for an installation of NEST models directly into NEST:
```
install_nest(models_path,nest_path)
```  
where the _models\_path_ has to point as previously selected for the _target_
argument, while _nest\_path_ has to point to the directory where NEST is installed (e.g., 
"/home/nest/work/nest-install"). The second argument is hereby equivalent to the
_nest\_install\_dir_ argument from the manual installation of models (see above).
The simulation can then be started. A typical script, therefore, can look like the following:
```
from pynestml.frontend.pynestml_frontend import to_nest,install_nest

to_nest(path="/home/nest/work/pynestml/models", target="/home/nest/work/pynestml/target",dev=True)

install_nest("/home/nest/work/pynestml/target", "/home/nest/work/nest-install")

nest.install(<the module name>)    
...
nest.Simulate(400.0)
```

For an in-depth introduction to the underlying modeling language NestML, we refer to the following [introduction](doc/lan/doc.md).
For those interested in the implementation of PyNestML or the general structure of a DSL-processing toolchain, a [documentation](doc/impl/doc.md) of all implemented components is provided. 
