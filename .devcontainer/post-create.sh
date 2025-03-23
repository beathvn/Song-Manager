pip install poetry
poetry config virtualenvs.in-project true
poetry install

# Tool for inspecting docker images https://github.com/wagoodman/dive (make sure to run this in bash)
# DIVE_VERSION=$(curl -sL "https://api.github.com/repos/wagoodman/dive/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
# curl -OL https://github.com/wagoodman/dive/releases/download/v${DIVE_VERSION}/dive_${DIVE_VERSION}_linux_amd64.deb
# sudo apt install ./dive_${DIVE_VERSION}_linux_amd64.deb


# configure zsh
echo "cloning zsh plugins"
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

plugins="zsh-autosuggestions zsh-syntax-highlighting"
for plugin in $plugins; do
    if ! grep -q "$plugin" ~/.zshrc; then
        echo "Adding plugin '$plugin' to ~/.zshrc"
        sed -i 's/plugins=(\(.*\))/plugins=(\1 '"$plugin"')/' ~/.zshrc
    else
        echo "Plugin '$plugin' already in ~/.zshrc"
    fi
done

echo "Setting ZSH_THEME"
sed -i 's/^ZSH_THEME=.*/ZSH_THEME="steeef"/' ~/.zshrc

# we need to do this, otherwise, we cannot install dirsync
git config --global --add safe.directory /workspaces/Song-Manager/.venv/src/dirsync