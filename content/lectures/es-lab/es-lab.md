---
title: "Embedded Software Labor"
date: 2025-11-12
summary: "Durchlauf des Labors des Modules \"Embedded Software\""
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

. Hierbei werden $c_i,c_j$ als Vektoren betrachtet, $\cdot$ ist das Skalarprodukt und $c_i \ll \delta$ ist die Linksrotation von $c_i$ um den Wert $\delta$.
Normalisiert man $\mathcal{CP}$, so erhält man einen Wert $\rho \in [-1, 1]$: den Korrelationskoeffizienten.

Chipsequenzen sind sogenannte "[Goldfolgen](https://en.wikipedia.org/wiki/Gold_code)", welche bestimmte Eigenschaften aufweisen:
- In der Autokorrelation -- also dem Korrelationsprodukt mit $i=j$ und $\delta = 0$ -- ergeben diese den Wert $n = \vert c \vert $ und für ein $\delta \ne 0$ einen Wert $\epsilon \approx 0$.
- Im Kreuzkorrelationsprodukt -- also dem Korrelationsprodukt mit $i \ne j$ und $\delta$ beliebig -- ergibt sich der Wert $\epsilon \approx 0$.

Will ein Satellit $S_i$ das Bit $b=1$ senden, so sendet er seine Chipsequenz $c_i$.
Will $S_i$ $b=0$ senden, so sendet er das Inverse seiner Chipsequenz: $\overline{c_i}$ (Nullen und Einsen geflippt).

Das Summensignal entsteht dadurch, dass mehrere Satelliten gleichzeitig und verschoben zueinander (asynchron) Bits -- also $c_i$ oder $\overline{c_i}$ -- senden und die gleichzeitig empfangenen Chips aufsummiert werden.
Es ist also die Summe mehrerer, verschobener Chipsequenzen -- oder invertierter Chipsequenzen:

{{< svg "lectures/es-lab/images/sumsignal_tex" >}}

<div class="highlight-block highlight-note">
Die Satelliten $S_1$ bis $S_4$, senden jeweils ein Bit.
Danach und davor werden weitere Bits gesendet.
Über einem beliebigen Bereich - hier rot markiert - wird jetzt spaltenweise die Summe genommen, um zum Summensignal $\mathcal{S}$ zu gelangen.
</div>

Im Labor wird die Annahme gemacht, dass jeder der Satelliten sein gesendetes Datenbit $b \in \\{0,1\\}$ periodisch sendet. In obiger Skizze wüsste man also, wie man die fehlenden Chips im roten Bereich auszufüllen hätte: man fängt einfach wieder an, die jeweilige Chipsequenz von vorne zu lesen.

<div class="highlight-block highlight-hint">
Alternativ kann man sich auch vorstellen, dass die Daten der Satelliten $S_1$ bis $S_4$ jeweils an sich selbst angehängt werden, wodurch der rote Bereich vollständig mit Chips ausgefüllt wird.
</div>

### Dekodierung

Wie kann man also aus dem Summensignal wieder zurückrechnen, welche der Satelliten welche Bits gesendet haben?

Bildet man das Korrelationsprodukt aus dem Summensignal $\mathcal{S}$ und der Chipsequenz $c_i$ eines Satelliten $S_i$ bei einer Verschiebung um $\delta$, so können folgende Szenarien auftreten:

- $S_i$ war keiner der Satelliten, der Daten gesendet hat.
Somit ist $\mathcal{CP}_{i,\mathcal{S}}(\delta) \approx 0$.

- $S_i$ hat Daten mit einer Verschiebung $\hat \delta \ne \delta$ gesendet.
Also $\mathcal{CP}_{i,\mathcal{S}}(\delta) \approx 0$.

- $S_i$ hat Daten mit einer Verschiebung um $\hat \delta = \delta$ gesendet.
In diesem Fall tritt eines der folgenden Szenarien auf:
    - $S_i$ hat das Bit $b=1$ und somit $c_i$ gesendet: $\mathcal{CP}_{i,\mathcal{S}}(\delta) \approx c_i \cdot c_i = \vert c_i \vert$
    - $S_i$ hat das Bit $b=0$ und somit $\overline{c_i}$ gesendet: $\mathcal{CP}_{i,\mathcal{S}}(\delta) \approx c_i \cdot (-c_i) = - \vert c_i \vert$

