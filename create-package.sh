#!/bin/bash -xe

# To run through docker:
#  docker-compose run --rm --no-deps app ./create-package.sh
#  docker-compose run --rm --no-deps app ./install-dependencies.sh

root_dir="$(cd $(dirname $0) && pwd -P)"
plugin_id="plugin.video.kodiconnect"
version="$(cat "${root_dir}/version")"
python_addon_version="${PYTHON_ADDON_VERSION}"

if [ -z "${python_addon_version}" ]; then
  echo "Missing PYTHON_ADDON_VERSION variable"
  exit 1
fi

package_dir="${root_dir}/packages/${python_addon_version}"

mkdir -p "${package_dir}"

package_filepath="${package_dir}/${plugin_id}-${version}.zip"

rm -fv "${package_filepath}"

tmpdir="$(mktemp -d)"
install_dir="${tmpdir}/${plugin_id}"
mkdir -p "${install_dir}"

cp -r \
  "${root_dir}/addon.xml" \
  "${root_dir}/plugin.py" \
  "${root_dir}/service.py" \
  "${root_dir}/resources" \
  "${root_dir}/icon.png" \
  "${root_dir}/LICENSE.txt" \
  "${install_dir}"

find "${install_dir}" -name '*.pyc' -exec rm "{}" \;

sed_replace_cmd="s/xversionx/${version}/g"
sed -i "${sed_replace_cmd}" "${install_dir}/addon.xml"
find "${install_dir}/resources/language" -name '*.po' -exec sed -i "${sed_replace_cmd}" "{}" \;

sed_replace_cmd="s/xpythonversionx/${python_addon_version}/g"
sed -i "${sed_replace_cmd}" "${install_dir}/addon.xml"

pushd "${tmpdir}"

zip -r "${package_filepath}" .

popd

cat "${tmpdir}/plugin.video.kodiconnect/addon.xml"

rm -r "${tmpdir}"

echo "Created package: ${package_filepath}"
