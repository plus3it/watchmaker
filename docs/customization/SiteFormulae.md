```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Modifying List of Executed-Formulas to Meet Site-needs

The `watchmaker` utility bundles several SaltStack formulae. Which formulae are executed, in what order and under what conditions are governed by the `.../states/top.sls` file:

- On Linux systems, the value of `.../` will be `/srv/watchmaker/salt`
- On Windows systems, the value of `.../` will be `C:\Watchmaker\Salt\srv`

A typical `.../states/top.sls` will look something like:

```
{%- set environments = ['dev', 'test', 'prod', 'dx'] %}

base:
  'G@os_family:RedHat':
    - name-computer
    - scap.content
    - ash-linux.vendor
    - ash-linux.stig
    - ash-linux.iavm
    - scap.scan

  'G@os_family:Windows':
    - name-computer
    - pshelp
    - netbanner.custom
    - ash-windows.stig
    - ash-windows.iavm
    - ash-windows.delta
    - scap.scan
    - ash-windows.custom
```

Adding, removing or re-ordering entries in this list modifies which formulae watchmaker executes and in what order it executes them

## Adding "Extra" Formulae to the Execution-List

In order to add a new formula to Wachmaker's execution-list, edit the `.../states/top.sls` file. For cross-platform formulae, ensure appropriate entries exist under both the `base:G@os_family:RedHat` and `base:G@os_family:Winodws` lists. To add a formula to the execution list, insert the formula-name into the list just as the already-configured formulae are. For example, to add the [cribl-agent-formula] to the RedHat execution, modify the above RedHat stanza to look like:

```{eval-rst}
.. literalinclude:: AddFormulaToTop-Simple-RedHat.txt
   :emphasize-lines: 7
   :language: yaml
```

If there are any futher conditionals that should be placed on the formula being added, surround the target-formula's list entry with suitable, Jinja-based conditional-operators. For example, if you want to ensure that the `cribl-agent` is executed when a suitable environment-value is specified, update the preceeding example to look like:

```{eval-rst}
.. literalinclude:: AddFormulaToTop-Jinja-RedHat.txt
   :emphasize-lines: 7-9
   :language: shell
```

## Removing Formulae the Execution-List

In order to prevent a formula from being automatically run by Watchmaker, edit the `.../states/top.sls` file and either wholly remove the referenced-formula from the list or comment it out. To make the `scap-formula`'s `scan` state not run[^1], modify the example `.../states/top.sls` file to look like:

```
base:
  'G@os_family:RedHat':
    - name-computer
    - scap.content
    - ash-linux.vendor
    - ash-linux.stig
    - ash-linux.iavm
```

or:

```{eval-rst}
.. literalinclude:: RemoveFormulaFromTop-Simple-RedHat.txt
   :emphasize-lines: 7
   :language: yaml
```
[^1]: This is often done by system-owners that value launch-time provisioning-automation speed over the presence of an intial hardening-scan report on the launched-systems hard drive.
