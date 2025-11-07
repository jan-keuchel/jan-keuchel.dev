---
title: Fuzzing Concurrently in Go
desc: Projektarbeit an der HKA
published: 2025-09-23
language: de
---
# Dokumentation: Fuzzing concurrent Go

## Nebenläufigkeit in Go

Nebenläufigkeit (Concurrency) in Go bezeichnet die Fähigkeit eines Programms, mehrere Operationen scheinbar gleichzeitig auszuführen, indem die Ausführung dieser Operationen in kleine Abschnitte zerlegt und zwischen ihnen hin- und hergewechselt wird. Diese Nebenläufigkeit kann in Go über sogenannte Goroutinen realisiert werden.

### Goroutinen

Eine Goroutine ist ein leichtgewichtiger Thread, der nicht vom Betriebssystem, sondern von der Go-Runtime verwaltet wird, wodurch die Kontextwechsel effizienter erfolgen als bei herkömmlichen Prozessen oder Threads.

#### Ablauf eines Programms I

Ein Programm, welches aus einer einzelnen Goroutine besteht, wird linear ausgeführt. 
Es ist also zu jedem Zeitpunkt klar, was derjenige Befehl ist, welcher als nächstes ausgeführt werden soll.
Unter der Verwendung von Goroutinen werden mehrere - jeweils linear ablaufende - Instanzen quasi-parallel ausgeführt.
Da die Goroutinen erstmal nicht aufeinander abgestimmt sind und diese - basierend auf der Aufwendigkeit der Operationen - unterschiedlich schnell arbeiten, ist nicht mehr klar, an welchem Punkt der Ausführung sich die jeweiligen Goroutinen befinden und wie sie im Verhältnis zueinander stehen.
Falls also eine Goroutine das Vorhandensein eines Datenpunktes - für dessen Berechnung eine andere Goroutine zuständig ist - als Voraussetzung für die korrekte Bearbeitung seiner Operationen hat, kann nicht garantiert werden, dass eben diese andere Goroutine jene Berechnung bereits ausgeführt hat.
Um den Ablauf multipler Goroutinen kontrollieren zu können und diese somit aufeinander abzustimmen, gibt es Synchronisierungsmöglichkeiten: 

* **Channels:** Channels ermöglichen Kommunikation und Synchronisation zwischen Goroutinen durch Message Passing. 
Eine Goroutine kann Daten über einen Channel senden (`ch <- data`), oder Daten aus einem Channel empfangen (`data := <-ch`). 
Die Ausführung einer Goroutine wird durch das Senden oder Empfangen von Daten in oder aus einem Channel blockiert, bis eine andere Goroutine mit dem jewiligen Pendant bereitsteht.
Somit ist es möglich, mehrere Goroutinen aufeinander abzustimmen.
    * Beispiel:
    {% highlight go linenos %}
    ch := make(chan int)    // erstellt einen Channel
    // Startet eine anonyme Funktion, die über eine 
    // andere Gortouine ausgeführt wird.
    go func() {             
        // Blockiert, bis 42 aus dem Channel gelesen wird
        ch <- 42            
    }() 
    // Blockiert, bis Daten in den Channel gesendet werden
    fmt.Println(<-ch)       
    {% endhighlight %}

* **Mutexe:** Mutexe (Mutual Exclusion) schützen gemeinsame Ressourcen vor gleichzeitigen Zugriffen durch Goroutinen, um Race Conditions zu verhindern. 
Ein Mutex wird mit `Lock()` gesperrt und mit `Unlock()` freigegeben.
Ist ein Mutex erstmal gesperrt kann er nicht von einer anderen Goroutine erneut gesperrt werden.
Es ist also erst dann wieder möglich, den `Lock()`-Befehl auszuführen, wenn der Mutex von derjenigen Goroutine, die den Mutex gesperrt hat, wieder freigegeben wird.
    * Beispiel:
    {% highlight go linenos %}
    // Erstellt einen Mutex
    var mu sync.Mutex   
    
    // Die Ressource, die geschützt werden soll
    var counter int     

    // Startet eine neue Goroutine
    go func() {         
        // Sperrt den Mutex, sodass nur eine Goroutine in diesen
        // Abschnitt eintreten kann Falls der Mutex durch eine 
        // andere Goroutine bereits gesperrt worden ist, würde diese
        // Goroutine hier blockieren, bis der Mutex wieder 
        // freigegeben wird.
        mu.Lock()       

        // Führt Operationen aus
        counter++       

        // Entsperrt den Mutex wieder, sodass eine
        // andere Goroutine eintreten kann
        mu.Unlock()     
    }()
    {% endhighlight %}

