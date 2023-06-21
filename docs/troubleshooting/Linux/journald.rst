:orphan:

.. image:: ../../images/cropped-plus3it-logo-cmyk.png
  :width: 140px
  :alt: Powered by Plus3 IT Systems
  :align: right
  :target: https://www.plus3it.com

==============
Using Journald
==============

Each of the relevant, boot-initiated processes may be viewed with the ``journalctl`` utility. This utility can provide wholly-unfiltered output as well as allowing the operator to drill-down into more-specific logged data.

----------------------
View *All* Logged Data
----------------------

The most basic method for viewing data stored in ``journald`` is to simply execute ``journalctl`` with no arguments. This will display a paginated-view of all logged data. This paginated view has the side-effect of truncating the logged-output to the terminal's width. To avoid pagination/truncation and, instead, see line-wrapped lines, it will be necessary to add the ``--no-pager`` flag. Since this defeats pagination, it will typically also be desirable to pipe the whole output-stream through a tool like ``more`` or ``less`` (if using ``less``, include the flag ``-r`` to preserve ANSI formatting-code interpretation). 

To sum up, use: ``journalctl --no-pager | less -r``

------------------------------------
View all data logged since last boot
------------------------------------

If using an AMI or VM-template such as those created with `spel <https://github.com/plus3it/spel>`_, the journald service will have been configured for persistent-logging. As such, the above ``journalctl``  information will display log-information for every system-epoch. To restrict the view to *only* the most recent boot, add the flag/option, ``-b 0``. Similarly, to view only the logged data from before the current boot-epoch, add the flag/option, ``-b 1``.

To sum up, use ``journalctl -b 0 --no-pager | less -r``

----------------------------------
Viewing *Only* `cloud-init` Output
----------------------------------

The ``journalctl`` utility allows you to filter output via a number of means. One of those methods is via systemd service-unit name. Since ``cloud-init``  is a systemd service-unit, the ``journald`` output may be restricted to *only* things logged through *that* service. To do so, execute ``journalctl -u cloud-init``

------------------------------
Viewing userData script-output
------------------------------

Applying a filter to show only userData script-output requires a couple of things:

1. Having enabled userData script(s) to emit logging information (e.g., through the ``logger`` utility)
2. Knowing what name the logging-enabled userData script(s) has been configured to report under

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Configuring userData Script(s) for Log-Capture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Absent explicit setup, userData scripts won't have been configured to emit logging-information in a way that the `journald` service will have captured. A simple wat to set up such logging is to add a line similar to:

.. code-block:: bash

  exec 1> >( logger -s -t "$(  basename "${0}" )" ) 2>&1


Near the top of the target userData script. This ensures that all STDOUT and STDERR content is sent to `journald` via the `logger` utility. The above is a BASH-ism. This won't work for POSIX-mode scripts and scripts using other interpreters will typically require their own syntax.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Filtering for Logging-Enabled userData Script(s) Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If using the above, ``logger``-based method, output may be filtered either via the service-name, the logged-events' ``COMM``-attribute or the userData script's name (``journalctl SYSLOG_IDENTIFIER=<SCRIPT_SHORT_NAME>``):

- Using service-name: In this case, the service-name is ``cloud-final.service``. This means, one would use ``journalctl -u cloud-final``
- Using the logged-event's program-name: This is done using the ``_COMM`` flag. For a ``logger-enabled`` script, the name to filter on would be ``logger``. This means one would use ``journalctl _COMM=logger``
- Using the userData script's name by using ``journalctl SYSLOG_IDENTIFIER=<SCRIPT_SHORT_NAME>``. Depending on how the userData script-payload had been declared, this will either be ``part-001`` or a specifically-requested script-name. To specifically request a name for the userData script(s), it will be necessary to have either declared a logging name other than ``"$(  basename "${0}" )"`` or to have encapsulated the script in a MIME-stream like:

    .. code-block:: bash
    
      --===============BOUNDARY==
      Content-Disposition: attachment; filename="userData-script.sh"
      Content-Transfer-Encoding: 7bit
      Content-Type: text/x-shellscript
      Mime-Version: 1.0
      
      #!/bin/bash
      set -x
      #
      # UserData script
      #################################################################
      
      # Log everything below into syslog
      exec 1> >( logger -s -t "$(  basename "${0}" )" ) 2>&1
      
      <ACTION_1>
      <ACTION_2>
      ...
      <ACTION_N>
    
  The ``SCRIPT_SHORT_NAME`` value will be the same as the value of the "``attachment``'s" ``filename`` argument (in the above case, ``userData-script.sh``).
