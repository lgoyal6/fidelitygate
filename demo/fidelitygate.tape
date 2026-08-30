Output demo/build/terminal.mp4

Require uv
Require jq

Set Shell "bash"
Set FontFamily "Menlo"
Set FontSize 22
Set Width 1600
Set Height 900
Set Padding 26
Set Framerate 30
Set TypingSpeed 8ms
Set Theme {"background":"#090e19","foreground":"#e8eefc","cursor":"#4fd1c5","black":"#090e19","red":"#ff6b6b","green":"#65d69e","yellow":"#f3bc64","blue":"#6e8cff","magenta":"#b692f6","cyan":"#4fd1c5","white":"#e8eefc","brightBlack":"#66738d","brightRed":"#ff8d8d","brightGreen":"#8be9b5","brightYellow":"#ffd48a","brightBlue":"#9bb0ff","brightMagenta":"#d3b7ff","brightCyan":"#80e7dd","brightWhite":"#ffffff"}

Hide
Type "cd __REPO_ROOT__"
Enter
Show

Type "uv run fidelitygate eval --suite evals/suites/smoke.json --system replay-baseline"
Enter
Sleep 4s

Type "uv run fidelitygate trace --suite evals/suites/search-stress.json --case-id env_900b --output /tmp/env_900b.json"
Enter
Sleep 2s

Type "jq '{verdict:.outcome.verdict, transitions:.outcome.explored_transitions, witness:.outcome.witness.actions, replay:[.outcome.witness.replay_successes,.outcome.witness.replay_attempts]}' /tmp/env_900b.json"
Enter
Sleep 7s