* **`select`:** Das select-Statement koordiniert die Ausführung, indem es zwischen mehreren Channel-Operationen wählt. 
Es blockiert, bis ein `case` (z. B. Senden/Empfangen) ausführbar ist, oder führt `default` aus, falls momentan keine Channel-Operation ausführbar ist. 
Es ermöglicht nicht-deterministische Auswahl bei gleichzeitigen Channel-Ereignissen.
    * Beispiel:
    {% highlight go linenos %}
    // Blockiert, bis einer der cases ausführbar ist
    select {    
    // Wartet auf Daten aus Channel ch1
    case msg := <-ch1:  
        fmt.Println(msg)
    // Wartet, bis '1' aus dem Channel ch2 gelesen wird
    case ch2 <- 1:  
        fmt.Println("Gesendet")
    // Wird direkt ausgeführt, falls kein case ausführbar ist
    default:   
        fmt.Println("Nichts bereit")
    }
    {% endhighlight %}

#### Beispiele Goroutinen und Synchronisierung

##### Einführungsbeispiel zu Goroutinen ohne Synchronisierung
{% highlight go linenos %}
package main

import (
    "fmt"
    "time"
)

func f(from string) {
    for i := 0; i < 3; i++ {
        fmt.Println(from, ":", i)
    }
}

func main() {

    // Synchrone Ausführung einer Funktion.
    // Es existiert also nur eine Goroutine.
    f("synchron")

    // Hier wird zusätzlich zu der aktuellen Goroutine eine 
    // weitere Goroutine erstellt, welche die Funktion 
    // asynchron ausführt.
    go f("asynchron")

    // Asynchroner Aufruf einer anonymen Funktion
    go func(msg string) {
        fmt.Println(msg)
    }("anonym, asynchron")

    // Momentan ist nicht klar, ob die beiden gestarteten 
    // Goroutinen schon fertig sind. Also wird für eine Sekunde
    // gewartet. Danach terminiert das Programm.
    time.Sleep(time.Second)
    fmt.Println("done")
}
{% endhighlight %}
(**Hinweis:** Durch das Warten von einer Sekunde ist nicht garantiert, dass die beiden gestarteten Goroutinen wirklich terminiert sind. Dafür gibt es andere Strukturen: WaitGroups)

Die "intuitive" Reihenfolge, in der das Programm ausgeführt werden sollte, wäre linear, von oben nach unten. Die Ausgabe wäre wie folgt:
{% highlight bash linenos %}
synchron : 0
synchron : 1
synchron : 2
asynchron : 0
asynchron : 1
asynchron : 2
anonym, asynchron
done
{% endhighlight %}
Wenn man das Programm allerdings ausführt, erhält man zum Beispiel die folgende Reihenfolge:
{% highlight bash linenos %}
synchron : 0
synchron : 1
synchron : 2
anonym, asynchron
asynchron : 0
asynchron : 1
asynchron : 2
done
{% endhighlight %}
Der Grund dafür ist, dass die Ausführung von `f` länger gedauert hat, als das Ausführen der anonymen Funktion.
Führt man das Programm noch weitere Male aus, kann es passieren dass man auch zu dieser Reihenfolge kommt (was der linearen Reihenfolge entspricht):
{% highlight bash linenos %}
synchron : 0
synchron : 1
synchron : 2
asynchron : 0
asynchron : 1
asynchron : 2
anonym, asynchron
done
{% endhighlight %}
Festzuhalten ist Folgendes: die "synchrone" Ausgabe wird **immer** als erstes ausgegeben werden, da zu diesem Zeitpunkt nur eine einzelne Goroutine vorhanden ist.
Sobald aber mehr als eine Goroutine vorhanden ist, und man diese nicht mit den oben beschriebenen Synchronisierungsmöglichkeiten aufeinander abstimmt, ist die Ausgabe nicht-deterministisch.

