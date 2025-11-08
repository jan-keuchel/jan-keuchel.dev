---
title: keuchel.dev
layout: default
---

## Hello there,
my name is Jan.

I'm a Computer Science student currently living in Karlsruhe.
{: .mb-1 }

You somehow managed to land on my personal webpage.
On here, I publish blogs, share lecture notes and showcase some of my projects.
{: .mb-05 }

The different sections can be found via the navigation bar above.
Below are the blog posts sorted by year.
The flags denote the language the post is written in.
{: .mb-05 }

<ul class="plain-list">
    {% assign postsByYear = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
    {% for year in postsByYear %}
        <li>
            <h2 class="mb-1 bb">{{ year.name }}</h2>
            {% include item-list.html collection=year.items %}
            <div class="mb-1"></div>
        </li>
    {% endfor %}
</ul>
