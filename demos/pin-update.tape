Source demos/_settings.tape

Output demos/pin-update.gif
Output demos/pin-update.mp4

Hide
Type `eval "$(pixi shell-hook -s bash -e dev)"`
Enter
Wait /\)/
Type `export DEMO_HOME=/tmp/.demo-home-pin && rm -rf "$DEMO_HOME" && mkdir -p "$DEMO_HOME" && echo 'PS1="$ "' > "$DEMO_HOME/.bash_profile" && export HOME="$DEMO_HOME" && export CONDARC="$(pwd)/demos/condarc" && export PS1="$DEMO_PS1"`
Enter
Wait /\$/
Type `export CONDA_GLOBAL_HOME=/tmp/.cg-demo-pin && rm -rf "$CONDA_GLOBAL_HOME" && export PATH="$CONDA_GLOBAL_HOME/bin:$PATH"`
Enter
Wait /\$/
Type "conda global install ruff && conda global install black"
Enter
Wait /\$/
Type "clear"
Enter
Wait /\$/
Show

Type "# Two tools installed"
Enter
Sleep 500ms

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 2s

Type "# Pin ruff to prevent upgrades"
Enter
Sleep 500ms

Type@80ms "conda global pin -e ruff"
Enter
Wait /\$/
Sleep 2s

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 2s

Type "# Update all — pinned tools are skipped"
Enter
Sleep 500ms

Type@80ms "conda global update"
Enter
Wait /\$/
Sleep 3s

Type "# Unpin when ready to upgrade"
Enter
Sleep 500ms

Type@80ms "conda global unpin -e ruff"
Enter
Wait /\$/
Sleep 2s

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 3s
