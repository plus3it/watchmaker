{%- from  tpldir ~ '/map.jinja' import scap with context %}

scap:
  lookup:
    driver: scc
    output_dir: {{ scap.output_dir }}
    content:
      local_dir: {{ scap.local_dir }}
    scc:
      version: '4.2'
      guide_patterns: {{ scap.guide_patterns | yaml }}
