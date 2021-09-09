# UP4 System Tests

Tests in this folder use UP4 ONOS APIs (P4Runtime) to simulate the attachment
and detachment of UEs. Tests also verify upstream and downstream traffic by
checking that GTP encapsulation and decapsulation is correctly performed by the
UPF (implemented by the leaves switches). The testing topology a paired-leaves
topology.

# Requirements to run UP4 tests

The UP4 test uses the P4RuntimeCliDriver. This driver requires
the `p4runtime-shell` to be installed on the ONOS Bench machine To install it
run `python3 -m pip install p4runtime-sh==0.0.2` (requires Python>3.7).

The driver also requires an ipython config file. The file should contain the
following lines:

```
c.InteractiveShell.color_info = False
c.InteractiveShell.colors = 'NoColor'
c.TerminalInteractiveShell.color_info = False
c.TerminalInteractiveShell.colors = 'NoColor'
```

and can be placed in `<IPYTHONDIR>/profile_default/ipython_config.py`. A
different location for the ipython config folder can be set via the `IPYTHONDIR`
, in that case the `ipython_config.py` file can be placed
in `<IPYTHONDIR>/profile_default`
(more info at https://ipython.readthedocs.io/en/stable/development/config.html).


