# Contributing

First of all, thank you for contributing to MeiliSearch! The goal of this document is to provide everything you need to know in order to contribute to MeiliSearch and its different integrations.

<!-- MarkdownTOC autolink="true" style="ordered" indent="   " -->

- [Assumptions](#assumptions)
- [How to Contribute](#how-to-contribute)
- [Git Guidelines](#git-guidelines)
- [Release Process (for Admin only)](#release-process-for-admin-only)

<!-- /MarkdownTOC -->

## Assumptions

1. **You're familiar with [GitHub](https://github.com) and the [Pull Request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)(PR) workflow.**
2. **You've read the MeiliSearch [documentation](https://docs.meilisearch.com) and the [README](/README.md).**
3. **You know about the [MeiliSearch community](https://docs.meilisearch.com/resources/contact.html). Please use this for help.**

## How to Contribute

1. Make sure that the contribution you want to make is explained or detailed in a GitHub issue! Find an [existing issue](https://github.com/meilisearch/meilisearch-digitalocean/issues/) or [open a new one](https://github.com/meilisearch/meilisearch-digitalocean/issues/new).
2. Once done, [fork the meilisearch-digitalocean repository](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) in your own GitHub account. Ask a maintainer if you want your issue to be checked before making a PR.
3. [Create a new Git branch](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository).
4. Make the changes on your branch.
5. [Submit the branch as a PR](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork) pointing to the `master` branch of the main meilisearch-digitalocean repository. A maintainer should comment and/or review your Pull Request within a few days. Although depending on the circumstances, it may take longer.<br>
 We do not enforce a naming convention for the PRs, but **please use something descriptive of your changes**, having in mind that the title of your PR will be automatically added to the next [release changelog](https://github.com/meilisearch/meilisearch-digitalocean/releases/).

## Git Guidelines

### Git Branches

All changes must be made in a branch and submitted as PR.
We do not enforce any branch naming style, but please use something descriptive of your changes.

### Git Commits

As minimal requirements, your commit message should:
- be capitalized
- not finish by a dot or any other punctuation character (!,?)
- start with a verb so that we can read your commit message this way: "This commit will ...", where "..." is the commit message.
  e.g.: "Fix the home page button" or "Add more tests for create_index method"

We don't follow any other convention, but if you want to use one, we recommend [this one](https://chris.beams.io/posts/git-commit/).

### GitHub Pull Requests

Some notes on GitHub PRs:

- [Convert your PR as a draft](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/changing-the-stage-of-a-pull-request) if your changes are a work in progress: no one will review it until you pass your PR as ready for review.<br>
  The draft PR can be very useful if you want to show that you are working on something and make your work visible.
- The branch related to the PR must be **up-to-date with `master`** before merging. If it's not, you have to rebase your branch. Check out this [quick tutorial](https://gist.github.com/curquiza/5f7ce615f85331f083cd467fc4e19398) to successfully apply the rebase from a forked repository.
- All PRs must be reviewed and approved by at least one maintainer.
- The PR title should be accurate and descriptive of the changes.

## Release Process (for Admin only)

The release tags of this package follow exactly the MeiliSearch versions.<br>
It means the `v0.17.0` tag in this repository corresponds to the DO image running with MeiliSerach `v0.17.0`.

This repository currently does not provide any automated way to test and release the DO image.<br>
**Please, follow carefully the steps in the next sections before any release.**

### Test before Releasing

1. In (`scripts/deploy.sh`)[/scripts/deploy.sh] and [`server/tools/build-image.py`](/server/tools/build-image.py), change all the `vX.X.X` by the new MeiliSearch version. If you want to test with a MeiliSearch RC, replace them by the right RC version tag (`vX.X.XrcX`).

2. Commit your changes on a new branch and open the related PR.

3. Create a tag on the PR branch corresponding to the MeiliSearch version you've just changed(`vX.X.X` or `vX.X.XrcX`):
```bash
$ git tag vX.X.X
$ git push origin <branch-name>
```

4. Build the image:
```bash
$ WIP
```

3. ...

_WIP_

⚠️ If you've done this steps with a MeiliSearch RC version, don't forget to finally remove the tag from the repository via the [GitHub interface](https://github.com/meilisearch/meilisearch-digitalocean/releases): click on the tag name, and then, on the red `Delete` button.

### Publish the DO Image

⚠️ The DO image should never be published with a `RC` version of MeiliSearch.

Once the tests in the previous section have been done:

1. Merge the PR.

2. Move the tag from the branch commit to the last `master` commit:
- Delete the tag remotely via the [release GitHub interface](https://github.com/meilisearch/meilisearch-digitalocean/releases). Click on the tag name and then on the red `Delete` button.
- Delete and re-create the tag in your local repository on the right commit:
```bash
$ git tag -d vX.X.X
$ git checkout master
$ git pull origin master
$ git tag vX.X.X
```
- Push it to the remote repository:
```bash
$ git push --tag origin master
```

3. ...

### Update the DO Image between two MeiliSearch Releases

It can happen you need to release a new DO image but you cannot wait for the new MeiliSearch release.<br>
For example, the `v0.17.0` is already pushed but you find out you need to fix the installation script: you can't wait for the `v0.18.0` release and need to re-publish the `v0.17.0` DO image.

In this case:
- Delete the current tag remotely and locally (see point 2 in [Publish the DO Image](#publish-the-do-image) to know how to do this).
- Apply your changes and test them (see [Test before Releasing](#test-before-releasing)).
- Publish again (see [Publish the DO Image](#publish-the-do-image))

<hr>

Thank you again for reading this through, we can not wait to begin to work with you if you made your way through this contributing guide ❤️