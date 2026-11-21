#!/usr/bin/env bash
# Launch video -> silent GIF (images/launch.gif). GIFs carry no audio, so this also mutes it.
#   tools/make_gif.sh path/to/launch.mp4
set -euo pipefail
V=${1:?launch video}
OUT="$(dirname "$0")/../images/launch.gif"
ffmpeg -v error -y -an -i "$V" -filter_complex \
  "hqdn3d=3:3:6:6,fps=12,scale=360:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
  "$OUT"
echo "$OUT"
