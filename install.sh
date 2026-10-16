#!/bin/sh
# Link every skill in this repo into ~/.agents/skills, where Codex and Pi read
# skills. Safe to re-run: it replaces only links into a clone of this repo
# (a repo whose .claude-plugin/marketplace.json is named "yudame"), removes
# only dangling links it made, and leaves everything else alone.
set -eu

REPO=$(cd "$(dirname "$0")" && pwd -P)
DEST="$HOME/.agents/skills"
MANIFEST="$DEST/.yudame-installed"
mkdir -p "$DEST"

marketplace() { # marketplace name of the repo at $1: the file's first "name"
  awk '{ t = t $0 " " } END {
    if (match(t, /"name"[ \t]*:[ \t]*"[^"]*"/)) {
      s = substr(t, RSTART, RLENGTH); sub(/^[^:]*:[ \t]*"/, "", s); sub(/"$/, "", s); print s
    } }' "$1/.claude-plugin/marketplace.json" 2>/dev/null
}

target() { # where the link $1 points, made absolute
  t=$(readlink "$1")
  case "$t" in /*) ;; *) t="$DEST/$t" ;; esac
  printf '%s\n' "$t"
}

ours() { # is $1 a skill directory path inside a clone of this repo?
  case "$1" in */plugins/*/skills/*) ;; *) return 1 ;; esac
  [ "$(marketplace "${1%/plugins/*/skills/*}")" = yudame ]
}

in_manifest() { # was "$1 -> $2" made by an earlier run?
  [ -f "$MANIFEST" ] && grep -Fxq "$1	$2" "$MANIFEST"
}

kept=$(mktemp)
trap 'rm -f "$kept"' EXIT

for src in "$REPO"/plugins/*/skills/*/; do
  src=${src%/}
  name=${src##*/}
  [ -f "$src/SKILL.md" ] || continue
  link="$DEST/$name"
  if [ -L "$link" ]; then
    t=$(target "$link")
    if [ "$t" = "$src" ]; then
      printf '%s\t%s\n' "$name" "$src" >>"$kept"
      continue
    fi
    if ours "$t" || { [ ! -e "$link" ] && in_manifest "$name" "$t"; }; then
      ln -sfn "$src" "$link"
      echo "replaced $name (was $t)"
    else
      echo "skipped $name: links to $t, not this repo"
      continue
    fi
  elif [ -e "$link" ]; then
    echo "skipped $name: $link exists and is not a link"
    continue
  else
    ln -s "$src" "$link"
    echo "linked $name"
  fi
  printf '%s\t%s\n' "$name" "$src" >>"$kept"
done

# Dangling links: a skill deleted or renamed here, or a clone that moved.
for link in "$DEST"/* "$DEST"/.[!.]*; do
  [ -L "$link" ] && [ ! -e "$link" ] || continue
  name=${link##*/}
  t=$(target "$link")
  case "$t" in
    "$REPO"/plugins/*/skills/*) ;;
    *) in_manifest "$name" "$t" || continue ;;
  esac
  rm "$link"
  echo "removed $name (pointed at missing $t)"
done

# Earlier entries whose link is still there and unchanged stay ours.
if [ -f "$MANIFEST" ]; then
  while IFS='	' read -r name t; do
    [ -L "$DEST/$name" ] && [ "$(target "$DEST/$name")" = "$t" ] &&
      ! grep -q "^$name	" "$kept" && printf '%s\t%s\n' "$name" "$t" >>"$kept"
  done <"$MANIFEST"
fi
sort -u "$kept" >"$MANIFEST"
echo "$(grep -c . "$MANIFEST") skills linked in $DEST"
