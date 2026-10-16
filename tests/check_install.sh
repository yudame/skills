#!/bin/sh
# install.sh links every skill into ~/.agents/skills, is idempotent, and
# replaces or removes only links it made.  sh tests/check_install.sh
set -u

REPO=$(cd "$(dirname "$0")/.." && pwd -P)
T=$(mktemp -d)
T=$(cd "$T" && pwd -P)
trap 'rm -rf "$T"' EXIT
export HOME="$T/home"
D="$HOME/.agents/skills"
fails=0
check() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; fails=$((fails + 1)); fi; }
run() { (cd "$1" && sh "$REPO/install.sh") >"$T/out" 2>&1; }
skills=$(ls -d "$REPO"/plugins/*/skills/*/ | wc -l | tr -d ' ')

# Fresh home: one link per skill, each to its directory.
run /
check "fresh home links every skill" '[ "$(find "$D" -type l | wc -l | tr -d " ")" = "$skills" ]'
check "links resolve to the skill" '[ "$(readlink "$D/do-build")" = "$REPO/plugins/yudame-dev/skills/do-build" ] && [ -f "$D/present/SKILL.md" ]'

# Second run, from another cwd: nothing changes.
ls -l "$D" >"$T/before"
run "$T"
ls -l "$D" >"$T/after"
check "second run changes nothing" 'cmp -s "$T/before" "$T/after" && ! grep -qE "^(linked|replaced|removed)" "$T/out"'

# Things it did not make survive and are reported.
mkdir -p "$T/other/.claude-plugin" "$T/other/plugins/x/skills/email"
echo '{"name": "other", "plugins": [{"name": "yudame"}]}' >"$T/other/.claude-plugin/marketplace.json"
rm "$D/house-style" "$D/email" "$D/zoom-out"
mkdir "$D/house-style"
ln -s "$T/other/plugins/x/skills/email" "$D/email"
ln -s "$T/elsewhere" "$D/zoom-out"
ln -s "$T/gone/plugins/y/skills/old" "$D/old"
run /
check "real directory survives" '[ -d "$D/house-style" ] && [ ! -L "$D/house-style" ]'
check "other marketplace link survives" '[ "$(readlink "$D/email")" = "$T/other/plugins/x/skills/email" ]'
check "unrelated link survives" '[ "$(readlink "$D/zoom-out")" = "$T/elsewhere" ]'
check "each is reported skipped" '[ "$(grep -c "^skipped" "$T/out")" = 3 ]'
check "foreign dangling link is left" '[ -L "$D/old" ]'

# A link into another clone of this repo is replaced.
mkdir -p "$T/clone/.claude-plugin" "$T/clone/plugins/yudame-dev/skills/do-test"
cp "$REPO/.claude-plugin/marketplace.json" "$T/clone/.claude-plugin/"
ln -sfn "$T/clone/plugins/yudame-dev/skills/do-test" "$D/do-test"
run /
check "another clone's link is replaced" '[ "$(readlink "$D/do-test")" = "$REPO/plugins/yudame-dev/skills/do-test" ]'

# Dangling links it made are removed: into this clone, or listed in the manifest.
ln -s "$REPO/plugins/yudame-dev/skills/retired" "$D/retired"
printf 'moved\t%s\n' "$T/moved/plugins/yudame/skills/moved" >>"$D/.yudame-installed"
ln -s "$T/moved/plugins/yudame/skills/moved" "$D/moved"
run /
check "dangling link into this clone is removed" '[ ! -L "$D/retired" ]'
check "dangling link in the manifest is removed" '[ ! -L "$D/moved" ]'
check "foreign dangling link is still left" '[ -L "$D/old" ]'

echo "$fails failing"
[ "$fails" = 0 ]
