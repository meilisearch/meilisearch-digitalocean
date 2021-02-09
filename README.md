<p align="center">
  <img src="https://res.cloudinary.com/meilisearch/image/upload/v1612343595/SDKs/meilisearch_digital_ocean.svg" alt="MeiliSearch-Python" width="200" height="200" />
</p>

<h1 align="center">MeiliSearch DigitalOcean</h1>

<h4 align="center">
  <a href="https://github.com/meilisearch/MeiliSearch">MeiliSearch</a> |
  <a href="https://docs.meilisearch.com">Documentation</a> |
  <a href="https://slack.meilisearch.com">Slack</a> |
  <a href="https://roadmap.meilisearch.com/tabs/1-under-consideration">Roadmap</a> |
  <a href="https://www.meilisearch.com">Website</a> |
  <a href="https://docs.meilisearch.com/faq">FAQ</a>
</h4>

<p align="center">
  <a href="https://github.com/meilisearch/meilisearch-python/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-informational" alt="License"></a>
</p>

<p align="center">⚡ MeiliSearch tools for DigitalOcean integration</p>

**MeiliSearch DigitalOcean** is a set of tools and scripts to improve user deployment of MeiliSearch on [DigitalOcean](https://www.digitalocean.com/).

**MeiliSearch** is an open-source search engine. [Discover what MeiliSearch is!](https://github.com/meilisearch/MeiliSearch)


## Table of Contents <!-- omit in toc -->

- [✋ Disclaimers](#-disclaimers)
- [📖 Documentation](#-documentation)
- [🔧 Installation](#-installation)
- [⚙️ Development Workflow and Contributing](#️-development-workflow-and-contributing)

## ✋ Disclaimers

### Deploying MeiliSearch on DigitalOcean  <!-- omit in toc -->

If you are looking for a guid to deploy a MeiliSearch Instance on DigitalOcean visit [the dedicated page of our documentation](https://docs.meilisearch.com/create/how_to/digitalocean_droplet.html#deploy-a-meilisearch-instance-on-digitalocean)

### Content of this repository  <!-- omit in toc -->

This repository contains a few tools and scripts used mainly by the MeiliSearch team, aiming to provide our users simple ways to deploy and configure MeiliSearch in the Cloud. As our heart resides on the Open Source community, we maintain several of this tools as open source project/repository.

## 📖 Documentation

See our [Documentation](https://docs.meilisearch.com/learn/tutorials/getting_started.html) or our [API References](https://docs.meilisearch.com/reference/api/).

## 🔧 Installation

After cloning this repository, install python dependencies with the following command:

```bash
$ pip3 install -r requirements.txt
```

Before running any script, make sure to obtain a DigitalOcean Access Key and set it in your environment:

```bash
export DIGITALOCEAN_ACCESS_TOKEN="XxXxxxxXXxxXXxxXXxxxXXXxXxXxXX"
```

## ⚙️ Development Workflow and Contributing

Any new contribution is more than welcome in this project!

If you want to know more about the development workflow or want to contribute, please visit our [contributing guidelines](/CONTRIBUTING.md) for detailed instructions!

<hr>

**MeiliSearch** provides and maintains many **SDKs and Integration tools** like this one. We want to provide everyone with an **amazing search experience for any kind of project**. If you want to contribute, make suggestions, or just know what's going on right now, visit us in the [integration-guides](https://github.com/meilisearch/integration-guides) repository.
