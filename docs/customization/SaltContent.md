```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```

<br>

# Salt Contents Archive File

The SallStack contents archive contains three main file-hierarchies

- `pillar`
- `states`
- `winrepo`

## The `pillar` Directory-Tree

This directry-hierarchy contains the pillar-data that is used to govern the behavior of executed SaltStack states. If modifying SaltStack states' behavior from their defaults (or supplying mandatory parameters), place the modifications under this directory-hierarchy.

## The `states` Directory-Tree

This directory-hierarchy governs _which_ Saltstack states will be executed from the available SaltStack formulae. Typically, only modification to this directory's `top.sls` is needed:

- States that are not desired for execution can be commented out or wholly removed.
- States that require conditional-execution can be placed inside of appropriate (Jinja) condition-blocks
- States that are beyond what's defined in the default `top.sls` can be added here to ensure their execution during a full run of watchmaker
- If a change in execution-order is desired, alter the list-order: listed states are executed serially in first-to-last order

## The `winrepo` Directory-Tree

&lt;TO_BE_WRITTEN&gt;
