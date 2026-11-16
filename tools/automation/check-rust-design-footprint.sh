#!/usr/bin/env bash
# Guard the default search executable against columnar dependency and size creep.
set -euo pipefail

cd "$(dirname "$0")/../.."
crate=osr-design-search
max_binary_bytes=2097152
max_package_bytes=262144
target_dir=${CARGO_TARGET_DIR:-target}

tree=$(cargo tree --locked -p "$crate" -e normal --prefix none --format '{p}')
if printf '%s\n' "$tree" | grep -E '^(arrow([_-]| )|parquet([_-]| )|polars([_-]| )|datafusion([_-]| )|geoarrow([_-]| ))' >/dev/null; then
    printf '%s\n' 'Default osr-design-search dependency graph includes columnar crates' >&2
    exit 1
fi

CARGO_BUILD_JOBS=${CARGO_BUILD_JOBS:-2} cargo build --locked --release -p "$crate" --bin "$crate"
binary="$target_dir/release/$crate"
binary_bytes=$(stat -c %s "$binary")
if (( binary_bytes > max_binary_bytes )); then
    printf 'Default binary %s bytes exceeds %s-byte budget\n' "$binary_bytes" "$max_binary_bytes" >&2
    exit 1
fi

cargo package --locked --offline --no-verify --allow-dirty -p "$crate"
package_id=$(cargo pkgid -p "$crate")
version=${package_id##*#}
version=${version##*@}
package="$target_dir/package/$crate-$version.crate"
package_bytes=$(stat -c %s "$package")
if (( package_bytes > max_package_bytes )); then
    printf 'Design-search source package %s bytes exceeds %s-byte budget\n' "$package_bytes" "$max_package_bytes" >&2
    exit 1
fi

printf 'default_binary_bytes=%s max=%s\n' "$binary_bytes" "$max_binary_bytes"
printf 'source_package_bytes=%s max=%s\n' "$package_bytes" "$max_package_bytes"
printf 'default_columnar_dependencies=0\n'