Um herauszufinden, welche Satelliten welche Bits gesendet haben muss man also pro Satellit $S_i$ und für jede Verschiebung $\delta$, $\mathcal{CP}_{i\mathcal{S}}(\delta)$ bilden und prüfen, ob ein Ausschlag in der Stärke des Korrelationsproduktes vorliegt.
Falls ein solcher Ausschlag vorliegt, hat der Satellit entweder ein Eins-Bit (positiver Ausschlag) oder ein Null-Bit (negativer Ausschlag) gesendet.

---

## C++
### Generierung der Chipsequenzen
Um das Summensignal dekodieren zu können, benötigt man die Chipsequenzen.
Die Verknüpfungskonfigurationen der Register waren auf dem Übungsblatt gegeben.

Hier die Funktion `generate_chip_seq`, welche die Chipsequenz eines Satelliten basierend auf der Konfiguration der Register generiert.

```cpp {linenos=inline}
std::bitset<SEQ_LEN> generate_chip_seq(std::array<int, 2> reg_sum) {
    // Initialize bit sets with all 1.
    std::bitset<10> a_reg_state;
    std::bitset<10> b_reg_state;
    a_reg_state.set();
    b_reg_state.set();

    // Chip sequence
    std::bitset<SEQ_LEN> code;

    bool a_new_lmb;
    bool b_new_lmb;
    bool code_bit;
    for (int i = 0; i < SEQ_LEN; i++) {
        // Update chip sequence
        code_bit =  a_reg_state[0] ^ 
                    b_reg_state[10 - reg_sum[0]] ^ 
                    b_reg_state[10 - reg_sum[1]];
        code[i] = code_bit;

        // Calculate new LMB
        a_new_lmb = a_reg_state[0] ^ a_reg_state[7];
        b_new_lmb = b_reg_state[0] ^ b_reg_state[1] ^ b_reg_state[2] ^
                    b_reg_state[4] ^ b_reg_state[7] ^ b_reg_state[8];

        // Right shift for rotation
        a_reg_state >>= 1;
        b_reg_state >>= 1;

        // Insert new bit
        a_reg_state[9] = a_new_lmb;
        b_reg_state[9] = b_new_lmb;
    }

    return code;
}
```

Mit Hilfe dieser Funktion werden nun die Chipsequenzen generiert

```cpp {linenos=inline}
int main(int argc, char *argv[]) {

    // [...]

    // Gegebene Daten vom Übungsblatt
    std::array<std::array<int, 2>, 24> register_sums = {{
        {2, 6}, {3, 7}, {4, 8}, {5, 9}, {1, 9}, {2, 10}, 
        {1, 8}, {2, 9}, {3, 10}, {2, 3}, {3, 4}, {5, 6},
        {6, 7}, {7, 8}, {8, 9}, {9, 10}, {1, 4}, {2, 5},
        {3, 6}, {4, 7}, {5, 8}, {6, 9}, {1, 3}, {4, 6},
    }};

    std::array<std::bitset<SEQ_LEN>, 24> chip_sequences;
    for (size_t i = 0; i < register_sums.size(); i++) {
        chip_sequences[i] = generate_chip_seq(register_sums[i]);
    }

}
```

und dann in Vektoren über `-1, 1` übersetzt:

```cpp {linenos=inline}
std::array<int, SEQ_LEN> translate_bitset_to_arr(std::bitset<SEQ_LEN> bs) {
    std::array<int, SEQ_LEN> arr;
    for (size_t i = 0; i < bs.size(); i++) {
        arr[i] = bs[i] ? 1 : -1;
    }

    return arr;
}

// [...]

int main(int argc, char *argv[]) {

    // [...]

    std::array<std::bitset<SEQ_LEN>, 24> chip_sequences;
    for (size_t i = 0; i < register_sums.size(); i++) {
        chip_sequences[i] = generate_chip_seq(register_sums[i]);
    }

}
```

