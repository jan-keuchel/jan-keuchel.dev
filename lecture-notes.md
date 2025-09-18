---
title: Lecture Notes
layout: default
---
In here you will find my notes to some of the courses I took at HKA.

<ul>
    {% for lecture in site.lecture-notes %}
        <li>
            <article> 
                <a href="{{ lecture.url }}">
                    <div>
                        <h3>{{ lecture.title }}</h3>
                        <div>
                            <p>
                                {{ lecture.desc }}
                            </p>
                        </div>
                        <div>
                            <time>
                                {{ lecture.published }}
                            </time>
                        </div>
                    </div>
                </a>
            </article>
        </li>
    {% endfor %}
</ul>
