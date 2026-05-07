Source demos/_settings.tape

Output demos/sync.gif
Output demos/sync.mp4

Hide
Type `eval "$(pixi shell-hook -s bash -e dev)"`
Enter
Wait /\)/
Type `export PS1="$DEMO_PS1" && mkdir -p /tmp/.demo-home && echo 'PS1="$ "' > /tmp/.demo-home/.bash_profile && export HOME=/tmp/.demo-home`
Enter
Wait /\$/
Type `export CONDA_GLOBAL_HOME=/tmp/.cg-demo-sync && rm -rf "$CONDA_GLOBAL_HOME" && export PATH="$CONDA_GLOBAL_HOME/bin:$PATH"`
Enter
Wait /\$/
Type "conda global install ruff"
Enter
Wait /\$/
Type "clear"
Enter
Wait /\$/
Show

Type "# The manifest is the source of truth"
Enter
Sleep 500ms

Type@80ms `bat ~/.conda/global.toml`
Enter
Wait /\$/
Sleep 3s

Type "# Edit it directly (or use 'conda global edit')"
Enter
Sleep 500ms

Type@80ms `cat >> ~/.conda/global.toml << 'EOF'`
Enter
Type ""
Enter
Type "[envs.black]"
Enter
Type `packages = ["black"]`
Enter
Type ""
Enter
Type `[envs.black.exposed]`
Enter
Type `black = "black"`
Enter
Type "EOF"
Enter
Wait /\$/
Sleep 1s

Type@80ms `bat ~/.conda/global.toml`
Enter
Wait /\$/
Sleep 3s

Type "# Sync reconciles disk with manifest"
Enter
Sleep 500ms

Type@80ms "conda global sync"
Enter
Wait /\$/
Sleep 3s

Type@80ms "conda global list"
Enter
Wait /\$/
Sleep 3s
