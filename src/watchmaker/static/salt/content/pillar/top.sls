base:
  'G@os_family:RedHat':
    - common.ash-linux
    - common.scap.elx

  'G@os_family:Windows':
    - common.ash-windows
    - common.netbanner
    - common.scap.windows
    - common.winrepo
