# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Bug Reports

When [reporting a bug][0] please include:

*   Your operating system name and version.
*   Any details about your local setup that might be helpful in
    troubleshooting.
*   Detailed steps to reproduce the bug.

## Documentation Improvements

Watchmaker could always use more documentation, whether as part of the official
Watchmaker docs, in docstrings, or even on the web in blog posts, articles, and
such. The official documentation is maintained within this project in
docstrings or in the [docs][3] directory. Contributions are
welcome, and are made the same way as any other code. See
[Development](#development-guide) guide.

## Feature Requests and Feedback

The best way to send feedback is to [file an issue][0] on GitHub.

If you are proposing a feature:

*   Explain in detail how it would work.
*   Keep the scope as narrow as possible, to make it easier to implement.
*   Remember that this is a community-driven, open-source project, and that
    code contributions are welcome. :)

## Development Guide

To set up `watchmaker` for local development:

1.  Fork [watchmaker](https://github.com/plus3it/watchmaker) (look for the
    "Fork" button).

1.  Clone your fork locally and update the submodules:

    ```shell
    git clone https://github.com/your_name_here/watchmaker.git && cd watchmaker
    git submodule update --init --recursive
    ```

1.  Create a branch for local development:

    ```shell
    git checkout -b name-of-your-bugfix-or-feature
    ```

1.  Now you can make your changes locally.

1.  Commit your changes and push your branch to GitHub:

    ```shell
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

1.  Submit a pull request through the GitHub website.

Note: If you want to preview documentation-changes before opening a pull request,
see the guidance in the "Documentation Previewing" section.

## Pull Request Guidelines

If you need some code review or feedback while you are developing the code just
open the pull request.

For pull request acceptance, you should:

1.  Update documentation whenever making changes to the API or functionality.
1.  Add a note to `CHANGELOG.md` about the changes. Include a link to the
    pull request.

## Documentation Previewing

For those who wish to have a local preview capability for the generated HTML
content (before submitting a PR), the following can be done:

1.  Build a Docker image using the `Dockerfile` found in the `ci/local`
    directory. If using Podman for local work with Docker containers, executing:

    ```shell
    podman build -f ci/local/Dockerfile . -t doc-preview
    ```

    Will build a container with the instrumentation necessary to
    locally-generate copies of the HTML files that are normally only generated
    when the project's GitHub Actions are executed. These GitHub Actions only
    execute as part of a pull request submission.

1.  Once the build finishes, build the local copy of the documentation by
    executing:

    ```shell
    podman run \
      -v $( pwd ):/watchmaker \
      localhost/doc-preview
    ```

    From the project-root. This will result in the "preview" versions of the
    HTML files being generated under the project's `dist/docs` directory.

    Note: If your local repo-copy already has contents under the `dist`
    directory, that content may cause the document-build to fail. It's
    recommended to run `git clean -fdx` before attempting to run the container.
    This should clean out ALL untracked files in your local repository

1.  To view the documents, use a `file://` URI to reference the location of your
    local git repository's `dist/docs` directory. This may be something like:

    ```shell
    file:///home/<USER>/watchmaker/dist/docs
    ```

1.  Click on the `index.html` file. You will be presented with a navigable
    document-hierarchy that mimics what will show up on Watchmaker's official
    documentation-site after your pull request is merged.


## Build a Development Branch in EC2

To install and run a development branch of watchmaker on a new EC2 instance,
specify something like this for EC2 userdata:

*   **For Linux**: Modify `GIT_REPO` and `GIT_BRANCH` to reflect working
    values for your development build. Modify `PIP_URL` and `PYPI_URL` as
    needed.

    ```shell
    #!/bin/sh
    GIT_REPO=https://github.com/<your-github-username>/watchmaker.git
    GIT_BRANCH=<your-branch>

    PYPI_URL=https://pypi.org/simple

    # Install pip
    python3 -m ensurepip

    # Install git
    dnf -y install git

    # Clone watchmaker
    git clone "$GIT_REPO" --branch "$GIT_BRANCH" --recursive

    # Install required backend tools
    cd watchmaker
    python3 -m pip install --index-url="$PYPI_URL" -r requirements/basics.txt

    # Install watchmaker
    uv pip install --index-url "$PYPI_URL" --editable .

    # Run watchmaker
    watchmaker --log-level debug --log-dir=/var/log/watchmaker
    ```

*   **For Windows**: Modify `GitRepo` and `GitBranch` to reflect working
    values for your development build. Optionally modify `BootstrapUrl`,
    `PythonUrl`, `GitUrl`, and `PypiUrl` as needed.

    ```shell
    <powershell>
    $GitRepo = "https://github.com/<your-github-username>/watchmaker.git"
    $GitBranch = "<your-branch>"

    $BootstrapUrl = "https://watchmaker.cloudarmor.io/releases/latest/watchmaker-bootstrap.ps1"
    $PythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    $GitUrl = "https://github.com/git-for-windows/git/releases/download/v2.40.1.windows.1/Git-2.40.1-64-bit.exe"
    $PypiUrl = "https://pypi.org/simple"

    # Use TLS 1.2+
    [Net.ServicePointManager]::SecurityProtocol = "Tls12, Tls13"

    # Download bootstrap file
    $BootstrapFile = "${Env:Temp}\$(${BootstrapUrl}.split("/")[-1])"
    (New-Object System.Net.WebClient).DownloadFile($BootstrapUrl, $BootstrapFile)

    # Install python and git
    & "$BootstrapFile" `
        -PythonUrl "$PythonUrl" `
        -GitUrl "$GitUrl" `
        -Verbose -ErrorAction Stop

    # Clone watchmaker
    git clone "$GitRepo" --branch "$GitBranch" --recursive

    # Install required backend tools
    cd watchmaker
    python3 -m pip install --index-url="$PYPI_URL" -r requirements/basics.txt

    # Install watchmaker
    uv pip install --index-url "$PypiUrl" --editable .

    # Run watchmaker
    watchmaker --log-level debug --log-dir=C:\Watchmaker\Logs
    </powershell>
    ```

[0]: https://github.com/plus3it/watchmaker/issues
[1]: https://travis-ci.org/plus3it/watchmaker/pull_requests
[3]: https://github.com/plus3it/watchmaker/tree/main/docs
