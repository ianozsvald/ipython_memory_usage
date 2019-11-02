# Conda Build integration

Conda build requires three files.
* meta.yaml - Definition file.
* bld.bat   - Script file with instructions for Windows builds.
* build.sh  - Script file with instructions for *nix builds.

## Build Package Locally
Relevant documentation: https://docs.conda.io/projects/conda-build/en/latest/user-guide/tutorials/build-pkgs.html

    # Clone repo
    git clone git@github.com:ianozsvald/ipython_memory_usage.git
    
    # Enter repo
    cd ipython_memory_usage
    
    # Build package locally
    conda-build recipe/meta.yaml
    
    # Check Smithy [Requires conda-smithy: `conda install -n root -c conda-forge conda-smithy`]
    cd recipe
    conda smithy recipe-lint

    # Test package locally
    conda install --use-local ipython_memory_usage


## Change the build source
Conda build supports a number of sources (source:) from which to prepare packages.

**Locally**

    # Set absolute or relative path
    path: ..

**Git**

    # Pin to a revision or version
    git_rev: b36bcc2f85a49dc33eec125d541fe8bee6b67cfd
    git_url: https://github.com/ianozsvald/ipython_memory_usage

**Remote package**

    # Set the URL and Signature (on ubuntu you can use `sha256sum source_file.tar.gz`)
    url: https://files.pythonhosted.org/packages/ed/8a/38fa2249179df377477a6967caf027de0ae93c6813c4e664f517da90f9e9/ipython_memory_usage-1.1.tar.gz
    sha256: 1f4697210257f853fea74de0cf3fae60a32e550e578bac6f46de9b40c550422b


## Updating the package
Make sure to update the version number and if not building locally pin the requsite source (git version or pypi package)


## Deploying to Conda Forge
In order to deploy to conda forge, follow the instructions on https://conda-forge.org/#contribute

Fork https://github.com/conda-forge/staged-recipes

Add meta.yaml to recipes/ipython_memory_usage .

Make sure meta-yaml uses a source package (url: .... tar.gz), not git!

Create a pull request.
