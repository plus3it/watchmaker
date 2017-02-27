# Configuration

Watchmaker is configured using a YAML file. To understand YAML, read up on it
[here][0].

Watchmaker comes with a default [config.yaml][1] file, which should work
out-of-the-box. You can also use it as an example to create your own
configuration file.

The configuration is a dictionary. The parent nodes (keys) are `All`, `Linux`,
or `Windows`. They identify parameters to use for all Operating Systems and
those specific to a particular OS. The next level identifies the workers to
use. For `Linux`, Watchmaker will use `Yum`, while `Salt` is used for both
`Linux` and `Windows`.

After the worker nodes, Watchmaker identifies all of the parameters needed for
a successful run of those workers. Each parameter in the `config.yaml` file are
also parameters that can be set at the CLI level.

You can create a file using the above format with your own set of standard
values and use that file for Watchmaker. Pass the CLI parameter `--config` to
point to that file.

[0]: http://www.yaml.org/spec/1.2/spec.html
[1]: https://github.com/plus3it/watchmaker/blob/develop/src/watchmaker/static/config.yaml
