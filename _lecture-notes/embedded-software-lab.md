---
title: Embedded Software Labor
desc: Durchlauf des Labors des Moduls "Embedded Software"
published: 2025-11-07
logo: /assets/images/HKA.png
language: de
ongoing: true
---

## Kontext
Die Aufgabe ist, einen Decoder für ein Summensignal von GPS-Daten zu schreiben.
Als Eingabe ist ein Summensignal gegeben.
Dieses ist eine asynchrone Überlagerung von 4 der insgesamt 24 Satelliten und ist 1023 Chips lang.
Zunächst wird der Decoder in C++ geschrieben, danach in C.
Anschließend werden die Laufzeiten verglichen und die Programme optimiert.

## C++
### Generierung von Chipsequenzen
Um das Summensignal dekodieren zu können, benötigt man die Chipsequenzen.
Die Verknüpfungskonfigurationen der Register waren auf dem Übungsblatt gegeben.

Hier die Funktion `generate_chip_seq`, welche die Chipsequenz eines Satelliten basierend auf der Konfiguration der Register generiert.

{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_chip_seq_gen %}
{% endhighlight %}

Mit Hilfe dieser Funktion werden nun die Chipsequenzen generiert
{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_generating_chip_sequences %}
{% endhighlight %}

und dann in Vektoren über `-1, 1` übersetzt:
{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_translation_to_vec %}
{% endhighlight %}

### Dekodierung
#### Zur Theorie
Zu zwei Chipsequenzen $c_i, c_j$ und einem Shift $\delta$ ist das Korrelationsprodukt $\mathcal{CP}$ definiert als:

$$
    \mathcal{CP}_{ij}(\delta) := c_i \cdot (c_j \ll \delta)
$$

. Hierbei werden $c_i,c_j$ als Vektoren betrachtetist, $\cdot$ ist das Skalarprodukt und $\ll$ ist die Linksrotation.
Normanisiert man $\mathcal{CP}$, so erhält man einen Wert $\rho \in \[-1, 1\]$: den Korrelationskoeffizienten.

Durch die Generierung haben die Chipsequenzen die Eigenschaft, dass diese in der Autokorrelation -- also dem Korrelationsprodukt mit $i=j$ und $\delta = 0$ -- den Wert $n = \vert c \vert $ liefern und für ein $\delta \ne 0$ einen Wert $\epsilon \approx 0$.
Im Kreuzkorrelationsprodukt -- also dem Korrelationsprodukt mit $i \ne j$ und $\delta$ beliebig -- wird ausschließlich ein Wert $\epsilon \approx 0$ geliefert.

Will ein Satellit $S_i$ den Wert $b=1$ senden, so sendet er seine Chipsequenz $c_i$.
Will $S_i$ den Wert $b=0$ senden, so sendet er das inverse von $c_i$ (Nullen und Einsen geflippt).

Im Labor wird die Annahme gemacht, dass jeder der Satelliten seinen gesendeten Chip $b \in \\{0,1\\}$ periodisch sendet, also davor und danach das gleiche $b$ gesendet hat bzw. danach senden wird.
Das Summensignal $\mathcal{S}$ ist die Summe aus mehreren, übereinander gelagerten und verschobenen Chipsequenzen:

<div class="full-width-img">
    {% include lecture_data/embedded-software-lab/sumsignal_tex %}
</div>

Um dekodieren zu können, welcher Satellite welches Bit gesendet hat, muss für jede Chipsequenz $c_i$ mit mit dem Summensignal $\mathcal{S}$ für jedes $\delta$ das Skalarprodukt gebildet werden.

Dabei können für einen Satelliten $S_i$ und ein $\delta$ folgende Werte für $\mathcal{CP}$ berechnet werden:
- **$\mathcal{CP} \approx 0 \longrightarrow$** $S_i$ hat kein Bit mit einer Verschiebung von $\delta$ gesendet.
- **$\mathcal{CP} \approx \vert c_i \vert \longrightarrow$** $S_i$ hat bei einer Verschiebung von $\delta$ eine $1$ gesendet.
- **$\mathcal{CP} \approx -\vert c_i \vert \longrightarrow$** $S_i$ hat bei einer Verschiebung von $\delta$ eine $0$ gesendet.


#### Berechnung der gesendeten Bits
Für jeden Satellit -- somit für jede Chipsequenz -- wird also für jedes Offset das Korrelationsprodukt berechnet.
Wird ein "Ausschlag" gefunden, kann dieser ausgegeben werden:

{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_cp %}
{% endhighlight %}

Somit entsteht z.B. die folgende Ausgabe: 

{% highlight cpp linenos %}
Satellite  8 has sent bit 1 (delta = 84)
Satellite 13 has sent bit 1 (delta = 595)
Satellite 19 has sent bit 0 (delta = 98)
Satellite 21 has sent bit 1 (delta = 126)
{% endhighlight %}





{% comment %} ## C {% endcomment %}
{% comment %} ### Generierung von Chipsequenzen {% endcomment %}
{% comment %} ### Dekodierung {% endcomment %}
{% comment %}{% endcomment %}
{% comment %} ## Vergleich {% endcomment %}
{% comment %} ### Zeitmessung {% endcomment %}
{% comment %}{% endcomment %}
{% comment %} ### Optimierung {% endcomment %}
{% comment %}{% endcomment %}
{% comment %} ### Finaler Vergleich {% endcomment %}
{% comment %}{% endcomment %}
{% comment %}{% endcomment %}