Die generierte Chipsequenz für den Satelliten $1$ sieht zum Beispiel so aus:
```cpp
1 1 -1 -1 1 -1 -1 -1 -1 -1 1 1 1 -1 -1 1 -1 1 -1 -1 1 -1 -1 1 1 1 1 -1 -1 1 -1 1 -1 -1 -1 1 -1 -1 1 1 1 1 1 -1 1 -1 1 -1 1 1 -1 1 -1 -1 -1 1 -1 -1 -1 1 -1 1 -1 1 -1 1 -1 1 1 -1 -1 1 -1 -1 -1 1 1 1 1 -1 1 -1 -1 1 1 1 1 1 1 -1 1 1 -1 1 1 1 -1 -1 1 1 -1 1 1 1 1 1 -1 -1 1 -1 1 -1 1 -1 1 -1 -1 -1 -1 1 -1 -1 -1 -1 -1 -1 -1 -1 1 1 1 -1 1 -1 1 -1 -1 1 -1 -1 -1 1 -1 -1 1 1 -1 1 1 1 1 -1 -1 -1 -1 -1 1 1 1 1 -1 1 -1 1 1 1 -1 -1 1 1 -1 -1 1 1 1 1 -1 1 1 -1 -1 -1 -1 -1 -1 -1 1 -1 1 1 1 1 -1 -1 1 1 1 1 1 -1 1 -1 1 -1 -1 1 1 -1 -1 -1 1 -1 1 1 -1 1 1 1 -1 -1 -1 1 1 -1 1 1 1 1 -1 1 -1 1 -1 -1 -1 1 -1 1 -1 1 1 -1 -1 -1 -1 -1 1 -1 -1 -1 -1 -1 -1 -1 -1 1 -1 -1 -1 -1 -1 -1 1 1 -1 -1 -1 1 1 1 -1 1 1 -1 -1 -1 -1 -1 -1 1 1 1 -1 -1 -1 1 1 -1 1 1 1 1 1 1 1 1 1 -1 1 -1 -1 1 1 1 -1 1 -1 -1 1 -1 1 1 -1 1 1 -1 -1 -1 -1 1 -1 1 -1 1 -1 1 1 -1 -1 -1 1 -1 -1 1 1 1 -1 -1 1 -1 1 1 -1 1 1 1 -1 1 1 -1 -1 -1 1 1 1 -1 1 1 1 -1 1 1 1 1 -1 -1 -1 -1 1 1 -1 1 1 -1 -1 -1 -1 1 1 -1 -1 1 -1 -1 1 -1 -1 1 -1 -1 -1 -1 -1 1 1 -1 1 1 -1 1 -1 -1 1 -1 1 1 -1 1 1 1 1 -1 -1 -1 1 -1 1 1 1 -1 -1 -1 -1 -1 -1 1 -1 1 -1 -1 1 -1 -1 1 1 1 1 1 1 -1 -1 -1 -1 -1 1 -1 1 -1 1 -1 1 1 1 -1 -1 1 1 1 1 1 -1 1 -1 1 1 1 1 1 -1 -1 1 1 -1 -1 1 1 -1 -1 -1 1 1 1 -1 -1 -1 1 1 -1 1 1 -1 1 -1 1 -1 1 -1 1 1 -1 1 1 -1 -1 -1 1 1 -1 1 1 1 -1 1 1 1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 1 -1 1 1 -1 -1 1 1 -1 1 1 -1 -1 1 1 1 -1 1 1 -1 1 -1 -1 -1 -1 -1 1 -1 1 -1 1 -1 1 1 1 -1 1 -1 1 1 1 -1 1 -1 -1 1 -1 1 -1 -1 -1 1 1 1 -1 -1 1 1 1 -1 -1 -1 1 -1 -1 1 -1 1 -1 -1 -1 1 -1 1 -1 -1 1 -1 1 1 -1 1 -1 -1 -1 -1 1 -1 1 -1 1 1 -1 1 1 -1 1 -1 1 1 -1 1 1 -1 -1 -1 1 1 1 -1 -1 1 1 1 1 -1 1 1 -1 -1 1 -1 -1 -1 -1 1 1 1 1 1 1 -1 -1 1 -1 1 1 -1 1 -1 -1 -1 1 -1 -1 -1 -1 1 1 1 1 1 -1 1 -1 1 -1 1 1 1 -1 -1 1 1 -1 -1 1 -1 -1 1 -1 -1 1 -1 -1 1 -1 1 1 1 1 1 1 1 1 1 1 -1 -1 -1 -1 1 1 1 1 1 -1 1 1 1 1 -1 -1 -1 1 1 -1 1 1 1 -1 -1 1 -1 1 1 -1 -1 -1 -1 1 1 1 -1 -1 1 -1 1 -1 1 -1 -1 -1 -1 1 -1 1 -1 -1 1 -1 1 -1 1 1 1 1 1 1 -1 -1 -1 1 1 1 1 -1 1 1 -1 1 -1 -1 1 1 1 -1 1 1 -1 -1 1 1 1 1 1 1 -1 1 1 1 1 1 -1 1 -1 -1 -1 1 1 -1 -1 -1 1 1 1 1 1 -1 -1 -1 -1 -1 -1 -1 1 -1 -1 1 -1 1 -1 -1 -1 1 -1 1 1 -1 1 -1 -1 -1 1 -1 -1 -1 1 -1 -1 1 1 -1 1 1 -1 -1 -1 -1 -1 -1 1 1 1 -1 1 1 -1 1 -1 -1 -1 1 1 -1 1 -1 -1 -1 1 -1 -1 1 -1 -1 -1 1 1 1 -1 -1 -1 1 -1 1 1 -1 -1 1 1 -1 -1 1 -1 -1 1 1 1 1 -1 -1 1 1 -1 1 1 1 1 1 1 -1 -1 1 1 -1 -1 1 -1 1 -1 -1 1 1 -1 1 -1 -1 1 1 -1 1 -1 1 1 1 1 -1 -1 1 1 -1 1 1 -1 1 -1 1 -1 -1 1 1 1 -1 1 1 1 1 -1 -1 -1 1 1
```