##### Beispiele mit Synchronisierung
###### Channels
{% highlight go linenos %}
package main

import (
    "fmt"
    "time"
    "log"
)

func main() {
    // Main Goroutine G0

    max_delay := 4000

    rand.Seed(time.Now().UnixNano())
    var wg sync.WaitGroup

    // Erstelle 2 Channels, um strings 
    // zwischen Goroutinen senden zu können
    c1 := make(chan string)
    c2 := make(chan string)

    // Konfiguriere die Waitgroup so, dass auf 
    // zwei Goroutinen gewartet wird
    wg.Add(2)

    // Asynchrone Goroutine G1
    go func(c1 chan string, c2 chan string) {
        // Beim Austritt aus der Funktion wird der Waitgroup
        // signalisiert, dass eine der Funktionen terminiert ist.
        defer wg.Done()

        log("[G1] Working...")
        time.Sleep(time.Duration(rand.Intn(max_delay)) * time.Millisecond)
        log("[G1] Finished working. Waiting for data from Channel c2...")
        data := <- c2			    // op1
        log("[G1] Received data. Continue working...")
        time.Sleep(time.Duration(rand.Intn(max_delay)) * time.Millisecond)
        log("[G1] Finished working. Forwarding data into Channel c1...")
        c1 <- data			        // op2
        log("[G1] Done.")
    } (c1, c2)

    // Asynchrone Goroutine G2
    go func(c1 chan string, c2 chan string) {
        defer wg.Done()

        log("[G2] Working...")
        time.Sleep(time.Duration(rand.Intn(max_delay)) * time.Millisecond)
        log("[G2] Finished working. Sending data into channel c2...")
        c2 <- "Greetings from G2"	// op3
        log("[G2] Done.")
    } (c1, c2)

    log("[G0] Working...")
    time.Sleep(time.Duration(rand.Intn(max_delay)) * time.Millisecond)
    log("[G0] Finished working. Waiting for data from Channel c1...")
    data := <- c1				    // op4
    log("[G0] Received data: '" + data + "'.\n[G0] Done")

    wg.Wait()

    close(c1)
    close(c2)

}
{% endhighlight %}
Bei der Ausführung dieses Programms kann zum Beispiel die folgende Ausgabe entstehen:
{% highlight bash linenos %}
[G0] Working...
[G2] Working...
[G1] Working...
[G2] Finished working. Sending data into channel c2...
[G1] Finished working. Waiting for data from Channel c2...
[G1] Recieved data. Continue working...
[G2] Done.
[G0] Finished working. Waiting for data from Channel c1...
[G1] Finished working. Forwarding data into Channel c1...
[G1] Done.
[G0] Received data: 'Greetings from G2'.
[G0] Done
{% endhighlight %}
In diesem Programm liegen Abhängigkeiten vor. Damit ist gemeint, dass es nicht in beliebiger Reihenfolge ausgeführt werden kann, da die Reihenfolge anhand von Channel-Operationen forciert ist.

Betrachtung der einzelnen Goroutinen:
* G0: Blockiert bei *op4*, bis Daten aus *c1* genommen werden.
* G1: Blockiert bei *op1*, bis Daten aus *c2* genommen werden. Erst danach kann *op2* ausgeführt werden, welche ebenfalls blockiert, bis die Daten von einer anderen Goroutine aus *c1* heraus genommen werden.
* G2: Blockiert bei *op3*, bis Daten aus *c2* genommen werden.


