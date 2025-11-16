---
title: Embedded Software Labor
desc: Durchlauf des Labors des Moduls "Embedded Software"
date: 2025-11-12
logo: /assets/images/HKA.png
language: de
ongoing: false
---

## Kontext

Die Aufgabe ist, einen Decoder für ein Summensignal von GPS-Daten zu schreiben.
Das Summensignal ist eine Folge aus $1023$ Zahlen.
Es gibt $24$ Satelliten.
Hiervon senden $4$ Satelliten jeweils ein Bit, welches als $1023$ Chips kodiert ist.
Die Satelliten senden ihre Daten asynchron.

Aus dem gegebenen Summensignal soll nun zurückgerechnet werden, welche $4$ Satelliten, welche Bits gesendet haben. 

---

## Theorie

### Aufbau des Summensignals

Eine Chipsequenz ist eine Folge aus $1023$ Bits, welche im folgenden "Chips" genannt werden, um zwischen Datenbits und Chips unterscheiden zu können.
Die Nullen einer Chipsequenz werden im folgenden als `-1` interpretiert.
Zu zwei Chipsequenzen $c_i, c_j$ und einem Shift $\delta$ ist das Korrelationsprodukt $\mathcal{CP}$ definiert als:

$$
    \mathcal{CP}_{ij}(\delta) := c_i \cdot (c_j \ll \delta)
$$

. Hierbei werden $c_i,c_j$ als Vektoren betrachtetist, $\cdot$ ist das Skalarprodukt und $c_i \ll \delta$ ist die Linksrotation con $c_i$ um den Wert $\delta$.
Normanisiert man $\mathcal{CP}$, so erhält man einen Wert $\rho \in \[-1, 1\]$: den Korrelationskoeffizienten.

Chipsequenzen sind sogenannte "[Goldfolgen](https://en.wikipedia.org/wiki/Gold_code)", welche bestimmte Eigenschaften aufweisen:
- In der Autokorrelation -- also dem Korrelationsprodukt mit $i=j$ und $\delta = 0$ -- ergeben diese den Wert $n = \vert c \vert $ und für ein $\delta \ne 0$ einen Wert $\epsilon \approx 0$.
- Im Kreuzkorrelationsprodukt -- also dem Korrelationsprodukt mit $i \ne j$ und $\delta$ beliebig -- ergibt sich der Wert $\epsilon \approx 0$.

Will ein Satellit $S_i$ das Bit $b=1$ senden, so sendet er seine Chipsequenz $c_i$.
Will $S_i$ $b=0$ senden, so sendet er das Inverse seiner Chipsequenz: $\overline{c_i}$ (Nullen und Einsen geflippt).

Das Summensignal entsteht dadurch, dass mehrere Satelliten gleichzeitig und verschoben zueinander (asynchron) Bits -- also $c_i$ oder $\overline{c_i}$ -- senden und die gleichzeitig empfangenen Chips aufsummiert werden.
Es ist also die Summe mehrerer, verschobener Chipsequenzen -- oder invertierter Chipsequenzen:

<div class="img-100 img-theme-toggle" id="sumsignal_tex">
    {% include lecture_data/embedded-software-lab/sumsignal_tex %}
</div>

{: .highlight-block .highlight-note }
Die Satelliten $S_1$ bis $S_4$, senden jeweils ein Bit.
Danach und davor werden weitere Bits gesendet.
Über einem beliebigen Bereich -- hier rot markiert -- wird jetzt spaltenweise die Summe genommen, um zum Summensignal $\mathcal{S}$ zu gelangen.

Im Labor wird die Annahme gemacht, dass jeder der Satelliten sein gesendetes Datenbit $b \in \\{0,1\\}$ periodisch sendet. In obiger Skizze wüsste man also, wie man die fehlenden Chips im roten Bereich auszufüllen hätte: man fängt einfach wieder an, die jeweilige Chipsequenz von vorne zu lesen.

{: .highlight-block .highlight-hint }
Alternativ kann man sich auch vorstellen, dass die Daten der Satelliten $S_1$ bis $S_4$ jeweils an sich selbst angehängt werden, wodurch der rote Bereich vollständig mit Chips ausgefüllt wird.

### Dekodierung

Wie kann man also aus dem Summensignal wieder zurückrechnen, welche der Satelliten welche Bits gesendet haben?

Bildet man das Korrelationsprodukt aus dem Summensignal $\mathcal{S}$ und der Chipsequenz $c_i$ eines Satelliten $S_i$ bei einer Verschiebung um $\delta$, so können folgende Szenarien auftreten:

