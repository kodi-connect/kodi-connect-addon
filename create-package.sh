#!/bin/bash -xe

root_dir="$(cd $(dirname $0) && pwd -P)"
plugin_id="plugin.video.kodiconnect"
package_filepath="${root_dir}/${plugin_id}-0.1.0.zip"

rm -fv "${package_filepath}"

tmpdir="$(mktemp -d)"
install_dir="${tmpdir}/${plugin_id}"
mkdir -p "${install_dir}"

cp -r \
  "${root_dir}/addon.xml" \
  "${root_dir}/plugin.py" \
  "${root_dir}/resources" \
  "${root_dir}/icon.png" \
  "${root_dir}/LICENSE.txt" \
  "${install_dir}"

find "${install_dir}" -name '*.pyc' -exec rm "{}" \;

pushd "${tmpdir}"

zip -r "${package_filepath}" .

popd

rm -r "${tmpdir}"
