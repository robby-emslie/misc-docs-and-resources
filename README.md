# Miscellaneous Docs and Resources

**6 July 2026: An update.** It has been a long time since I've used this account. I've largely been pre-occupied with projects for my day job and other projects. Bear with me as I build out my portfolio on here; if there's something you'd like to see, please send me a message! I have a whole bunch of stuff to collect from across a handful of projects spanning automation (Workato and n8n, including custom integration layers) and software solutions to Classical Education resources; there are even a bunch of tools and resources I've built and/or compiled for liturgical and spiritual purposes that I'll eventually include here.

I'm a typical polymath, philosopher, and "lay monk" -- above all else, I'm powered by caffeine and extremely disorganized in my personal space. Don't judge me! :-) <3

A collection of documentation, resources, and other disparate nonsense that doesn't fit anywhere else.

## Contents

- [About Me](#about-me)
- [**A script library**](./scripts/) where I've (very recently) started trying to aggregate all the most useful scripts I've created over the years.
    - [Python](./scripts/python/)
        - [`scraper.py`](./scripts/python/scraper.py) is a simple commandline utility for scraping HTML pages, extracting tabular data, and rendering it in CSV format.
        - [`stripDataFromJson.py`](./scripts/python/stripDataFromJson.py) is a tool to strip the values from a JSON source file -- particularly useful when you need to share an API schema but don't want to (or *can't*) share the data in your sample. This will strip out all the data and replace it with a data-type identifier (like `"<string>"` or `"<integer>"`) to preserve the formatting guidelines.
        - [`workatoEmbeddedApi.py`](./scripts/python/workatoEmbeddedApi.py) is a class and associated methods for the Workato API to enable common tasks from a local enviornment: pull environment details, add collaborators to workspaces, do stuff with environment properties, etc. Nothing in here is "magic" -- it's all just standard operations from the [Workato Docs](https://docs.workato.com) rendered in Python because I got tired of typing it out in *every* admin script I wrote. Some of these functions can be rehashed in recipes to host admin and DevOps pipelines directly in Workato.
    - [Bash](./scripts/bash/)
    - [JavaScript](./scripts/javascript/)
        - [`csvExtractAndTransform.js`](./scripts/javascript/csvExtractAndTransform.js) is a simple ETL utility for parsing data out of a CSV source, transforming fields according to JSON-encoded transformation formulae
    - [Ruby](./scripts/ruby/)
- Various [**guides, documentation, how-tos, and cheat sheets**](./docs/) for Linux, software development and scripting, networking, cybersecurity, and so on.
    - [A guide to spinning up n8n locally](./docs/setup_n8n_dev_environment.md) for local automation and node development. This guide is based on using Podman (a Docker alternative) and also implements a PostgreSQL database to ensure data persistance -- I assume you actually want to *use* your automation environment, and not just develop nodes at random, yes? ;-)
- [**Essays**](./essays/) I've written relevant to the technology industry
    - [An Ethical Analysis of the Proliferation of Artificial Intelligence](./essays/2025-ethical_proliferation_of_ai.md) details the conundrum of AI proliferation from the perspective of ethical philosophy. This essay dares to ask whether, in our haste to implement AI, we have presumed an affirmative to a crucial question -- "*should* we...?" -- and suggests that, until we turn our attention back to this query, any further implementation becomes is inherently unethical.

## About Me

I don't fit neatly into too many boxes. I actually kind of hate labels, anyway. There are only a few that seem to fit for me, and they're more accurately descriptors, not identifiers:

Catholic. Autodidact. Polymath. Philosopher. IT worker. Music lover. Coffee junkie. Neurodiverse.

Everything else is just fluid details, but it all seems to fit together well enough to work for me. God made me something of an enigma and I've learned to embrace that.

I grew up in Florida, lived in Tennessee for 10 years, and now residing happily in New England. I'm an IT worker, mostly dealing with software automation, but I'm also a decent carpenter. I also have some additional skills in animal care and fire/EMS from years of volunteer work.

And, as it turns out, I'm a surprisingly good teacher, going on my fifth year of pedagogy in a classical (liberal arts tradition) curriculum. Look for some resources for that, here, too.

I love music and the arts -- especially in the classical traditions. It draws some humorous looks when people ask my favorite bands and I start with The Cure and end with Antonin Dvorak. And I'm a philosophy geek; in 2023, I finally went back to school -- this time with an actual degree in mind -- to study philosophy. Eventually, maybe I'll study theology.

I didn't grow up in a particularly religious household, but I've become steadily more grounded in my faith since high school. My family was Episopalian; during high school and my young adult years, I explored every religion I could, but ultimately ended up right back at an Episcopal Church. It took another five years after that to get to Catholicism. Then another period of apostasy, a great deal of spiritual turmoil, and now I'm happily involved in the Church and I feel like I've finally found my spot.

I have some ideas of what I want to do with that, and with all of this -- tying it all together -- in the coming years and decades, but I try not too get too invested in the future. Things change, unforeseen events happen, circumstances shift... it's much easier and less stressful to be fluid about it all. At the end of the day, I'm thankful for every good gift God has given me, but I'm also not under any illusions that it's permanent. Even if I spend the rest of my life in this spot, it's only the Faith, Hope, and Love that I've built up in my life that I'll take with me on the final adventure. "The rest," as they say, "is details."

## Usage and Distribution

Feel free to explore, read, use, and share the contents of this repository. Everything contained herein is provided "as-is" under the [Creative Commons BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.