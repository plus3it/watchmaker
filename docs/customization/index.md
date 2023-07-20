```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Execution Customization

This document is intended to help both the `watchmaker` user-community and `watchmaker` developers and contributors better understand how to customize the execution of the `watchmaker` configuration-utility. This will be covered in the documents linked-to from the (below) "**Common Scenarios**" section.

## Background

By default, `watchmaker` executes a standard set of configuration-tasks. The `watchmaker` utility primarily leverages [SaltStack](https://docs.saltproject.io/en/latest/topics/about_salt_project.html#about-salt) for these configuration-tasks.

The configuration-tasks, themselves, are grouped into sets of related tasks. Related tasks can be things like:

- Performing OS-hardening (e.g., applying STIGs)
- Joining a Linux or Windows host to an Active Directory domain
- Installing/configuring enterprise-mandated software (e.g., anti-virus or other security-tooling)
- etc.

These task-sets are delivered in the form of formulas. From the [vendor documentation](https://docs.saltproject.io/en/latest/topics/development/conventions/formulas.html) on formulas:

> Formulas are pre-written Salt States. They are as open-ended as Salt States themselves and can be used for tasks such as installing a package, configuring, and starting a service, setting up users or permissions, and many other common tasks.
>
> All official Salt Formulas are found as separate Git repositories in the "saltstack-formulas" organization on GitHub

The `watchmaker` project follows a similar convention. Formulae specifically authored to work under `watchmaker` can be found by visiting [Plus3 IT's GitHub](https://github.com/plus3it) and querying for the substring, "[-formula](https://github.com/plus3it/?q=-formula&type=all&language=&sort=)".

## Critical Files

Customization-activities will be governed by two, main files: the watchmaker configuration file (a.k.a.,`config.yaml`) and the Salt content archive (a.k.a., `salt-content.zip`). Discussion of the files' contents are as follows:

```{toctree}
:maxdepth: 1
ConfigYaml.md
SaltContent.md
```

## Common Scenarios

The behavior of watchmaker can be easily customized towards several ends. The most-commonly encountered are:

```{toctree}
:maxdepth: 1

SiteParameters.md
SiteFormulae.md
FormulaUpdates.md
NewFormulas.md
```

If there are other customization-scenarios that should be included in this document-set, please see the [contribution guidance](../contributing.md). The contribution document covers how to submit requests for documentation-improvements as well as guidance on how to contribute changes (like further customization documentation).