###### Mutexe
Bei Mutexen geht das darum, sicherzustellen, dass keine parallelen Modifikationen von geteilten Ressourcen stattfinden.
Ein Mutex kann entweder *offen* oder *gesperrt* sein, was mit den Operationen `mutex.Lock()`, sowie `mutex.Unlock()` realisiert wird.
Führt eine Goroutine den `Lock()`-Befehl aus, so ist der Mutex, auf dem die Operation ausgeführt wird, gesperrt. 
Somit ist es keiner anderen Goroutine mehr möglich, den Mutex ebenfalls zu sperren, bis diejenige Goroutine, die den Mutex ursprünglich gesperrt hat, diesen mit `Unlock()` wieder freigibt. 
Alle anderen Goroutinen blockieren also beim `Lock()`-Befehl.

Im Folgenden Beispiel wird bis 2000 gezählt. Einmal "normal", also in einer einzelnen Goroutine, dann mithilfe von mehreren Goroutinen, welche aber ohne Beschränkungen auf den Counter zugreifen und im letzten Fall ebenfalls mithilfe von mehreren Goroutinen aber zusätzlich mithilfe eines Mutex, welcher Race-Conditions verhindert.

{% highlight go linenos %}
package main

import (
    "fmt"
    "time"
)

func main() {

    // Synchron
    ctr := 0
    for range(2000) {
        ctr++
    }

    fmt.Println("Synchron Counter: ", ctr)

    // Asynchron
    var wg sync.WaitGroup
    wg.Add(10)

    ctr = 0

    // Starte 10 asynchron ausgeführte anonyme Funktionen
    for range(10) {
        go func() {
            defer wg.Done()
            for range(200) {
                ctr++
            }
        }()
    }
    wg.Wait()

    fmt.Println("Asynchron Counter: ", ctr)

    // Asynchron mit Mutex
    wg.Add(10)
    var mu sync.Mutex

    ctr = 0
    for range(10) {
        go func() {
            defer wg.Done()
            for range(200) {
                mu.Lock()   // Mutex sperren
                ctr++       // Gesicherter Datenzugriff
                mu.Unlock() // Mutex freigeben
            }
        }()
    }
    wg.Wait()

    fmt.Println("Asynchron Counter, Mutex: ", ctr)

}
{% endhighlight %}

**Ausgabe mehrerer Programm-Ausführungen:**
{% highlight bash linenos %}
Synchron Counter:  2000
Asynchron Counter:  1840
Asynchron Counter, Mutex:  2000
--------------------------------
Synchron Counter:  2000
Asynchron Counter:  2000
Asynchron Counter, Mutex:  2000
--------------------------------
Synchron Counter:  2000
Asynchron Counter:  1572
Asynchron Counter, Mutex:  2000
{% endhighlight %}
Der Synchrone Counter ist immer korrekt, da nur eine Goroutine auf die Ressource zugreift. 
Im zweiten Fall können Probleme entstehen, weil das Inkrementieren keine atomare Operation ist: Mehrere Goroutinen kopieren sich also den aktuellen Wert des Counters in den Speicher und inkrementieren diesen jeweils. Dann schreiben alle den Wert wieder zurück in die Counter-Variable, wodurch manche Inkrementierungen verloren gehen.
Im letzten Fall entstehen keine Probleme, weil durch einen Mutex sichergestellt ist, dass sich immer nur eine Goroutine im Abschnitt der Inkrementation befindet.


###### `select`-Statement
{% highlight go linenos %}
package main

import (
    "fmt"
    "time"
)