### Dekodierung
Für jeden Satellit -- somit für jede Chipsequenz -- wird also für jedes Offset das Korrelationsprodukt berechnet.
Wird ein "Ausschlag" gefunden -- in diesem Fall ein Korrelationsprodukt, welches vom Betrag her größer als `800` ist -- , kann der Satellit mit entsprechender Verschiebung $\delta$ und gesendetem Bit ausgegeben werden:

```cpp {linenos=inline}
int main(int argc, char *argv[]) {

    // [...]

    int correlation_product = 0;
    int delta = 0;
    int bit = 0;
    // For each satellite...
    for (size_t i = 0; i < chip_vectors.size(); i++) {

        delta = -1;
        bit = -1;

        // Test every offset delta...
        for (int d = 0; d < SEQ_LEN; d++) {
            correlation_product = 0;
            // ... and calculate the CP.
            for (int j = 0; j < SEQ_LEN; j++) {
                correlation_product += input[j] * chip_vectors[i][(j+d) % SEQ_LEN];
            }

            if (correlation_product > 800) {
                bit = 1;
                delta = d;
            } else if (correlation_product < -800) {
                bit = 0;
                delta = d;
            } 
        }

        if (bit != -1) {
            printf("Satellite %2d has sent bit %d (delta = %d)\n", (int)(i+1), bit, delta);
        }
    }

    // [...]

}
```

<div class="highlight-block highlight-hint">

Dass die Satelliten immer wieder das gleiche Signal senden wurde dadurch realisiert, dass in Zeile `19` ein Modulo-Operator (`%`) verwendet wurde. 
Somit werden die Daten, wenn man am Ende ankommt, wieder von vorne durchlaufen.
</div>

Es entsteht z.B. die folgende Ausgabe: 

``` cpp {linenos=inline}
Satellite  8 has sent bit 1 (delta = 84)
Satellite 13 has sent bit 1 (delta = 595)
Satellite 19 has sent bit 0 (delta = 98)
Satellite 21 has sent bit 1 (delta = 126)
```

---

## C
Das Programm in `C` zu übersetzen ist nicht sonderlich kompliziert.
Es fallen ausschließlich einige Datenstrukturen weg, welche leicht durch normale Arrays (Pointer) ersetzt werden können.

### Generierung der Chipsequenzen

