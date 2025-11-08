---
title: Display of code on a webpage
desc: This document shows how code looks on a webpage
date: 18.09.2025
language: en
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

This is an even longer piece of code:
{% highlight go linenos %}
func handleStart(s *Server, p *packet.Packet) {

	log.Printf("Debug handleStart called\n")

	// Decode raw bytes
	payload, err := packet.DecodeFlagData(p.Data)
	if err != nil {
		log.Printf("[Server] Error decoding StateData: %v\n", err)
		return
	}

	// Set the voters start vote to 'true'
	s.conns[s.playerIdToConn[payload.PlayerID]].votedStart = true

	// Check if all clients voted for start
	for _, clientState := range s.conns {
		if !clientState.votedStart {
			return
		}
	}

	s.setupGame()

}

func handleExit(s *Server, p *packet.Packet) {

}

func handleGameInput(s *Server, p *packet.Packet) {

	// Decode raw bytes
	payload, err := packet.DecodeInputData(p.Data)
	if err != nil {
		log.Printf("[Server] Error decoding StateData: %v\n", err)
		return
	}

	// Get player
	player := s.game.Players[payload.PlayerID]

	// Update movement input
	player.Up 	= payload.Up
	player.Left 	= payload.Left 
	player.Right 	= payload.Right
	player.Down 	= payload.Down 

	// Update shooting input
	player.Shoot	= payload.Shoot
	player.MouseX	= int32(payload.AimX)
	player.MouseY	= int32(payload.AimY)

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
