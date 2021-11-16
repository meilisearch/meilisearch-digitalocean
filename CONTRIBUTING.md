# Contributing <!-- omit in TOC -->

First of all, thank you for contributing to MeiliSearch! The goal of this document is to provide everything you need to know in order to contribute to MeiliSearch and its different integrations.

- [Assumptions](#assumptions)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Git Guidelines](#git-guidelines)
- [Release Process (for internal team only)](#release-process-for-internal-team-only)

## Assumptions

1. **You're familiar with [GitHub](https://github.com) and the [Pull Request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)(PR) workflow.**
2. **You've read the MeiliSearch [documentation](https://docs.meilisearch.com) and the [README](/README.md).**
3. **You know about the [MeiliSearch community](https://docs.meilisearch.com/resources/contact.html). Please use this for help.**

## How to Contribute

1. Make sure that the contribution you want to make is explained or detailed in a GitHub issue! Find an [existing issue](https://github.com/meilisearch/meilisearch-digitalocean/issues/) or [open a new one](https://github.com/meilisearch/meilisearch-digitalocean/issues/new).
2. Once done, [fork the meilisearch-digitalocean repository](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) in your own GitHub account. Ask a maintainer if you want your issue to be checked before making a PR.
3. [Create a new Git branch](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository).
4. Make the changes on your branch.
5. [Submit the branch as a PR](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork) pointing to the `main` branch of the main meilisearch-digitalocean repository. A maintainer should comment and/or review your Pull Request within a few days. Although depending on the circumstances, it may take longer.<br>
 We do not enforce a naming convention for the PRs, but **please use something descriptive of your changes**, having in mind that the title of your PR will be automatically added to the next [release changelog](https://github.com/meilisearch/meilisearch-digitalocean/releases/).

## Development Workflow

### Setup <!-- omit in toc -->

Install the required python packages to your environment:

```bash
pip3 install -r requirements.txt
```

### Tests and Linter <!-- omit in toc -->

Each PR should pass the tests and the linter to be accepted.

```bash
# Linter
pylint tools
```

## Git Guidelines

### Git Branches <!-- omit in TOC -->

All changes must be made in a branch and submitted as PR.
We do not enforce any branch naming style, but please use something descriptive of your changes.

### Git Commits <!-- omit in TOC -->

As minimal requirements, your commit message should:
- be capitalized
- not finish by a dot or any other punctuation character (!,?)
- start with a verb so that we can read your commit message this way: "This commit will ...", where "..." is the commit message.
  e.g.: "Fix the home page button" or "Add more tests for create_index method"

We don't follow any other convention, but if you want to use one, we recommend [this one](https://chris.beams.io/posts/git-commit/).

### GitHub Pull Requests <!-- omit in TOC -->

Some notes on GitHub PRs:

- [Convert your PR as a draft](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/changing-the-stage-of-a-pull-request) if your changes are a work in progress: no one will review it until you pass your PR as ready for review.<br>
  The draft PR can be very useful if you want to show that you are working on something and make your work visible.
- The branch related to the PR must be **up-to-date with `main`** before merging. If it's not, you have to rebase your branch. Check out this [quick tutorial](https://gist.github.com/curquiza/5f7ce615f85331f083cd467fc4e19398) to successfully apply the rebase from a forked repository.
- All PRs must be reviewed and approved by at least one maintainer.
- The PR title should be accurate and descriptive of the changes.

## Release Process (for internal team only)

⚠️ The [cloud-scripts](https://github.com/meilisearch/cloud-scripts) repository should be upgraded to the new version before this repository can be updated and released.

The release tags of this package follow exactly the MeiliSearch versions.<br>
It means that, for example, the `v0.17.0` tag in this repository corresponds to the DO image running MeiliSearch `v0.17.0`.

This repository currently does not provide any automated way to test and release the DO image.<br>
**Please, follow carefully the steps in the next sections before any release.**

### Set your environment <!-- omit in TOC -->

After cloning this repository, install python dependencies with the following command:

```bash
pip3 install -r requirements.txt
```

Before running any script, make sure to [obtain a DigitalOcean API Token](https://www.digitalocean.com/docs/apis-clis/api/create-personal-access-token/) and set it in your environment:

```bash
export DIGITALOCEAN_ACCESS_TOKEN="XxXxxxxXXxxXXxxXXxxxXXXxXxXxXX"
```

After [adding your SSH key to DigitalOcean account](https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/), include the fingerprint of your SSH key in the `SSH_KEYS_FINGERPRINTS` list on [`tools/config.py`](tools/config.py)

### Test before Releasing <!-- omit in TOC -->

1. In [`tools/config.py`](tools/config.py), update the `MEILI_CLOUD_SCRIPTS_VERSION_TAG` variable value with the new MeiliSearch version you want to release, in the format: `vX.X.X`. If you want to test with a MeiliSearch RC, replace it by the right RC version tag (`vX.X.XrcX`).

2. Run the [`tools/build_image.py`](tools/build_image.py) script to build the DigitalOcean image without analytics:

```bash
python3 tools/build_image.py --no-analytics
```

This command will create a DigitalOcean Droplet on MeiliSearch's account and configure it in order to prepare the Marketplace image. It will then create a snapshot, which should be ready to be published to the Marketplace. The Droplet will automatically be removed from the account after the image creation.<br>
The image name will be MeiliSearch-v.X.X.X-Debian-X.

3. Test the image: create a new Droplet based on the new snapshot `MeiliSearch-v.X.X.X-Debian-X`, and make sure everything is running smoothly. Connect via SSH to the droplet and test the configuration script that is run automatically on login.<br>
🗑 Don't forget to destroy the Droplet after the test.

4. When you are ready to create the final image to release juste remove the `--no-analytics` option

```bash
python3 tools/build_image.py
```

### Publish the DO Image <!-- omit in TOC -->

⚠️ The DO image should never be published with a `RC` version of MeiliSearch.

Once the tests in the previous section have been done:

1. Commit your changes on a new branch.

2. Open a PR from the branch where changes where done and merge it.

3. Create a git tag on the last `main` commit:

```bash
git checkout main
git pull origin main
git tag vX.X.X
git push origin vX.X.X
```

⚠️ If changes where made to the repository between your testing branch was created and the moment it was merged, you should consider building the image and testing it again. Some important changes may have been introduced, unexpectedly changing the behavior of the image that will be published to the Marketplace.

4. In the [DigitalOcean Vendor Portal](https://marketplace.digitalocean.com/vendorportal), click on the title of the `MeiliSearch` image. A form will open for a new image submission. Update the information regarding the new version in the form:

- Update the `App version` (with the version number, without the starting v, so `vX.X.X` becomes `X.X.X`).
- In the `System image` field, click on `Select system image` and select the image you have tested from the list (`MeiliSearch-v.X.X.X-Debian-X`).
- In the `Software Included` field, update the MeiliSearch version.
- Check the `Application summary`, `Application Description` and `Getting started instructions` fields for any inconsistent information that should be updated about MeiliSearch usage or installation.
- In the `Reason for update` field, write "Bump MeiliSearch to vX.X.X".
- Verify the form, and hit on `Submit`.

⚠️ When the image is submitted to the Marketplace, MeiliSearch will immediately lose its ownership. The submitted image won't appear anymore in the organization dashboard, and no further modification can be done.

This will start the DigitalOcean review process. This can take a few days, and the result will be notified via email to the DigitalOcean admin account. If the image is accepted, it will be automatically published on the Marketplace. If it is rejected, an email explaining the problems will be sent to administrators.

### Update the DO Image between two MeiliSearch Releases <!-- omit in TOC -->

It can happen that you need to release a new DO image but you cannot wait for the new MeiliSearch release.<br>
For example, the `v0.17.0` is already pushed but you find out you need to fix the installation script: you can't wait for the `v0.18.0` release and need to re-publish the `v0.17.0` DO image.

In this case:

- Apply your changes and reproduce the testing process (see [Test before Releasing](#test-before-releasing)).
- Delete the current tag remotely and locally:

```bash
git push --delete origin vX.X.X
git tag -d vX.X.X
```

- Publish the image again (see [Publish the DO Image](#publish-the-do-image))

<hr>

Thank you again for reading this through, we can not wait to begin to work with you if you made your way through this contributing guide ❤️
