---
title: Embedded Software Labor
desc: Durchlauf des Labors des Moduls "Embedded Software"
date: 2025-11-07
logo: /assets/images/HKA.png
language: de
ongoing: true
---

## Kontext

Die Aufgabe ist, einen Decoder für ein Summensignal von GPS-Daten zu schreiben. Es gibt $24$ Satelliten. Hiervon senden $4$ Satelliten jeweils ein Bit, welches als $1023$ Chips kodiert ist. Aus diesen Daten ergibt sich ein Summensignal. 

Aus dem gegebenen Summensignal soll nun zurückgerechnet werden, welche $4$ Satelliten, welche Bits gesendet haben. 

---

## Theorie

### Aufbau des Summensignals

Zu zwei Chipsequenzen $c_i, c_j$ und einem Shift $\delta$ ist das Korrelationsprodukt $\mathcal{CP}$ definiert als:

$$
    \mathcal{CP}_{ij}(\delta) := c_i \cdot (c_j \ll \delta)
$$

. Hierbei werden $c_i,c_j$ als Vektoren betrachtetist, $\cdot$ ist das Skalarprodukt und $\ll$ ist die Linksrotation.
Normanisiert man $\mathcal{CP}$, so erhält man einen Wert $\rho \in \[-1, 1\]$: den Korrelationskoeffizienten.

Durch die Generierung haben die Chipsequenzen die Eigenschaft, dass diese in der Autokorrelation -- also dem Korrelationsprodukt mit $i=j$ und $\delta = 0$ -- den Wert $n = \vert c \vert $ liefern und für ein $\delta \ne 0$ einen Wert $\epsilon \approx 0$.
Im Kreuzkorrelationsprodukt -- also dem Korrelationsprodukt mit $i \ne j$ und $\delta$ beliebig -- ergibt sich der Wert $\epsilon \approx 0$.

Will ein Satellit $S_i$ den Wert $b=1$ senden, so sendet er seine Chipsequenz $c_i$.
Will $S_i$ den Wert $b=0$ senden, so sendet er das inverse von $c_i$ (Nullen und Einsen geflippt).

Das Summensignal entsteht dadurch, dass mehrere Satelliten parallel und verschoben zueinander (asynchron) Bits -- also ihre Chipsequenzen -- senden.
Es ist also die Summe mehrerer, verschobener Chipsequenzen:

<div class="full-width-img img-theme-toggle">
    {% include lecture_data/embedded-software-lab/sumsignal_tex %}
</div>

Im Labor wird die Annahme gemacht, dass jeder der Satelliten sein gesendetes Datenbit $b \in \\{0,1\\}$ periodisch sendet.

Um die fehlenden Flächen mit Chips auszufüllen, fängt man also bei den Daten des jeweiligen Satelliten wieder an, von vorne zu lesen -- der Satellit sendet das gleiche Signal erneut.

{: .highlight-block .highlight-hint }
Alternativ kann man sich im obigem Bild auch so vorstellen, dass die Daten der Satelliten $S_1$ bis $S_4$ jeweils an sich selbst angehängt werden, sodass der rote Bereich vollständig mit Chips ausgefüllt ist.
Dann bildet man Spaltenweise die Summe und erhält das Summensignal $\mathcal{S}$.

### Dekodierung

Wie funktioniert also die Dekodierung?

Bildet man das Korrelationsprodukt aus dem Summensignal $\mathcal{S}$ und der Chipsequenz $c_i$ eines Satelliten $S_i$ bei einer Verschiebung um $\delta$, so können folgende Szenarien auftreten:

- $S_i$ war keiner der Satelliten, der Daten gesendet hat.
Somit ist $c_i \cdot \mathcal{S} \approx 0$.

- $S_i$ hat Daten gesendet, allerdings mit einer Verschiebung $\hat \delta \ne \delta$.
Also $c_i \cdot \mathcal{S} \approx 0$.

- $S_i$ hat Daten mit einer Verschiebung um $\hat \delta = \delta$ gesendet.
In diesem Fall tritt eines der folgenden Szenarien auf:
    - $S_i$ hat das Bit $b=1$ -- und somit $c_i$ -- gesendet: $c_i \cdot \mathcal{S} \approx c_i \cdot c_i = \vert c_i \vert$
    - $S_i$ hat das Bit $b=0$ -- und somit $\overline{c_i}$ -- gesendet: $c_i \cdot \mathcal{S} \approx c_i \cdot (-c_i) = - \vert c_i \vert$

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


#### Berechnung der gesendeten Bits
Für jeden Satellit -- somit für jede Chipsequenz -- wird also für jedes Offset das Korrelationsprodukt berechnet.
Wird ein "Ausschlag" gefunden, kann dieser ausgegeben werden:

