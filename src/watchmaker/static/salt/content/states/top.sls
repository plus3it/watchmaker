base:
  'G@os_family:RedHat':
    - name-computer
    - scap.content
    - ash-linux.vendor
    - ash-linux.stig
    - ash-linux.iavm
    # Recommend other custom states be inserted here
    - scap.scan

  'G@os_family:Windows':
    - name-computer
    - pshelp
    - emet
    - ash-windows.stig
    - ash-windows.iavm
    # Recommend other custom states be inserted here
    - ash-windows.delta
    - ash-windows.custom