func main() {

    // Erstellt zwei Channel c1, c2
    c1 := make(chan string)
    c2 := make(chan string)

    // Zwei asynchrone Goroutinen, welche eine 
    // bzw. zwei Sekunden warten und dann Daten in c1, c2 geben
    go func() {
        time.Sleep(1 * time.Second)
        c1 <- "one"
    }()
    go func() {
        time.Sleep(2 * time.Second)
        c2 <- "two"
    }()

    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-c1:
            fmt.Println("received", msg1)
        case msg2 := <-c2:
            fmt.Println("received", msg2)
        }
    }
}
{% endhighlight %}
Beim Ausführen dieses Programms erhält man die folgende Ausgabe:
{% highlight bash linenos %}
received one
received two
{% endhighlight %}
(Das warten von einer bzw. zwei Sekunden soll eine Berechnung simulieren.)
Tauscht man die Wartezeit der anonymen Goroutinen aus, sodass - im Code - erstere 2 Sekunden wartet und - im Code - letztere nur 1 Sekunde wartet, so terminiert das Programm mit folgender Ausgabe:
{% highlight bash linenos %}
received two
received one
{% endhighlight %}
Es ist also festzuhalten, dass das `select`-Statement ausschließlich den Ablauf in der jeweiligen Goroutine blockiert, bis eines der Ereignisse (`case`'s) eintritt.
Somit ist hierbei keinerlei Reihenfolge oder Abhängigkeit einer Goroutine zu einer anderen festgelegt. 

Im Gegenteil, alle `case`'s, die sich in einem `select`-Statement befinden, sind unabhängig voneinander und sollten *theoretisch* beliebig permutiert werden können und dennoch in einer validen Ausführung des Programms resultieren.

#### Ablauf eines Programms II
Festzuhalten ist also, dass man die - ohne weitere Eingriffe -  zufällige Ausführungsreihenfolge, bei der Verwendung von multiplen Goroutinen, mithilfe von Channels kontrollieren und aufeinander abstimmen kann.
Jede Channel-Operationen stellt also einen Synchronisierungspunkt dar, der die Korrektheit des Programms garantieren soll.

Durch `select`-Statements ergeben sich weitere Kontrollmöglichkeiten. Jedoch gilt im Bezug auf die Abhängigkeit der parallel laufenden Goroutinen, dass diese nicht in Relation zueinander stehen, also unabhängig voneinander sind.
Zu jedem Zeitpunkt der Ausführung, zu dem sich ein Programm in einem bestimmten Zustand befindet, sollte jede der durch ein `select`-Statement zur Verfügung gestellten Optionen (`case`'s) einen validen Folgezustand hervorrufen.
Anders: Für jede mögliche Ausführungsreiheinfolge muss das Programm korrekt ausgeführt werden können.

### Fehler unter der Verwendung von Channels

Channels werden - wie oben beschrieben - verwendet, um die unterschiedlichen Goroutinen aufeinander abzustimmen, diese untereinander zu synchronisieren und Daten zwischen ihnen auszutauschen.
Allerdings können bei ihrer Verwendung Fehler auftreten, die die Korrektheit eines Programms beeinträchtigen oder zu Programmabbrüchen führen.

#### Typen von Fehlern

1. **Deadlock**: Ein Deadlock tritt auf, wenn Goroutinen auf eine Channel-Operation warten, die niemals ausgeführt wird, weil keine andere Goroutine das entsprechende Pendant (Senden oder Empfangen) ausführt.
Dies führt dazu, dass alle Goroutinen blockiert sind, das Programm hängen bleibt und Go's Laufzeitumgebung einen Deadlock-Fehler wirft: `fatal error: all goroutines are asleep - deadlock!`

2. **Lecks bei Channels**: Werden Daten in einen Channel geschrieben, aber von keiner anderen Goroutine gelesen, weil z.B. kein Verweis mehr auf den Channel besteht, oder einfach wegen eines Logikfehlers in der Programmierung, tritt ein Channel-Leck auf (*leaking channel*). 
Der Channel selbst, sowie die Daten im Channel bleiben also im Speicher und verursachen einen Speicherleck.

3. **Falsches Schließen von Channels**: Schließt man einen Channel zu früh, in einer falschen Goroutine oder versucht einen Channel mehrach zu schließen, kann unerwartetes Verhalten auftreten.

#### Beispiele
##### Deadlock durch fehlenden Empfänger
{% highlight go linenos %}
package main

import "fmt"

func main() {
    ch := make(chan int) // Erstelle einen Channel
    ch <- 42             // Blockiert, da kein Empfänger existiert.
    fmt.Println(<-ch)    // Wird nie erreicht
}
{% endhighlight %}

**Ausgabe:** `fatal error: all goroutines are asleep - deadlock!.`

**Das Problem:** Die Main-Goroutine versucht den Wert `42` in den Channel `ch` zu senden. Da es keine andere Goroutine gibt, die diesen Wert ließt, blockiert das Programm. Die Go Laufzeitumgebung erkennt den Deadlock un bricht das Programm ab.

##### Leckender Channel
{% highlight go linenos %}
package main

import (
    "fmt"
    "time"
)

func main() {
    ch := make(chan int)
    go func() {     // G1
        ch <- 42 // Blockiert, da kein Empfänger den Channel liest.
    }()
    time.Sleep(time.Second)
    fmt.Println("Programm beendet")
}
{% endhighlight %}

**Das Problem:** Die Main-Goroutine beendet sich, ohne auf die Goroutine zu warten, die Daten in den Channel `ch` sendet. G1 bleibt blockiert und verursacht einen Speicherleck.

##### Panic durch Senden an geschlossenen Channel
{% highlight go linenos %}
package main

import "fmt"

func main() {
    ch := make(chan int)
    close(ch)    // Channel wird geschlossen
    ch <- 42     // Senden an geschlossen Channel verursacht Panic
    fmt.Println(<-ch)
}
{% endhighlight %}

**Ausgabe:** `panic: send on closed channel`

**Das Problem:** Hier wird ein Channel geschlossen - was z.B. in einer anderen Goroutine passieren könnte - und dann eine Nachricht in diesen Channel gegeben, wodurch ein "Panic" entsteht.

### Komplexität der Fehler
Die hier aufgeführten Fehler sind trivial zu beheben und nicht schwer zu erkennen.
Sie sind so geschrieben, dass der Fehler bei jeder ausführung auftritt und es z.B. zu einem Absturz des Programms führt.
Mit wachsender Komplexität des Programms wird es immer schwerer Fehler zu erkennen: Die Fehler könnten bis jetzt einfach noch nicht aufgetreten sein, weil man bisher nur geeignete Ausführungsreihenfolgen getestet hat. 
Wenn man dann doch feststellet, dass sich ein Programm nicht so wie gewünscht verhält, wird es ebenfalls kompliziert herauszufinden welche Sequenz den Fehler ausgelöst hat - Man kann die Ausführung nämlich nicht einfach wiederholen.

#### Beispiel mit nicht-deterministischer Ausführung
{% highlight go linenos %}
package main

import "fmt"

func main() {
    // G0

    rand.Seed(time.Now().UnixNano())

    ch1 := make(chan int)
    ch2 := make(chan int)

    // G1
    go func() {
        time.Sleep(time.Millisecond * time.Duration(rand.Intn(10)))
        ch1 <- 10 // op1
    }()

    // G2
    go func() {
        time.Sleep(time.Millisecond * time.Duration(rand.Intn(500)))
        value := <- ch1 // op2
        value *=2
        time.Sleep(time.Millisecond * time.Duration(rand.Intn(100)))
        ch2 <- value // op3
    }()

    time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))

    select {
    case value := <- ch1: // op4
        fmt.Println("Received value:", value)
    case <-time.After(500 * time.Millisecond): // op5
        fmt.Println("Nothing received. Continuing...")
    }

    value := <- ch2 // op6
    fmt.Println("Received final value:", value)

}
{% endhighlight %}

