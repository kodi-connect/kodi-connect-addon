#!/bin/bash -xe

root_dir="$(cd $(dirname $0) && pwd -P)"
lib_dir="${root_dir}/resources/lib"

rm -rf "${lib_dir}"
mkdir -p "${lib_dir}"

tmpdir="$(mktemp -d)"

virtualenv "${tmpdir}"
pushd "${tmpdir}"
source "${tmpdir}/bin/activate"

pip install tornado fuzzywuzzy[speedup] setix tinynumpy

venv_libs=$(file "${tmpdir}/lib/python"*"/site-packages" | cut -d: -f1)

ls -l "${venv_libs}"

cp -r "${venv_libs}/certifi" "${lib_dir}"
cp -r "${venv_libs}/six.py" "${lib_dir}"
cp    "${venv_libs}/singledispatch.py" "${venv_libs}/singledispatch_helpers.py" "${lib_dir}"
cp    "${venv_libs}/backports_abc.py" "${lib_dir}"
cp -r "${venv_libs}/tornado" "${lib_dir}"
cp -r "${venv_libs}/Levenshtein" "${lib_dir}"
cp -r "${venv_libs}/fuzzywuzzy" "${lib_dir}"
# cp -r "${venv_libs}/numpy" "${lib_dir}"
# cp -r "${venv_libs}/setix" "${lib_dir}"

ls -l "${lib_dir}"

popd
rm -r "${tmpdir}"
