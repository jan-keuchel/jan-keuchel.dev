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

![Sum Signal SVG](sumsignal_tex)