{% highlight cpp linenos %}
{% include lecture_data/embedded-software-lab/cpp_cp %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
Dass die satelliten das gleiche Signal hintereinander senden wurde dadurch realisiert, dass in Zeile `19` ein Modulo-Operator (`%`) verwendet wurde, um die Daten wieder von vorne zu durchlaufen.

Somit entsteht z.B. die folgende Ausgabe: 

{% highlight cpp linenos %}
Satellite  8 has sent bit 1 (delta = 84)
Satellite 13 has sent bit 1 (delta = 595)
Satellite 19 has sent bit 0 (delta = 98)
Satellite 21 has sent bit 1 (delta = 126)
{% endhighlight %}

---

## C
Das Programm in `C` zu übersetzen ist nicht sonderlich kompliziert.
Es fallen ausschließlich einige Datenstrukturen weg.
Diese können aber leicht durch normale Arrays (pointer) ersetzt werden.

### Generierung der Chipsequenzen

Die Funktion zur Generierung von Chipsequenzen ändert sich nicht stark ab.
Anstelle der `std::bitset` Objekte werden nun `int` Arrays genutzt.
Eine Änderung ist, dass somit keine Bitoperationen -- und somit das Rechtsschieben -- mehr möglich sind.
Somit wird ebenfalls die Funktion `sr` (shift right) benötigt:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_sr %}
{% endhighlight %}

Die Funktion `generate_chip_sequence` sieht also wie folgt aus:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_chip_seq_gen %}
{% endhighlight %}


{: .highlight-block .highlight-hint}
Bitte nicht vergessen, den in Zeile `4` allokierten Speichers später wieder zu deallokieren...

Die Schleifen für den Aufruf von `generate_chip_sequence`, sowie die Übersetzung in Vektoren über `-1, 1` ändern sich nicht bemerkenswert ab und werden hier nicht zusätzlich erwähnt.

### Berechnung der gesendeten Bits

Auch an der Berechnung der Kreuzkorrelationsprodukte ergeben sich nicht viele Änderungen.
Hier die Schleife:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_cp %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
Dass die satelliten das gleiche Signal hintereinander senden wurde hier erneut dadurch realisiert, dass in Zeile `13` ein Modulo-Operator (`%`) verwendet wurde, um die Daten wieder von vorne zu durchlaufen.

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
Der Vergleich wird für folgende Intervalle ausgeführt:
- Generierung der Chipsequenzen
- Übersetzung der Chipsequenzen (von `0, 1` zu `-1, 1`)
- Berechnung der gesendeten Bits
- Gesamtzeit

### Zeitmessung
Im Falle von `C++` gibt `std::chrono::high_resolution_clock::now()` einen Zeitstemptel zurück.
Dieser kann an den entsprechenden Stellen eingefügt werden.
Nach dem Durchlauf der Berechnungen können die entsprechenden Differenzen gebildet werden:
{% highlight cpp linenos %}
auto gen_duration = std::chrono::duration_cast<std::chrono::microseconds>(start_translation - start_generation);
{% endhighlight %}

In `C` kann man mit `clock()` einen Zeitstempel erhalten. 
Die Zeitstempel müssen also entsprechenden abgespeichert und später die Differenz gebildet werden.
Für die Ausgabe muss man die Einheit noch umrechnen:

{% highlight c linenos %}
cpu_time_used = ((double) (start_translation - start_generation)) / CLOCKS_PER_SEC;
printf("Generation of sequence numbers took: %d microseconds.\n", (int) (cpu_time_used * 1000000));
{% endhighlight %}

{: .highlight-block .highlight-note}
Damit das Ergebnis weniger stark schwankt, wird ein Skript geschrieben, welches die Programme mehrfach -- in diesem Fall `50` Mal -- ausführt und den Mittelwert für die jeweiligen Intervalle ausgibt.

Somit ergibt sich:
{% highlight bash linenos %}
C  : gen=1.809 ms, translate=0.099 ms, cp=39.351 ms,  total=41.260 ms
C++: gen=3.442 ms, translate=0.411 ms, cp=126.900 ms, total=130.754 ms
{% endhighlight %}

{: .highlight-block .highlight-important }
In der Gesamtzeit ist `C` also um einen Faktor von **3.17** schneller als `C++`.

### Optimierung durch Compiler-Flags

Für die Kompilierung der Programme wurden `gcc` und `g++` genutzt.
Diese haben unterschiedliche Optimierungsstufen: `-O0, -O1, -O2` und `-O3`.
Diese optimieren zunehmen auf Geschwindigkeit.

Der Standardwert beider Compiler ist `-O0`.
Bei den oben gelisteten Ergebnissen handelt es sich also um nicht optimierte Progreamme.

Die Frage ist jetzt also: wie verhalten sich die Laufzeiten des `C`- bzw. `C++`-Progamms über die unterschiedlichen Optimierungsstufen hinweg.

Da die benötigte Zeit von Durchlauf zu Durchlauf stark variieren kann, ist es besser, nicht eine Messung pro Programm pro Optimierungsstufe durchzuführen, sondern den Mittelwert mehrerer Ausführungen zu bilden.

