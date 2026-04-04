#!/usr/bin/env python3
"""turing - Turing machine simulator with tape visualization and step-by-step execution."""

import sys, json

class TuringMachine:
    def __init__(self, rules, initial='q0', accept='qaccept', reject='qreject', blank='_'):
        self.rules = rules  # {(state, symbol): (new_state, write, direction)}
        self.initial = initial
        self.accept = accept
        self.reject = reject
        self.blank = blank

    def run(self, tape_input, max_steps=10000, verbose=False):
        tape = list(tape_input) if tape_input else [self.blank]
        head = 0
        state = self.initial
        steps = 0
        history = []

        while steps < max_steps:
            # extend tape if needed
            while head < 0:
                tape.insert(0, self.blank)
                head += 1
            while head >= len(tape):
                tape.append(self.blank)

            symbol = tape[head]
            history.append((state, head, ''.join(tape)))

            if state == self.accept:
                if verbose: self._print_step(steps, state, head, tape, "ACCEPT")
                return True, steps, ''.join(tape).strip(self.blank), history
            if state == self.reject:
                if verbose: self._print_step(steps, state, head, tape, "REJECT")
                return False, steps, ''.join(tape).strip(self.blank), history

            key = (state, symbol)
            if key not in self.rules:
                if verbose: self._print_step(steps, state, head, tape, "HALT (no rule)")
                return False, steps, ''.join(tape).strip(self.blank), history

            new_state, write, direction = self.rules[key]
            if verbose:
                self._print_step(steps, state, head, tape,
                    f"({state},{symbol}) → ({new_state},{write},{direction})")

            tape[head] = write
            state = new_state
            if direction == 'R': head += 1
            elif direction == 'L': head -= 1
            steps += 1

        return None, steps, ''.join(tape).strip(self.blank), history

    def _print_step(self, step, state, head, tape, info):
        tape_str = ''.join(tape)
        pointer = ' ' * head + '^'
        print(f"  Step {step:4d}: [{state:10s}] {tape_str}")
        print(f"             {'':10s}  {pointer} {info}")

def load_machine(path):
    with open(path) as f:
        data = json.load(f)
    rules = {}
    for r in data.get('rules', []):
        rules[(r['state'], r['read'])] = (r['next'], r['write'], r['move'])
    return TuringMachine(
        rules,
        data.get('initial', 'q0'),
        data.get('accept', 'qaccept'),
        data.get('reject', 'qreject'),
        data.get('blank', '_'),
    )

def cmd_run(args):
    verbose = '-v' in args or '--verbose' in args
    args = [a for a in args if a not in ('-v', '--verbose')]
    tm = load_machine(args[0])
    tape = args[1] if len(args) > 1 else ''
    result, steps, output, _ = tm.run(tape, verbose=verbose)
    status = 'ACCEPTED' if result else ('REJECTED' if result is False else 'TIMEOUT')
    print(f"\nResult: {status} in {steps} steps")
    print(f"Output: '{output}'")

def cmd_create(args):
    """Create example TM (binary increment)."""
    name = args[0] if args else 'increment'
    examples = {
        'increment': {
            'name': 'Binary Increment',
            'initial': 'right', 'accept': 'done', 'reject': 'qreject', 'blank': '_',
            'rules': [
                {'state': 'right', 'read': '0', 'next': 'right', 'write': '0', 'move': 'R'},
                {'state': 'right', 'read': '1', 'next': 'right', 'write': '1', 'move': 'R'},
                {'state': 'right', 'read': '_', 'next': 'carry', 'write': '_', 'move': 'L'},
                {'state': 'carry', 'read': '0', 'next': 'done', 'write': '1', 'move': 'R'},
                {'state': 'carry', 'read': '1', 'next': 'carry', 'write': '0', 'move': 'L'},
                {'state': 'carry', 'read': '_', 'next': 'done', 'write': '1', 'move': 'R'},
            ]
        },
        'palindrome': {
            'name': 'Palindrome checker (a/b)',
            'initial': 'q0', 'accept': 'qaccept', 'reject': 'qreject', 'blank': '_',
            'rules': [
                {'state': 'q0', 'read': 'a', 'next': 'qa', 'write': '_', 'move': 'R'},
                {'state': 'q0', 'read': 'b', 'next': 'qb', 'write': '_', 'move': 'R'},
                {'state': 'q0', 'read': '_', 'next': 'qaccept', 'write': '_', 'move': 'R'},
                {'state': 'qa', 'read': 'a', 'next': 'qa', 'write': 'a', 'move': 'R'},
                {'state': 'qa', 'read': 'b', 'next': 'qa', 'write': 'b', 'move': 'R'},
                {'state': 'qa', 'read': '_', 'next': 'checka', 'write': '_', 'move': 'L'},
                {'state': 'checka', 'read': 'a', 'next': 'back', 'write': '_', 'move': 'L'},
                {'state': 'checka', 'read': '_', 'next': 'qaccept', 'write': '_', 'move': 'R'},
                {'state': 'checka', 'read': 'b', 'next': 'qreject', 'write': 'b', 'move': 'R'},
                {'state': 'qb', 'read': 'a', 'next': 'qb', 'write': 'a', 'move': 'R'},
                {'state': 'qb', 'read': 'b', 'next': 'qb', 'write': 'b', 'move': 'R'},
                {'state': 'qb', 'read': '_', 'next': 'checkb', 'write': '_', 'move': 'L'},
                {'state': 'checkb', 'read': 'b', 'next': 'back', 'write': '_', 'move': 'L'},
                {'state': 'checkb', 'read': '_', 'next': 'qaccept', 'write': '_', 'move': 'R'},
                {'state': 'checkb', 'read': 'a', 'next': 'qreject', 'write': 'a', 'move': 'R'},
                {'state': 'back', 'read': 'a', 'next': 'back', 'write': 'a', 'move': 'L'},
                {'state': 'back', 'read': 'b', 'next': 'back', 'write': 'b', 'move': 'L'},
                {'state': 'back', 'read': '_', 'next': 'q0', 'write': '_', 'move': 'R'},
            ]
        }
    }
    if name not in examples:
        print(f"Available: {', '.join(examples.keys())}")
        sys.exit(1)
    print(json.dumps(examples[name], indent=2))

def cmd_stats(args):
    tm = load_machine(args[0])
    states = set()
    symbols = set()
    for (s, sym) in tm.rules:
        states.add(s)
        symbols.add(sym)
    for ns, w, _ in tm.rules.values():
        states.add(ns)
        symbols.add(w)
    print(f"States: {len(states)} ({', '.join(sorted(states))})")
    print(f"Symbols: {len(symbols)} ({', '.join(sorted(symbols))})")
    print(f"Rules: {len(tm.rules)}")
    print(f"Initial: {tm.initial}")
    print(f"Accept: {tm.accept}")

CMDS = {
    'run': (cmd_run, 'FILE [TAPE] [-v] — run Turing machine'),
    'create': (cmd_create, '[increment|palindrome] — create example TM'),
    'stats': (cmd_stats, 'FILE — machine statistics'),
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: turing <command> [args...]")
        for n, (_, d) in sorted(CMDS.items()):
            print(f"  {n:8s} {d}")
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd not in CMDS: print(f"Unknown: {cmd}", file=sys.stderr); sys.exit(1)
    CMDS[cmd][0](sys.argv[2:])

if __name__ == '__main__':
    main()