**Ausgabe mehrerer Programm-Ausführungen:**
{% highlight bash linenos %}
Received value: 0
Received final value: 20
--------------------------------
Received value: 0
Received final value: 20
--------------------------------
Received value: 0
Received final value: 20
--------------------------------
Received value: 0
Received final value: 20
--------------------------------
Received value: 10
fatal error: all goroutines are asleep - deadlock!
--------------------------------
Received value: 0
Received final value: 20
{% endhighlight %}
Wie vorher erwähnt: hätte man nach den ersten vier Tests aufgehört, wäre einem vielleicht nicht aufgefallen, dass bei der Ausführung des Programms ein Deadlock auftreten kann.
Der Grund dafür ist auch bei diesem Beispiel noch leicht erkennbar: `G0` und `G2` lesen beide mit *op4* und *op2* Daten von `ch1`, während `G1` mit *op1* Daten in `ch1` sendet.
Da nur ein Datenpunkt in `ch1` gegeben wird und basierend auf der Verzögerung, welche von Ausführung zu Ausführung variiert, entweder `G0` oder `G2` die Daten aus `ch1` ließt, blockiert die andere Goroutine.
Leißt `G2` die Daten aus `ch1` führt dies zu keinen Problemen, da `G0` einen Timeout im `select`-Statement hat und somit bei *op6* blockiert.
`G2` sendet, nach dem Lesen der Daten aus `ch1`, mit *op3* weitere Daten in `ch2`.
Somit kann auch `G0` Daten aus `ch2` lesen und blockiert nicht dauerhaft.

