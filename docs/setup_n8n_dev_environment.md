# Setup an n8n development environment

*July 2026*

Whether you're considering digging into the powerful [n8n](https://www.n8n.io) automation platform, and especially if you want to create custom nodes or tinker with the platform's codebase, or you just want to *use* the platform for exactly the purposes it was intended, you're going to need a local instance of n8n to get started. Here's how to do it in no-time-flat from a container image, complete with a SQL database to power it.

> [!NOTE]
> This guide is written based on my own experience setting this up in my home lab. I'm running on ParrotOS, and the commands reflect that platform. In most cases, if you're using a non-Debian Linux distribution, you shouldn't run into any difficulty porting this guide to your environment. On Windows or MacOS, it might be a little less straightforward and I would advise you to consult the docs and/or a knowledgeable friend to help navigate the process. I can tell you that, if your goal is just to spin up a dev-env for building a node, the [n8n docs](https://docs.n8n.io/) contain a solid [how-to for setting up your environment](https://docs.n8n.io/connect/create-nodes/build-your-node/set-up-your-development-environment) and running the platform locally (without a container).

## Contents

1. [Grab development dependencies](#1-install-dependencies)
    1. [Development dependencies](#11-development-dependencies-nodejs-npm-and-nvm)
    2. [Podman](#12-setting-up-podman)
2. [Build your Dockerfile](#2-build-your-dockerfile)
3. [Spin up the n8n environment](#3-spin-up-the-n8n-environment)

## 1. Install dependencies

To build custom nodes for n8n, you need to have the tools to do it. The platform is built on **Node.js**, so you'll need to install that and the **npm** package manager. You can do both (and manage your installed versions if you're planning on, or already, working on other Node.js projects) with the **nvm** tool, so start there.

If you just want to run the n8n platform to automate stuff, and you don't want to build custom nodes or play with the n8n codebase, you can forego installing all the development tools and skip down to [1.2: Setting up Podman](#12-setting-up-podman).

### 1.1 Development dependencies: Node.js, npm, and nvm

In theory, you should be able to run

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.5/install.sh | bash
```

in your terminal and this should do the hard work for you. If you don't have `curl`, or would prefer to use `wget`, you can find a similar command, along with more detailed instructions on how to make npm work, in [the nvm docs on GitHub](https://github.com/nvm-sh/nvm#installing-and-updating).

> [!TIP]
> At the time I'm writing this, the current **npm** is version 0.40.5, which is reflected in the URL for getting and running the `install.sh` script in the above command. Visit that link to the nvm docs on GH to confirm the version if you think that might be outdated. Keep your software current!

Once you've got nvm setup, you can use it to install and swap between Node.js versions:

```bash
# install Node.js version 24
nvm install 24

# tell nvm to use version 24
nvm use 24

# tell nvm to use Node.js version 18
nvm use 18

# switch back to version 24
nvm use 24
```

By this point, npm should have *also* been installed -- typically when you install Node.js. You can verify that if you try to check the version; if it's installed it will tell you the version:

```bash
npm -v
# 9.2.0
```

If, for some reason, it's not there, you can run their installer script with

```bash
curl -qL https://www.npmjs.com/install.sh | bash
```

If that doesn't work, or you want more details, they have their own [docs on GitHub](https://github.com/npm/cli/blob/latest/README.md) that you might want to dig into.

### 1.2 Setting up Podman

Assuming you've gotten through all of that without too much difficulty, all that's left is getting Podman (or Docker, if you prefer). This will vary, depending on the platform you're using, so I would suggest heading over to [their installation instructions](https://podman.io/docs/installation) if you need help. I was able to just run

```bash
sudo apt -y install podman
```

and let it do its thing.

Okay. Ready? Let's get "down and dirty" with setting up your n8n instance.

## 2. Build your Dockerfile

> [!NOTE]
> These instructions are based on my own implementation in my home lab, and I'm using [**Podman**](https://podman.io/) instead of the more popular [**Docker**](https://www.docker.com/) platform to manage my containers, but it works exactly the same. In most cases, you can simply replace `podman` with `docker` in the commands (for example, `podman-compose` and `docker-compose` are generally interchangeable) to achieve the same result, but if you're running into problems, you may need to consult your container manager's documentation.

Thwe  beautiful thing about using the Dockerfile to build your n8n instance is that it's quick, and you can change your setup on-the-fly with minimal effort. But keep something in mind: **if you don't setup a persistent database with PostgreSQL and tie it to your n8n instance, you'll lose your n8n configuration and any workflows you've built in there every time you shutdown the environment**. Without a database configured, n8n will just use a SQLite database to power itself, and that's probably sufficient if you're just building nodes and not trying to *use* the environment for anything, but if you *do* want to actually automate stuff, you'll need to setup a database that persists through spin-downs and restarts. I'll give you both versions of the Dockerfile, but unless you're regularly building nodes and basically never running workflows, it doesn't make much sense to forego setting up a database.

For a basic environment with a self-destructing SQLite backend:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - DB_TYPE=sqlite
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  n8n_data:
```

Obviously, this isn't very useful. Here's a more "involved" configuration that bakes a PostgreSQL database into the environment. 

## 3. Spin up the n8n environment