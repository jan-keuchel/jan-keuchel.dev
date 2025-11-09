---
title: Embedded Software Labor
desc: Durchlauf des Labors des Moduls "Embedded Software"
date: 2025-11-07
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

---
 
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

<div class="full-width-img img-theme-toggle">
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

---

## C
Das Programm in `C` zu übersetzen ist nicht sonderlich kompliziert.
Es fallen ausschließlich einige Datenstrukturen weg.
Diese können aber leicht durch normale Arrays (pointer) ersetzt werden.

### Generierung von Chipsequenzen

Die Funktion zur Generierung von Chipsequenzen ändert sich nicht stark ab.
Anstelle der `std::bitset` Objekte werden nun `short` Arrays genutzt.
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
Bitte nicht das Deallokieren des in Zeile `4` allokierten Speichers vergessen...

Die Schleifen für den Aufruf von `generate_chip_sequence`, sowie die Übersetzung in Vektoren über `-1, 1` ändern sich nicht bemerkenswert ab.

### Dekodierung

Auch an der Berechnung des Kreuzkorrelationsproduktes ergeben sich nicht viele Änderungen.
Hier die Schleife:

{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_cp %}
{% endhighlight %}

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

Hieraus ergibt sich ...

**...für `C`:**
{% highlight bash linenos %}
./c_decoder input
Generation of sequence numbers took: 2583 microseconds.
Translation of sequence numbers took: 158 microseconds.
cp calculation took: 47172 microseconds.
Total: 49913 microseconds.
{% endhighlight %}

**...für `C++`:**
{% highlight bash linenos %}
./p_decoder input
Generation of sequence numbers took: 5490 microseconds.
Translation of sequence numbers took: 639 microseconds.
cp calculation took: 202245 microseconds.
Total: 208375 microseconds.
{% endhighlight %}

`C` ist in diesem Fall also insgesamt ca. 4 mal so Schnell wie `C++`.

### Optimierung
Die Operation, die am aufwendigsten ist, ist der Modulo-Operator (`%`) in der Schleife, welche das Korrelationsprodukt berechnet.
Es gilt also, diesen Operator wenn möglich zu eliminieren.
In diesem Fall dient er dazu, dass der Index, wenn dieser am Ende des Arrays ankommt, wieder an den Anfang gesetzt wird, sodass kein `IndexOutOfBounds` auftritt.

Dies kann auch anders erreicht werden:
Anstatt ein Array der Länge $n$ zu haben, welches von einem Offset $\delta$ aus traversiert wird -- und somit jeden Iterationsschritt sichergestellt werden muss, dass man nicht "aus der Begrenzung" läuft --, kann man das Array zu Beginn an sich selbst anhängen und somit auf einem Array der Länge $2n$ operieren.
Somit ist es bei einer Schleife, welche $n$ Iterationen durchläuft und einem Offset, welcher maximal $n$ ist, nicht möglich "out of bounds" zu geraten.

Somit ergibt sich die folgende Schleife:
{% highlight c linenos %}
{% include lecture_data/embedded-software-lab/c_optimized_cp %}
{% endhighlight %}

{: .highlight-block .highlight-hint}
Da der Offset $\delta$ nun nicht mehr in die Chipsequenz, sondern in den Input gegeben wird, muss bei der Berechnung von `delta` in den Zeilen 19 bzw. 22 nicht einfach $\delta$ abgespeichert werden, sondern `SEQ_LEN - d`

Gleiches wird im `C++` code vorgenommen.

Die Verbesserung in der Berechnungszeit ist enttäuschend gering bzw. aussagekräftig:

**`C`:**
{% highlight bash linenos %}
./c_decoder input
Generation of sequence numbers took: 2780 microseconds.
Translation of sequence numbers took: 159 microseconds.
cp calculation took: 46917 microseconds.
Total: 49856 microseconds.
{% endhighlight %}

**`C++`:**
{% highlight bash linenos %}
./p_decoder input
Generation of sequence numbers took: 5391 microseconds.
Translation of sequence numbers took: 660 microseconds.
cp calculation took: 187002 microseconds.
Total: 193054 microseconds.
{% endhighlight %}

### Compiler Flags
Beim Compilieren der Programme kann eine Optimierung verwendet werden.
Diese reicht von `-O0` (default Wert) bis `-O3`.

Es werden nun also beide Programme mit allen Optimierungsleveln compiliert und die Zeitwerte verglichen.

#### Skript zur automatisierung des Vergleichs
Da es keinen Spaß macht, dies manuell zu tun -- bzw. es mehr Spaß macht, ein Skript zu schreiben, welches dieses automatisiert tut und die ergebnisse plottet -- wird ein Python Skript geschrieben, welches einem die Arbeit abnimmt:

{% highlight python linenos %}
{% include lecture_data/embedded-software-lab/time_benchmark_script %}
{% endhighlight %}

### Finaler Vergleich

Die Ausgabe auf der Kommandozeile:

{% highlight bash linenos %}
python time_benchmark.py

--- C ---
C -O0: generation=2.895 ms, translation=0.159 ms, correlational product=46.708 ms, total=49.761 ms
C -O1: generation=0.275 ms, translation=0.014 ms, correlational product=18.454 ms, total=18.743 ms
C -O2: generation=0.328 ms, translation=0.016 ms, correlational product=7.446 ms, total=7.791 ms
C -O3: generation=0.279 ms, translation=0.004 ms, correlational product=7.384 ms, total=7.666 ms

--- C++ ---
C++ -O0: generation=4.771 ms, translation=0.587 ms, correlational product=162.087 ms, total=167.445 ms
C++ -O1: generation=0.139 ms, translation=0.047 ms, correlational product=6.108 ms, total=6.295 ms
C++ -O2: generation=0.085 ms, translation=0.060 ms, correlational product=4.000 ms, total=4.146 ms
C++ -O3: generation=0.079 ms, translation=0.052 ms, correlational product=3.924 ms, total=4.055 ms
{% endhighlight %}

Der Plot:

<div class="full-width-img img-theme-toggle">
    <img src="{{ '/assets/images/decoder_timing_comparison.png' | relative_url }}"
         alt="Time comparison plot">
</div>

Hierbei stellt man interessanter Weise fest: 

**`C++` ist in diesem Fall schneller als `C`**, sobald man die Optimierungsflags des Compilers verwendet!
