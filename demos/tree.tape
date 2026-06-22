Source demos/_settings.tape

Output demos/tree.gif
Output demos/tree.mp4

Hide
Type `eval "$(pixi shell-hook -s bash -e dev)"`
Enter
Wait /\)/
Type `export DEMO_HOME=/tmp/.demo-home-tree && rm -rf "$DEMO_HOME" && mkdir -p "$DEMO_HOME" && echo 'PS1="$ "' > "$DEMO_HOME/.bash_profile" && export HOME="$DEMO_HOME" && export CONDARC="$(pwd)/demos/condarc" && export PS1="$DEMO_PS1"`
Enter
Wait /\$/
Type `export CONDA_GLOBAL_HOME=/tmp/.cg-demo-tree && rm -rf "$CONDA_GLOBAL_HOME" && export PATH="$CONDA_GLOBAL_HOME/bin:$PATH"`
Enter
Wait /\$/
Type "conda global install black"
Enter
Wait /\$/
Type "clear"
Enter
Wait /\$/
Show

Type "# See what's inside a tool's environment"
Enter
Sleep 500ms

Type@80ms "conda global tree -e black"
Enter
Wait /\$/
Sleep 4s

Type "# Add a dependency to the environment"
Enter
Sleep 500ms

Type@80ms "conda global add tomli -e black"
Enter
Wait /\$/
Sleep 2s

Type "# The tree grows"
Enter
Sleep 500ms

Type@80ms "conda global tree -e black"
Enter
Wait /\$/
Sleep 4s
