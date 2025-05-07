# Song-Manager

> [!IMPORTANT]
> **Disclaimer:**
> This project is provided "as is", without express or implied warranties of any kind. The author assumes no responsibility or liability for the use of this project or for the accuracy, reliability, or timeliness of the information contained herein. Any actions taken based on this project or the information provided therein are done so at the user's own risk.
> This project is for entertainment purposes only. The author assumes no liability for any violations of copyright, laws or regulations resulting from the use of this project. It is the user's responsibility to ensure that their actions are in accordance with applicable law.
> It is strongly recommended that users purchase their favorite songs and music content legally in order to properly support artists and rights holders. Any use of this project to illegally distribute, reproduce or access copyrighted material without authorization is expressly prohibited.
> By using this project, the user agrees to hold the author harmless from any claims, damages or legal consequences that may arise from the use of this project.

## What is it about?

Song-Manager is a collection of scripts to manage your music collection. This includes spotify and rekordbox as well as some other functionalities.

The documentation is split up into several sections. See the table of contents below for an overview:

- [Spotify](./docs/spotify.md)
- [Rekordbox](./docs/rekordbox.md)
- [Other](./docs/other.md)
- [Developement](./docs/developement.md)

## Getting started

### Dev Container

For some features (no local folder mounts required) you can use devcontainer. To learn more about that, check [this](https://code.visualstudio.com/docs/devcontainers/containers) out.

### Local machine (tested only on MacOS)

Some features require you run them on your local machine.
make sure that you have `uv` installed - you can install that with [brew](https://brew.sh). Then make sure you configure the virtual environmen in the project with:

```bash
uv sync
```

This will create a virtual environment and install all dependencies.

> [!NOTE]
> Make a script executable with this command `chmod +x script.sh`