#### Skript zur automatisierung des Vergleichs
Da es keinen Spaß macht dies manuell zu tun, wird ein Python Skript geschrieben, welches ...

- beide Varianten des Programms (`C` und `C++`) in den unterschiedlichen Optimierungsstufen kompiliert
- die Ausgaben bezüglich der Laufzeit der Programme speichert
- die Mittelwerte berechnet
- das Ergebnis plottet

{: .text-small }
**Das Skript:**

{% highlight python linenos %}
{% include lecture_data/embedded-software-lab/time_benchmark_script %}
{% endhighlight %}

#### Zwischenergebnisse

Die Ausgabe des Skripts ist wie folgt:

{% highlight python linenos %}
{% include lecture_data/embedded-software-lab/comp_1 %}
{% endhighlight %}

Die jeweils ersten Zeilen sind bereits von vorher bekannt.
Die Faktoren bezüglich der Gesamtzeiten für die Optimierungsstufen sind: 
- `-O0:` **3.169**
- `-O1:` **1.089**
- `-O2:` **0.977**
- `-O3:` **1.005**

Der erstellte Plot:

<div class="full-width-img img-theme-toggle">
    <img src="{{ '/assets/images/decoder_timing_comp_1.png' | relative_url }}"
         alt="Time comparison plot">
</div>

{: .highlight-block .highlight-important }
**Fazit:** Ab der Optimierungsstufe `-O1` ist der Unterschied zwischen `C` und `C++` vernachlässigbar.

### Code Optimierung
#### Kurze Theorie
Die Gesamtzeit ist -- wie zu erwarten war -- fast ausschließlich durch die Berechnung der Korrelationsprodukte bestimmt.
Folglich wird sich in der Code-Optimierung nur auf diesen Abschnitt bezogen.

Betrachtet man die Schleife, stellt man fest, dass diejenige Zeile, die den größten Einfluss auf die Laufzeit hat, die folgende ist (`C` Version, Zeile 14):

{% highlight c linenos %}
cp += input[j] * chip_sequences[i][(j+d) % SEQ_LEN];
{% endhighlight %}

Innerhalb dieser Zeile ist der Modulo-Operator maßgeblich am Aufwand beteiligt.
Es gilt also, diesen möglichst zu eliminieren.

Der Sinn des Modulo-Operators ist, dass man das erneute Senden der gleichen Bits realisiert -- also die Chip-Sequenz wieder von vorne durchläuft.
Verschiebt man nicht mehr die Chip-Sequenzen um ein $\delta$, sondern das Summensignal, kann man den Modulo-Operator überflüssig machen, indem man die Eingabe erneut an sich selbst anhängt.

Bisher wurden die Chips der Chipsequenzen folgendermaßen miteinander verknüpft:

<div class="full-width-img img-theme-toggle">
    {% include lecture_data/embedded-software-lab/offset_mod_tex %}
</div>

{: .highlight-block .highlight-note}
Hier ist ein Summensignal $\mathcal{S}$ und eine um $\delta$ rotierte Chipsequenz $c_i$ der Länge $10$.
Die Beschriftungen der Form $\mathcal{S}[j]$ und $c_i[k]$ zeigen an, wo sich die jeweiligen Werte befinden, damit man sieht, wie sich die Rotation um $\delta$ auswirkt.

Anstelle dessen werden sie nun, um den Modulo-Operator zu eliminieren wie folgt miteinander verknüpft:

<div class="full-width-img img-theme-toggle">
    {% include lecture_data/embedded-software-lab/offset_2S_tex %}
</div>

{: .highlight-block .highlight-note}
Achtet man auf die Indeices, die miteinander verknüpft werden, so stellt man fest, dass beide Varianten die gleichen Indices verknüpfen und somit das gleiche berechnen.

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

### Optimierung durch Compiler-Flags II


#### Zwischenergebnisse

Die Ausgabe des Skripts ist wie folgt:

{% highlight python linenos %}
{% include lecture_data/embedded-software-lab/comp_2 %}
{% endhighlight %}

Die jeweils ersten Zeilen sind bereits von vorher bekannt.
Die Faktoren bezüglich der Gesamtzeiten für die Optimierungsstufen sind: 
- `-O0:` **2.614**
- `-O1:` **0.673**
- `-O2:` **0.678**
- `-O3:` **0.684**

Der erstellte Plot:

<div class="full-width-img img-theme-toggle">
    <img src="{{ '/assets/images/decoder_timing_comp_2.png' | relative_url }}"
         alt="Time comparison plot">
</div>

{: .highlight-block .highlight-important }
**Fazit:** Ohne Compileroptimierung ist `C` deutlich schneller als `C++` (Faktor **2.614**). Sobald allerdings die Compileroptimierung eingeschaltet wird (ab `-O1`) ist **`C++` schneller als `C`** um einen Faktor von **1.474**.

### Auswertung
