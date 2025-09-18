---
title: Books
layout: default
---
<ul>
    {% for book in site.books %}
        <li>
            <article> 
                <a href="{{ book.url }}">
                    <div>
                        <h3>{{ book.title }}</h3>
                        <div>
                            <p>
                                {{ book.desc }}
                            </p>
                        </div>
                        <div>
                            <time>
                                {{ book.published }}
                            </time>
                        </div>
                    </div>
                </a>
            </article>
        </li>
    {% endfor %}
</ul>
