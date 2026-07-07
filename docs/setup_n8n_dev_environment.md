# Setup an n8n development environment

Version 1.0
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

## 2. Build your docker-compose.yml and Dockerfile

> [!NOTE]
> These instructions are based on my own implementation in my home lab, and I'm using [**Podman**](https://podman.io/) instead of the more popular [**Docker**](https://www.docker.com/) platform to manage my containers, but it works exactly the same. In most cases, you can simply replace `podman` with `docker` in the commands (for example, `podman-compose` and `docker-compose` are generally interchangeable) to achieve the same result, but if you're running into problems, you may need to consult your container manager's documentation.

Thwe  beautiful thing about using the a container to build your n8n instance is that it's quick, and you can change your setup on-the-fly with minimal effort. But keep something in mind: **if you don't setup a persistent database with PostgreSQL and tie it to your n8n instance, you'll lose your n8n configuration and any workflows you've built in there every time you shutdown the environment**. Without a database configured, n8n will just use a SQLite database to power itself, and that's probably sufficient if you're just building nodes and not trying to *use* the environment for anything, but if you *do* want to actually automate stuff, you'll need to setup a database that persists through spin-downs and restarts. I'll give you both versions of the `docker-compose.yml`, but unless you're regularly building nodes and basically *never* running workflows, it doesn't make much sense to forego setting up a database.

### The docker-compose.yml file

This is the part that builds your docker image from the n8n source image (and your PostgreSQL database if you're using it).

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

Obviously, this isn't very useful. Here's a more "involved" configuration that bakes a PostgreSQL database into the environment. Replace `<your_super_strong_password> with a secure password for your database.

```yaml
services:
  postgres:
    image: docker.io/library/postgres:15-alpine
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=<your_super_strong_password>
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  n8n:
    image: docker.io/n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=<your_super_strong_password>
    volumes:
      - n8n_data:/home/node/.n8n
      - ./custom-nodes:/home/node/.n8n/custom
    depends_on: 
      - postgres
    restart: unless-stopped

volumes:
  n8n_data:
  postgres_data:
```

### Dockerfile for custom node development

If you plan on creating your own custom nodes, you'll need to take a few more steps after you finish developing the node(s) to make them available. Once you've built your custom node and run `npm run build`, you'll need to install it in your host environment, so you'll need to tell your container environment to copy the custom node from `/some/directory/n8n-nodes-custom_node` into its `./custom-nodes` directory and run `npm install` when the container spins up.

This happens in two steps. First you need to build the `Dockerfile`, itself, then you need to modify your `docker-compose.yml` file to reference *that* instead of just the source n8n image.

#### 1. Create the Dockerfile

This isn't terribly difficult. You're just creating a simple `Dockerfile` that tells your container host to build an image from tne n8nio image and, copy the custom node into the image when it spins up, and run the `npm install` commands to install your node. It should look something like this:

```Dockerfile
FROM n8nio/n8n:latest

# Copy your custom node(s) into the container -- you'll need a COPY for each node package
COPY source-directory/n8n-nodes-custom_node /home/node/.n8n/custom/n8n-nodes-custom_node

# And install it -- you'll need RUN for each node package
RUN cd /home/node/.n8n/custom/n8n-nodes-custom_node && npm install && npm run build

# If you need to add any special files, like credentials or configurations, for each one add:
COPY configs-or-creds.json /home/node/.n8n/configs-or-creds.json
```

Then you need to edit the `docker-compose.yml` to read **your** `Dockerfile`, instead of the default from n8nio...

#### 2. Modify docker-compose.yml

This part is super easy. Open the `docker-compose.yml` you built earlier and change the n8n service like this:

```yaml
services:
  n8n:
    build: . # this tells your container composer to `build` a container instead of running an `image`
    ports:
      - "5678:5678:" # ... the rest of the config stays the same ...
```

That's basically it. Super simple. Depending on how you've got your directories structured, you may need to change this a little bit, but that part should be fairly self-explanatory if you understand how to navigate the filesystem on your host box.

Let's make it do something!

## 3. Spin up the n8n environment

If you've gotten along fine to this point, you're past the hardest part. Hop back into your terminal, and do this:

```bash
# Navigate to the directory you stashed your Dockerfile in
cd /path/to/docker-compose.yml

# if you're just running the default image (not baking in nodes with a customer Dockerfile), do this:
podman-compose up -d

# if you're including custom nodes (or otherwise using a custom Dockerfile), do this:
podman-compose up --build
```

*Et voila!* You should now have your n8n environment up and running. You can access it from your browser by heading over to http://localhost:5678/ -- you'll need to setup the owner account to get started. Happy automating!