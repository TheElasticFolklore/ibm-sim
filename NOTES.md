# What I checked, and what the agent got wrong

## What the agent got wrong

- Agent did a good job fixing the bugs, and improving overall architecture of the code.
- However, when I asked it to remove dead code, it removed everything that was not used.
- Then, I told it to check whether the functions are actually dead or not used (left).

## What I checked before I accepted its work

- I review the code manually to check if logic is correct.
- `config_loader` is imported to use hardcoded 80% value.
- I ran `python verify.py` to confirm it.

## What the data actually said

- **Service due** and **load coefficient** were the main predictor.
- **Service due** or **load coefficient** alone does not predict reliablely.
