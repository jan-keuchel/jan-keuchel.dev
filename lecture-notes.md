---
title: Lecture Notes
layout: default
---
# Lecture Notes

In here you will find my notes to some of the courses I took at HKA.

<ul>
    {% for lecture in site.data.lecture-notes %}
        <li>
            <a href="{{ lecture.link }}">{{ lecture.name }}</a>
        </li>
    {% endfor %}
</ul>