Ließt allerdings `G0` die Daten zuerst aus `ch1`, so blockiert die Goroutine danach bei *op6*, dem Lesen von Daten aus `ch2`.
Währenddessen blockiert `G2` bei *op2*, dem Lesen von Daten aus `ch1`.
Keine der Goroutinen sendet Daten in einen Channel, weshalb das Blockieren nicht aufgelöst werden kann: Es entsteht also ein Deadlock.

#### Was nun? Wie findet man Fehler in komplexen Programmen?
Es ist schwierig ein komplexes und umfangreiches Programm auf Basis von Nebenläufigkeit zu schreiben, welches keine Fehler enthält.
Manche - wenn auch sehr unwahrscheinliche - Verschachtelungen der Goroutinen fallen nicht direkt auf, können aber dennoch zu Fehlern führen.
Alle möglichen Reihenfolgen zu durchdenken und vor Fehlern abzusichern ist nicht effizient möglich.

Folglich benötigt man ein Tool, welches diese Aufgabe für einen übernimmt.

Zwei solcher Tools sind **GFuzz** und **GoPie**.
Diese basieren auf dem Prinzip von *Fuzzing*: Das Bereitstellen von zufälligen Eingaben in ein Programm, mit dem Ziel, eine Eingabe zu finden, die zu einem Fehler führt.
GFuzz und GoPie variieren das Konzept des Fuzzings so, dass nicht zufällige Eingaben an ein Programm bereitgestellt werden, sondern die Ausführungsreihenfolge der parallel laufenden Goroutinen manipuliert wird.

Allerdings ist der naive Ansatz, alle möglichen Kombinationen per "Brute Force" auf Fehler zu testen, bei großen Projekten auch mithilfe eines Tools nicht effizient: die Anzahl der Kombinationsmöglichkeiten steigt zu stark an.
GFuzz und GoPie sammeln also während ihrer Ausführung Daten, um 1) das aktuelle Programm auf Fehler zu prüfen und 2) die Ausführungsreihenfolge der Goroutinen im nächsten Durchlauf effektiver permutieren zu können, sodass fehlerhafte Durchgänge schneller gefunden werden.

## GFuzz
### Funktionsweise
Durch Nebenläufigkeit hervorgerufene Bugs können anhand von zwei Ausprägungen kategorisiert werden:
- Es handelt sich um einen "blocking" oder "non-blocking" bug
- Die Ursache ist "shared memory" oder "message passing"

Ein "blocking" bug ist ein solcher, der dazu führt, dass eine der Goroutinen während der Ausführung hängen bleibt und nicht mehr weiter ausgeführt werden kann. Bei "non-blocking" bugs hingegen, laufen alle Goroutinen weiter, es entstehen aber ungewünschte Ergebnisse.

GFuzz fokusiert sich auf *blocking* und *non-blocking* *message passing* bugs. Für *shared memory* Bugs liegen bereits andere Tools vor.

