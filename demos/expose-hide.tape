Source demos/_settings.tape

Output demos/expose-hide.gif
Output demos/expose-hide.mp4

Hide
Type `eval "$(pixi shell-hook -s bash -e dev)"`
Enter
Wait /\)/
Type `export DEMO_HOME=/tmp/.demo-home-expose && rm -rf "$DEMO_HOME" && mkdir -p "$DEMO_HOME" && echo 'PS1="$ "' > "$DEMO_HOME/.bash_profile" && export HOME="$DEMO_HOME" && export CONDARC="$(pwd)/demos/condarc" && export PS1="$DEMO_PS1"`
Enter
Wait /\$/
Type `export CONDA_GLOBAL_HOME=/tmp/.cg-demo-expose && rm -rf "$CONDA_GLOBAL_HOME" && export PATH="$CONDA_GLOBAL_HOME/bin:$PATH"`
Enter
Wait /\$/
Type "conda global install ruff"
Enter
Wait /\$/
Type "clear"
Enter
Wait /\$/
Show

Type "# ruff is installed — expose an extra binary"
Enter
Sleep 500ms

Type@80ms "conda global expose ruff-fmt=ruff -e ruff"
Enter
Wait /\$/
Sleep 2s

Type "# Both names work now"
Enter
Sleep 500ms

Type@80ms "ruff version"
Enter
Wait /\$/
Sleep 1s

Type@80ms "ruff-fmt --version"
Enter
Wait /\$/
Sleep 2s

Type "# Hide the alias without uninstalling"
Enter
Sleep 500ms

Type@80ms "conda global hide ruff-fmt -e ruff"
Enter
Wait /\$/
Sleep 2s

Type "# The original is still there"
Enter
Sleep 500ms

Type@80ms "ruff version"
Enter
Wait /\$/
Sleep 2s

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 3s