Die Funktion zur Generierung von Chipsequenzen ändert sich nicht stark ab.
Anstelle der `std::bitset` Objekte werden nun `int` Arrays genutzt.
Eine Änderung ist, dass somit keine Bitoperationen -- also das Rechtsschieben -- mehr möglich sind.
Es wird also ebenfalls die Funktion `sr` (*shift right*) benötigt:

```C {linenos=inline}
void sr(int *x) {
    for (int i = 0; i < 9; i++) {
        x[i] = x[i+1]; 
    }
    x[9] = 0;
}
```

Die Funktion `generate_chip_sequence` sieht also wie folgt aus:

```C {linenos=inline hl_lines=4}
int *generate_chip_sequence(int reg_sum[2]) {
    int a[10] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
    int b[10] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1};
    int *code = (int *)calloc(SEQ_LEN, sizeof(int));

    int a_new_lmb;
    int b_new_lmb;
    int code_bit;
    
    for (int i = 0; i < SEQ_LEN; i++) {
        // Update code
        code_bit = a[0] ^ b[10 - reg_sum[0]] ^ b[10 - reg_sum[1]];
        code[i] = code_bit;

        // Calculate new LMB
        a_new_lmb = a[0] ^ a[7];
        b_new_lmb = b[0] ^ b[1] ^ b[2] ^ b[4] ^ b[7] ^ b[8];

        // Shift
        sr(a);
        sr(b);

        a[9] = a_new_lmb;
        b[9] = b_new_lmb;
    }

    return code;
}
```


<div class="highlight-block highlight-hint">

Bitte nicht vergessen, den in Zeile `4` allokierten Speichers später wieder zu deallokieren...
</div>

Die Schleifen für den Aufruf von `generate_chip_sequence`, sowie die Übersetzung in Vektoren über `-1, 1` ändern sich nicht erwähnenswert ab und werden hier nicht zusätzlich aufgeführt.

### Dekodierung

Auch an der Berechnung der Kreuzkorrelationsprodukte ergeben sich nicht viele Änderungen.
Hier die Schleife:

```c {linenos=inline}
int cp = 0;
int delta = 0;
int bit = 0;

for (int i = 0; i < NUM_SAT; i++) {
    delta = -1;
    bit = -1;

    for (int d = 0; d < SEQ_LEN; d++) {
        cp = 0;

        for (int j = 0; j < SEQ_LEN; j++) {
            cp += input[j] * chip_sequences[i][(j+d) % SEQ_LEN];
        }

        if (cp > 800) {
            bit = 1;
            delta = d;
        } else if (cp < -800) {
            bit = 0;
            delta = d;
        } 

    }

    if (bit != -1) {
        printf("Satellite %2d has sent bit %d (delta = %d)\n", i+1, bit, delta);
    }
}
```

<div class="highlight-block highlight-hint">

Dass die Satelliten immer wieder das gleiche Signal senden wurde auch hier dadurch realisiert, dass in Zeile `13` ein Modulo-Operator (`%`) verwendet wurde. Somit werden die Daten, wenn man am Ende ankommt, wieder von vorne durchlaufen.
</div>

Die Ausgabe ist glücklicherweise identisch:

```C {linenos=inline}
Satellite  8 has sent bit 1 (delta = 84)
Satellite 13 has sent bit 1 (delta = 595)
Satellite 19 has sent bit 0 (delta = 98)
Satellite 21 has sent bit 1 (delta = 126)
```

---

## Vergleich
Nun werden die beiden Programme bezüglich des Zeitaufwandes verglichen.
Die Chipgenerierung und Übersetzung sind nicht von Interesse.
Was betrachtet wird, ist die Berechnung der Korrelationsprodukte.

### Zeitmessung
In `C++` gibt `std::chrono::high_resolution_clock::now()` einen Zeitstemptel zurück.
Vor und nach der Berechnung der Korrelationsprodukte wird also ein Zeitstemptel abgespeichert.
Dann kann die entsprechende Differenz gebildet werden:

```cpp {linenos=inline}
auto gen_duration = std::chrono::duration_cast<std::chrono::microseconds>(start_translation - start_generation);
```

