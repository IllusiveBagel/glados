# GLaDOS

GLaDoS based voice assistant

## Getting Started

- Clone repo and submodules with `git clone --recurse-submodules https://github.com/IllusiveBagel/glados.git`

- Download TTS model from [Google Drive](https://drive.google.com/file/d/1TRJtctjETgVVD5p7frSVPmgw8z8FFtjD/view) and extract in the project root directory

- Install required Python libaries with `pip install -r ./requirements.txt`

- rename `example.config.yaml` to `config.yaml` replacing the `address:` and `token:` values with your home assistant values. While in this file if the `rooms:` value doesnt match your setup you can adjust that too

- run `python3 glados.py`
