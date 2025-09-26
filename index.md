---
title: jankeuchel.dev
layout: default
---
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