In `C` kann man mit `clock()` einen Zeitstempel erhalten. 
Es wird analog vorgegangen.
Für die Ausgabe muss man die Einheit umrechnen:

```c {linenos=inline}
cpu_time_used = ((double) (start_translation - start_generation)) / CLOCKS_PER_SEC;
printf("Generation of sequence numbers took: %d microseconds.\n", (int) (cpu_time_used * 1000000));
```

Nun kann man die Programme beliebig oft ausführen und die Zeitdaten messen.

<div class="highlight-block highlight-important">

Die mittlere Ausführungszeit für die Berechnung der Korrelationsprodukte beträgt:
- **`C`:**  $\overline t = 61.692 ms$
- **`C++`:**  $\overline t = 184.398 ms$

Die `C`-Implementierung ist damit um einen Faktor von **2.989** schneller als die `C++`-Version.
</div>

<div class="highlight-block highlight-note">

Damit das Ergebnis weniger stark schwankt, werden die Programme mehrfach -- in diesem Fall `100` Mal -- ausführt und der Mittelwert gebildet.
Dies gilt auch für die Zeiten, die nachfolgend genannt werden.

</div>

### Optimierung durch Compiler-Flags

Für die Kompilierung der Programme wurden `gcc` und `g++` genutzt.
Die Compiler haben unterschiedliche Optimierungsstufen: `-O0, -O1, -O2` und `-O3`.
Diese optimieren zunehmend auf Geschwindigkeit.

Der Standardwert beider Compiler für die Optimierungsstufen ist `-O0`.
Bei den oben gelisteten Laufzeiten handelt es sich also um nicht optimierte Programme.

Es stellt sich die Frage: wie verhalten sich die Laufzeiten des `C`- bzw. `C++`-Progamms über die unterschiedlichen Optimierungsstufen hinweg.

#### Zwischenergebnisse

Dazu werden beide Programme in den genannten Optimierungsstufen kompiliert und deren Zeiten in einer Datei notiert.

{{< svg "lectures/es-lab/images/interm_res_tex" >}}

<div class="highlight-block highlight-important">

**Fazit:** Ab der Optimierungsstufe `-O1` ist der Unterschied zwischen `C` und `C++` vernachlässigbar.

</div>

### Code Optimierung
#### Kurze Theorie
Betrachtet man die Schleife, stellt man fest, dass diejenige Zeile, die den größten Einfluss auf die Laufzeit hat, die folgende ist (`C`-Version, Zeile `13`):

```C {linenos=inline}
cp += input[j] * chip_sequences[i][(j+d) % SEQ_LEN];
```

Was diese Zeile so aufwendig macht, ist der Modulo-Operator.
Es gilt also, diesen möglichst zu eliminieren.

Der Sinn des Modulo-Operators ist, dass man das erneute Senden der gleichen Bits realisiert -- also die Chip-Sequenz wieder von vorne durchläuft.

Dies kann auch anders realisiert werden:
Anstatt die Chip-Sequenzen um ein $\delta$ zu rotieren, kann man das Summensignal erneut an sich selbst anhängen und dann erst ab einem Offset $\delta$ das Korrelationsprodukt bilden.

Bisher wurden die Chipsequenzen und das Summensignal folgendermaßen miteinander verknüpft:

{{< svg "lectures/es-lab/images/offset_mod_tex" >}}

<div class="highlight-block highlight-note">

Das Summensignal $\mathcal{S}$ und eine um $\delta$ nach rechts rotierte Chipsequenz $c_i$ der Länge $10$.
Verknüpft werden also $c_i[0]$ bis $c_i[6]$ mit $\mathcal{S}[3]$ bis $\mathcal{S}[9]$ und $c_i[7]$ bis $c_i[9]$ mit $\mathcal{S}[0]$ bis $\mathcal{S}[3]$.

</div>

Anstelle dessen wird das Korrelationsprodukt nun wie folgt gebildet:

{{< svg "lectures/es-lab/images/offset_2S_tex" >}}

<div class="highlight-block highlight-note">

