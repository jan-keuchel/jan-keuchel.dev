---
title: jankeuchel.dev
layout: default
---
## This is the first section
In here, you can find some text...

## This is the second section
With more text.

<ul>
    {% assign postsByYear = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
    {% for year in postsByYear %}
        <li>
            <details>
                <summary>{{ year.name }}</summary>
                <ul>
                    {% for post in year.items %}
                        <li>
                            <a href="{{ post.url }}">{{ post.title }}</a>
                            <span>({{ post.date | date: "%b %d" }})</span>
                        </li>
                    {% endfor %}
                </ul>
            </details>
        </li>
    {% endfor %}
</ul>