- $S_i$ war keiner der Satelliten, der Daten gesendet hat.
Somit ist $\mathcal{CH}_{i,\mathcal{S}}(\delta) \approx 0$.

- $S_i$ hat Daten mit einer Verschiebung $\hat \delta \ne \delta$ gesendet.
Also $\mathcal{CH}_{i,\mathcal{S}}(\delta) \approx 0$.

- $S_i$ hat Daten mit einer Verschiebung um $\hat \delta = \delta$ gesendet.
In diesem Fall tritt eines der folgenden Szenarien auf:
    - $S_i$ hat das Bit $b=1$ und somit $c_i$ gesendet: $\mathcal{CH}_{i,\mathcal{S}}(\delta) \approx c_i \cdot c_i = \vert c_i \vert$
    - $S_i$ hat das Bit $b=0$ und somit $\overline{c_i}$ gesendet: $\mathcal{CH}_{i,\mathcal{S}}(\delta) \approx c_i \cdot (-c_i) = - \vert c_i \vert$

Um herauszufinden, welche Satelliten welche Bits gesendet haben muss man also pro Satellit $S_i$ und für jede Verschiebung $\delta$, $\mathcal{CP}_{i\mathcal{S}}(\delta)$ bilden und prüfen, ob ein Ausschlag in der Stärke des Korrelationsproduktes vorliegt.
Falls ein solcher Ausschlag vorliegt, hat der Satellit entweder ein Eins-Bit (positiver Ausschlag) oder ein Null-Bit (negativer Ausschlag) gesendet.

---

## C++
### Generierung der Chipsequenzen
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

Die generierte Chipsequenz für den Satelliten $1$ sieht zum Beispiel so aus:
{% highlight cpp %}
{% include lecture_data/embedded-software-lab/chip_seq_sat_1 %}
{% endhighlight %}

### Dekodierung


{: .no-toc }
#### Berechnung der gesendeten Bits
Für jeden Satellit -- somit für jede Chipsequenz -- wird also für jedes Offset das Korrelationsprodukt berechnet.
Wird ein "Ausschlag" gefunden -- in diesem Fall ein Korrelationsprodukt, welches vom Betrag her größer als `800` ist -- , kann der Satellit mit entsprechender Verschiebung $\delta$ und gesendetem Bit ausgegeben werden:

{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_cp %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
Dass die Satelliten immer wieder das gleiche Signal senden wurde dadurch realisiert, dass in Zeile `19` ein Modulo-Operator (`%`) verwendet wurde. 
Somit werden die Daten, wenn man am Ende ankommt, wieder von vorne durchlaufen.

Es entsteht z.B. die folgende Ausgabe: 

{% highlight cpp linenos %}
Satellite  8 has sent bit 1 (delta = 84)
Satellite 13 has sent bit 1 (delta = 595)
Satellite 19 has sent bit 0 (delta = 98)
Satellite 21 has sent bit 1 (delta = 126)
{% endhighlight %}

---

## C
Das Programm in `C` zu übersetzen ist nicht sonderlich kompliziert.
Es fallen ausschließlich einige Datenstrukturen weg, welche leicht durch normale Arrays (Pointer) ersetzt werden können.

### Generierung der Chipsequenzen

Die Funktion zur Generierung von Chipsequenzen ändert sich nicht stark ab.
Anstelle der `std::bitset` Objekte werden nun `int` Arrays genutzt.
Eine Änderung ist, dass somit keine Bitoperationen -- also das Rechtsschieben -- mehr möglich sind.
Es wird also ebenfalls die Funktion `sr` (*shift right*) benötigt:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_sr %}
{% endhighlight %}

Die Funktion `generate_chip_sequence` sieht also wie folgt aus:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_chip_seq_gen %}
{% endhighlight %}


{: .highlight-block .highlight-hint}
Bitte nicht vergessen, den in Zeile `4` allokierten Speichers später wieder zu deallokieren...

Die Schleifen für den Aufruf von `generate_chip_sequence`, sowie die Übersetzung in Vektoren über `-1, 1` ändern sich nicht erwähnenswert ab und werden hier nicht zusätzlich aufgeführt.

### Berechnung der gesendeten Bits

