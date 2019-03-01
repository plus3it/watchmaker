{%- set os = grains['os'] |lower %}
{%- if os == 'redhat' %}
    {%- set os = 'rhel' %}
{%- endif %}

ash-linux:
  lookup:
    scap-profile: C2S
    scap-cpe: /root/scap/content/openscap/ssg-rhel{{ grains['osmajorrelease'] }}-cpe-dictionary.xml
    scap-xccdf: /root/scap/content/openscap/ssg-{{ os }}{{ grains['osmajorrelease'] }}-xccdf.xml
    scap-ds: /root/scap/content/openscap/ssg-{{ os }}{{ grains['osmajorrelease'] }}-ds.xml