Das Summensignal $\mathcal{S}$ wurde an sich selbst angehängt.
Die Verknüpfung von $c_i$ und $\mathcal{S}$ findet jetzt erst ab einem Offset $\delta$ statt.
Das Wichtige: Verknüpft werden immer noch $c_i[0]$ bis $c_i[6]$ mit $\mathcal{S}[3]$ bis $\mathcal{S}[9]$ und $c_i[7]$ bis $c_i[9]$ mit $\mathcal{S}[0]$ bis $\mathcal{S}[3]$.

</div>

#### Optimierte Implementierung
Hier die optimierte Schleife in `C++`:

```cpp {linenos=inline}
int correlation_product = 0;
int delta = 0;
int bit = 0;
// For each satellite...
for (size_t i = 0; i < chip_vectors.size(); i++) {

    delta = -1;
    bit = -1;

    // Test every offset delta...
    for (int d = 0; d < SEQ_LEN; d++) {
        correlation_product = 0;
        // ... and calculate the CP.
        for (int j = 0; j < SEQ_LEN; j++) {
            correlation_product += input[j+d] * chip_vectors[i][j];
        }

        if (correlation_product > 800) {
            bit = 1;
            delta = SEQ_LEN - d;
        } else if (correlation_product < -800) {
            bit = 0;
            delta = SEQ_LEN - d;
        } 
    }

    if (bit != -1) {
        printf("Satellite %2d has sent bit %d (delta = %d)\n", (int)(i+1), bit, delta);
    }
}
```

Hierbei ändern sich zwei Dinge: 
- der Modulo-Operator wurde entfernt indem der Offset $\delta$ nun auf das Summensignal gegeben wird. 
- Dadurch, dass der Offset nun auf das Summensignal und nicht auf die Chipsequenz gerechnet wird, muss beim Speichern des Offsets nicht `d`, sondern `SEQ_LEN - d` gespeichert werden.

Und hier die optimierte Schleife in `C`:

```C {linenos=inline}
int cp = 0;
int delta = 0;
int bit = 0;

for (int i = 0; i < NUM_SAT; i++) {
    delta = -1;
    bit = -1;

    for (int d = 0; d < SEQ_LEN; d++) {
        cp = 0;

        for (int j = 0; j < SEQ_LEN; j++) {
            cp += input[j + d] * chip_sequences[i][j];
        }

        if (cp > 800) {
            bit = 1;
            delta = SEQ_LEN - d;
        } else if (cp < -800) {
            bit = 0;
            delta = SEQ_LEN - d;
        } 

    }

    if (bit != -1) {
        printf("Satellite %2d has sent bit %d (delta = %d)\n", i+1, bit, delta);
    }
}
```

Die Änderungen sind analog zu denjenigen in `C++`.

### Optimierung durch Compiler-Flags II

{{< svg "lectures/es-lab/images/results_table_opt_tex" >}}

<div class="highlight-block highlight-important">

**Fazit:** Die Ergebnisse unterscheiden sich im Verhältlnis nicht sonderlich von denjenigen ohne Code-Optimierung: `C` ist deutlich schneller als `C++`, solange man keine Compiler Optimierung nutzt.
Sobald diese genutzt wird, sind `C` und `C++` quasi gleich schnell.
</div>

### Verbesserungen durch Code-Optimierung
Um welchen Faktor haben sich also die Programme durch die Code-Optimierung bei den jeweiligen Optimierungsstufen verbessert?

Im Falle von `C` hat sich folgendes ergeben:

{{< svg "lectures/es-lab/images/results_C_improv_tex" >}}

Bei `C++` sieht es wie folgt aus:

{{< svg "lectures/es-lab/images/results_Cpp_improv_tex" >}}

<div class="highlight-block highlight-important">

**Fazit:** Die Code-Optimierung ohne Compiler-Optimierung bringt also bei `C++` eine Verbesserung um $13\%$ und bei `C` um $30\%$.
Dies ist bereits substantiell.
Interessant ist allerdings, dass die Verbeserung erst richtig zu tragen kommt, wenn dazu noch eine Compiler-Optimierung verwendet wird.
Hierdurch erreicht man bei `C++` Verbesserungen von bis zu $82\%$ und bei `C` bis zu $83\%$.
</div>

## Anhang

<a href="/data/C_Cpp_Comparison.csv">Download .csv file</a>
