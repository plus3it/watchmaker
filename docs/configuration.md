# Configuration

Watchmaker is configured using a YAML file. To understand YAML, read up on it
[here][0].

Watchmaker comes with a default [config.yaml][1] file, which should work
out-of-the-box. You can also use it as an example to create your own
configuration file.

The configuration is a dictionary. The parent nodes (keys) are `all`, `linux`,
or `windows`. The parent nodes contain a list of workers to execute, and each
worker contains parameters specific to that worker. The `all` node is applied
to every system, and `linux` and `windows` are applied only to their respective
systems.

You can create a file using the above format with your own set of standard
values and use that file for Watchmaker. Pass the CLI parameter `--config` to
point to that file.

[0]: http://www.yaml.org/spec/1.2/spec.html
[1]: https://github.com/plus3it/watchmaker/blob/develop/src/watchmaker/static/config.yaml
