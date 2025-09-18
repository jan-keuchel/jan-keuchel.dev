---
title: jankeuchel.dev
layout: default
---
<ul>
    {% assign postsByYear = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
    {% for year in postsByYear %}
        <li>
            <h3>{{ year.name }}</h3>
            <ul>
                {% for post in year.items %}
                    <li>
                        <article> 
                            <a href="{{ post.url }}">
                                <div>
                                    <h3>{{ post.title }}</h3>
                                    <div>
                                        <p>
                                            {{ post.desc }}
                                        </p>
                                    </div>
                                    <div>
                                        <time>
                                            {{ post.published }}
                                        </time>
                                    </div>
                                </div>
                            </a>
                        </article>
                    </li>
                {% endfor %}
            </ul>
        </li>
    {% endfor %}
</ul>