Es wird sich auf *select* Blöcke fokusiert, weil für jeden *select* Block gilt, dass jede Option (jeder *case*) ohne vorgeschriebene Reihenfolge ausgeführt werden kann. Diese Nachrichten sind also nebenläufig und können später permutiert werden.

Um den Verlauf einer Ausführung des Programmes zu dokumentieren wird eine Struktur definiert: Jeder Ablauf wird durch eine Reihe von Drei-Tupeln dargestellt.
- Die *ID* des *select* Blocks
- Die Anzahl an *case*'s in einem Block
- Welcher der *case*'s ausgeführt worden ist.

#### Ablauf

- GFuzz nimmt ein Programm und Test-Eingaben als Eingabe und kompiliert dieses Programm. Hierbei wird die Runtime-Umgebung modifiziert, sodass die Ausführungsreiheinfolge bei *select*-Statements permutiert werden kann.
- Dann wird das Programm mit allen eingaben gestartet, ohne es zu beeinflussen. Die Ausführungsreiheinfolgen mit den jeweiligen Eingaben werden gespeichert.
- Danach wird immer eine dieser Reihenfolgen und Eingaben ausgewählt, permutiert und gestartet.
- Während der Ausführung werden Daten gesammelt, um einen Score zu berechnen, welcher dazu dient, neue Permutationen zu priorisieren, weil diese wahrscheinlicher sind Bugs auszulösen.

## GoPie

Das Ziel von GoPie ist es, durch Nebenläufigkeit hervorgerufene Bugs in Programmen aufzudecken, indem die Ausführungsreiheinfolge bestimmter Operationen permutiert und forciert wird.
GoPie ist also ein allgemeiners Tools als GFuzz und beschränkt sich nicht nur auf *select*-Statements.

### Funktionsweise
#### primitive-oriented operations
GoPie betrachtet die folgenden Primitive und Operationen auf den jeweiligen Primitiven:
- Goroutinen (routine): Keien Operation
- Mutexe (mutex): Lock, Unlock
- Read/Write-Mutexe (rwmutex): Lock, Unlock, RLock, RUnlock
- Channel (channel): Send, Recv, Close

Ein Tripel, bestehend aus einer Goroutine, einem Primitiv und einer Operation auf diesem Primitiv ergibt eine sogenannte **primitive-oriented operation**

#### scheduling chains
Die Reihenfolge, in der diese primitive-oriented operations ausgeführt werden, muss festgehalten und definiert werden. Für diesen Zweck gibt es **scheduling chains**.
Hierbei handelt es sich um eine Liste der primitive-oriented operation Tripel, die somit die Reihenfolge definiert, in der diese ausgeführt wurden - oder werden sollen.

#### Forcierung der Ausführungsreiheinfolge
GoPie forciert die Ausführungsreiheinfolge indem um die Operationen auf den Primitiven schleifen eingebaut werden, welche dafür sorgen, dass das Programm blockiert.
Die scheduling chain gibt vor, welche Operation als nächstes ausgeführt werden soll. Basierend auf diesen Daten wird zwischen den Schleifen hin- und hergewechselt.

## Toolanwendung
Fehlgeschlagen an diesem Projekt ist die tatsächliche Anwendung der Tools **GFuzz** und **GoPie**.
GoPie wurde installiert, hat aber nach teilweise mehreren Stunden keine Ausgaben geliefert. 
Ich konnte nicht herausfinden, was zu diesem Problem geführt hat.
GFuzz zu installieren habe ich leider nicht geschafft.
GoPie und GFuzz mithilfe von **ADVOCATE Go** zu nutzen hat leider ebenfalls zu Problemen geführt.
Dies hat hauptsächlich mit Pfad- und Versionsproblemen zutun gehabt.
Nach der Installation von ADVOCATE und der Anwendung von GFuzz mithilfe von ADVOCATE, wurde allerdings kein Fehler in offensichtliche fehlerhaften Programmen gefunden.
Die am Ende beschriebenen Tools konnten also nicht selbst getestet werden.
