# LTL Checker

## Instructions

Install dependency: `sudo apt-get install graphviz`

Compile the ltl2ba:
```shell
cd ltl2ba-1.3 && make && cd ..
```

Add following commands in `~/.bashrc`

```shell
(Replace XXXX to your local path)
export PATH=${PATH}:/XXXX/ltl2ba-1.3
export PATH=${PATH}:/XXXX/gltl2ba-master
```

## Run

`python check_ltl.py`

The statistics for the LTL checking will show up in terminal, and the error/false LTL will show up at the end