Auch an der Berechnung der Kreuzkorrelationsprodukte ergeben sich nicht viele Änderungen.
Hier die Schleife:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_cp %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
Dass die Satelliten immer wieder das gleiche Signal senden wurde auch hier dadurch realisiert, dass in Zeile `13` ein Modulo-Operator (`%`) verwendet wurde. Somit werden die Daten, wenn man am Ende ankommt, wieder von vorne durchlaufen.

Die Ausgabe ist glücklicherweise identisch:

{% highlight cpp linenos %}
Satellite  8 has sent bit 1 (delta = 84)
Satellite 13 has sent bit 1 (delta = 595)
Satellite 19 has sent bit 0 (delta = 98)
Satellite 21 has sent bit 1 (delta = 126)
{% endhighlight %}

---

## Vergleich
Nun werden die beiden Programme bezüglich des Zeitaufwandes verglichen.
Die Chipgenerierung und Übersetzung sind nicht von Interesse.
Was betrachtet wird, ist die Berechnung der Korrelationsprodukte.

### Zeitmessung
In `C++` gibt `std::chrono::high_resolution_clock::now()` einen Zeitstemptel zurück.
Vor und nach der Berechnung der Korrelationsprodukte wird also ein Zeitstemptel abgespeichert.
Dann kann die entsprechende Differenz gebildet werden:
{% highlight cpp linenos %}
auto gen_duration = std::chrono::duration_cast<std::chrono::microseconds>(start_translation - start_generation);
{% endhighlight %}

In `C` kann man mit `clock()` einen Zeitstempel erhalten. 
Es wird analog vorgegangen.
Für die Ausgabe muss man die Einheit umrechnen:

{% highlight c linenos %}
cpu_time_used = ((double) (start_translation - start_generation)) / CLOCKS_PER_SEC;
printf("Generation of sequence numbers took: %d microseconds.\n", (int) (cpu_time_used * 1000000));
{% endhighlight %}

Nun kann man die Programme beliebig oft ausführen und die Zeitdaten messen.

<div class="highlight-block highlight-important" markdown="1">
{: .text-small}
Die mittlere Ausführungszeit für die Berechnung der Korrelationsprodukte beträgt:
- **`C`:**  $\overline t = 61.692 ms$
- **`C++`:**  $\overline t = 184.398 ms$

{: .text-small}
Die `C`-Implementierung ist damit um einen Faktor von **2.989** schneller als die `C++`-Version.
</div>

{: .highlight-block .highlight-note}
Damit das Ergebnis weniger stark schwankt, werden die Programme mehrfach -- in diesem Fall `100` Mal -- ausführt und der Mittelwert gebildet.
Dies gilt auch für die Zeiten, die nachfolgend genannt werden.

### Optimierung durch Compiler-Flags

Für die Kompilierung der Programme wurden `gcc` und `g++` genutzt.
Die Compiler haben unterschiedliche Optimierungsstufen: `-O0, -O1, -O2` und `-O3`.
Diese optimieren zunehmend auf Geschwindigkeit.

Der Standardwert beider Compiler für die Optimierungsstufen ist `-O0`.
Bei den oben gelisteten Laufzeiten handelt es sich also um nicht optimierte Programme.

Es stellt sich die Frage: wie verhalten sich die Laufzeiten des `C`- bzw. `C++`-Progamms über die unterschiedlichen Optimierungsstufen hinweg.

{: .no-toc}
#### Zwischenergebnisse

Dazu werden beide Programme in den genannten Optimierungsstufen kompiliert und deren Zeiten in einer Datei notiert.

{% comment %} {: .highlight-block .highlight-warning} {% endcomment %}
{% comment %} **TODO:** weird SVG fuckup... {% endcomment %}

<div class="img-80 img-theme-toggle">
    {% include lecture_data/embedded-software-lab/interm_res_tex %}
</div>

{: .highlight-block .highlight-important }
**Fazit:** Ab der Optimierungsstufe `-O1` ist der Unterschied zwischen `C` und `C++` vernachlässigbar.

### Code Optimierung
#### Kurze Theorie
Betrachtet man die Schleife, stellt man fest, dass diejenige Zeile, die den größten Einfluss auf die Laufzeit hat, die folgende ist (`C`-Version, Zeile `13`):

{% highlight c linenos %}
cp += input[j] * chip_sequences[i][(j+d) % SEQ_LEN];
{% endhighlight %}

Was diese Zeile so aufwendig macht, ist der Modulo-Operator.
Es gilt also, diesen möglichst zu eliminieren.

Der Sinn des Modulo-Operators ist, dass man das erneute Senden der gleichen Bits realisiert -- also die Chip-Sequenz wieder von vorne durchläuft.

