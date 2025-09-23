---
title: Display of code on a webpage
desc: This document shows how code looks on a webpage
published: 18.09.2025
---
# CODE

This article is about displaying code. Either inline a webpage like this: `int i = 0;` or as a block:
{% highlight go linenos %}
package main

include (
    "fmt"
    )

func main() {
    fmt.Println("This is a test!!!")
}
{% endhighlight %}

# Math
Another thing to test is the use of LaTeX. In this case, it is achieved via KaTeX. This $x$ is inline math. While this block:
\\[ 
    \int_{-\infty}^\infty e^{-x^2} dx = \sqrt{\pi} 
\\]
is a block.

Might this work?
\\[
    \int_{-\infty}^\infty e^{-x^2} dx = \sqrt{\pi}
\\]
