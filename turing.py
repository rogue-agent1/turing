#!/usr/bin/env python3
"""Turing machine simulator — configurable states, symbols, transitions."""
import sys, json

class TuringMachine:
    def __init__(self, tape="", blank="_", start="q0", accept={"halt"}):
        self.tape = list(tape) if tape else [blank]
        self.blank = blank; self.head = 0; self.state = start
        self.accept = accept; self.transitions = {}; self.steps = 0
    def add(self, state, symbol, new_state, write, move):
        self.transitions[(state, symbol)] = (new_state, write, move)
    def read(self):
        while self.head >= len(self.tape): self.tape.append(self.blank)
        while self.head < 0: self.tape.insert(0, self.blank); self.head += 1
        return self.tape[self.head]
    def step(self):
        sym = self.read()
        key = (self.state, sym)
        if key not in self.transitions: return False
        new_state, write, move = self.transitions[key]
        self.tape[self.head] = write
        self.head += 1 if move == "R" else -1
        self.state = new_state; self.steps += 1
        return True
    def run(self, max_steps=10000, trace=False):
        while self.state not in self.accept and self.steps < max_steps:
            if trace: print(self.render())
            if not self.step(): break
        return self.state in self.accept
    def result(self):
        return "".join(self.tape).strip(self.blank)
    def render(self):
        t = "".join(self.tape)
        ptr = " " * self.head + "^"
        return f"[{self.state}] {t}\n       {ptr}"

def binary_increment():
    tm = TuringMachine("1011", start="right", accept={"halt"})
    tm.add("right", "0", "right", "0", "R")
    tm.add("right", "1", "right", "1", "R")
    tm.add("right", "_", "carry", "_", "L")
    tm.add("carry", "1", "carry", "0", "L")
    tm.add("carry", "0", "halt", "1", "R")
    tm.add("carry", "_", "halt", "1", "R")
    return tm

def busy_beaver_3():
    tm = TuringMachine("", start="A", accept={"halt"})
    tm.add("A","_","B","1","R"); tm.add("A","1","halt","1","R")
    tm.add("B","_","C","_","R"); tm.add("B","1","B","1","R")
    tm.add("C","_","C","1","L"); tm.add("C","1","A","1","L")
    return tm

if __name__ == "__main__":
    demo = sys.argv[1] if len(sys.argv) > 1 else "increment"
    if demo == "increment":
        tm = binary_increment()
        print(f"Input:  {tm.result()}")
        tm.run(trace="--trace" in sys.argv)
        print(f"Output: {tm.result()} ({tm.steps} steps)")
    elif demo == "beaver":
        tm = busy_beaver_3()
        tm.run(1000)
        ones = tm.result().count("1")
        print(f"3-state busy beaver: {ones} ones in {tm.steps} steps")
    else:
        print("Usage: turing.py [increment|beaver] [--trace]")