Dies kann auch anders realisiert werden:
Anstatt die Chip-Sequenzen um ein $\delta$ zu rotieren, kann man das Summensignal erneut an sich selbst anhängen und dann erst ab einem Offset $\delta$ das Korrelationsprodukt bilden.

Bisher wurden die Chipsequenzen und das Summensignal folgendermaßen miteinander verknüpft:

<div class="img-100 img-theme-toggle">
    {% include lecture_data/embedded-software-lab/offset_mod_tex %}
</div>

{: .highlight-block .highlight-note }
Das Summensignal $\mathcal{S}$ und eine um $\delta$ nach rechts rotierte Chipsequenz $c_i$ der Länge $10$.
Verknüpft werden also $c_i[0]$ bis $c_i[6]$ mit $\mathcal{S}[3]$ bis $\mathcal{S}[9]$ und $c_i[7]$ bis $c_i[9]$ mit $\mathcal{S}[0]$ bis $\mathcal{S}[3]$.

Anstelle dessen wird das Korrelationsprodukt nun wie folgt gebildet:

{% comment %} {: .highlight-block .highlight-warning} {% endcomment %}
{% comment %} **TODO:** weird SVG fuckup... and "Abbildung" missing {% endcomment %}

<div class="img-100 img-theme-toggle">
    {% include lecture_data/embedded-software-lab/offset_2S_tex %}
</div>

{: .highlight-block .highlight-note }
Das Summensignal $\mathcal{S}$ wurde an sich selbst angehängt.
Die Verknüpfung von $c_i$ und $\mathcal{S}$ findet jetzt erst ab einem Offset $\delta$ statt.
Das Wichtige: Verknüpft werden immer noch $c_i[0]$ bis $c_i[6]$ mit $\mathcal{S}[3]$ bis $\mathcal{S}[9]$ und $c_i[7]$ bis $c_i[9]$ mit $\mathcal{S}[0]$ bis $\mathcal{S}[3]$.

#### Optimierte Implementierung
Hier die optimierte Schleife in `C++`:

{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_optimized_cp %}
{% endhighlight %}

Hierbei ändern sich zwei Dinge: 
- der Modulo-Operator wurde entfernt indem der Offset $\delta$ nun auf das Summensignal gegeben wird. 
- Dadurch, dass der Offset nun auf das Summensignal und nicht auf die Chipsequenz gerechnet wird, muss beim Speichern des Offsets nicht `d`, sondern `SEQ_LEN - d` gespeichert werden.

Und hier die optimierte Schleife in `C`:

{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/c_optimized_cp %}
{% endhighlight %}

Die Änderungen sind analog zu denjenigen in `C++`.

### Optimierung durch Compiler-Flags II: Ergebnisse

<div class="img-80 img-theme-toggle">
    {% include lecture_data/embedded-software-lab/results_table_opt_tex %}
</div>

{: .highlight-block .highlight-important }
**Fazit:** Die Ergebnisse unterscheiden sich im Verhältlnis nicht sonderlich von denjenigen ohne Code-Optimierung: `C` ist deutlich schneller als `C++`, solange man keine Compiler Optimierung nutzt.
Sobald diese genutzt wird, sind `C` und `C++` quasi gleich schnell.

Eine Frage gibt es noch:
Um welchen Faktor haben sich die Programme durch die Code-Optimierung bei den jeweiligen Optimierungsstufen verbessert?

Im Falle von `C` hat sich folgendes ergeben:

<div class="img-80 img-theme-toggle">
    {% include lecture_data/embedded-software-lab/results_C_improv_tex %}
</div>

Bei `C++` sieht es wie folgt aus:

<div class="img-80 img-theme-toggle">
    {% include lecture_data/embedded-software-lab/results_Cpp_improv_tex %}
</div>

{: .highlight-block .highlight-important }
**Fazit:** Die Code-Optimierung ohne Compiler-Optimierung bringt also bei `C++` eine Verbesserung um $13\%$ und bei `C` um $30\%$.
Dies ist bereits substantiell.
Interessant ist allerdings, dass die Verbeserung erst richtig zu tragen kommt, wenn dazu noch eine Compiler-Optimierung verwendet wird.
Hierdurch erreicht man bei `C++` Verbesserungen von bis zu $82\%$ und bei `C` bis zu $83\%$.

## Anhang

<p class="text-small mt-1">
<a href="/data/C_Cpp_Comparison.csv">Download .csv file</a>
</p>
