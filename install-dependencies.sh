#!/bin/bash -xe

root_dir="$(cd $(dirname $0) && pwd -P)"
lib_dir="${root_dir}/resources/lib"

rm -rf "${lib_dir}"
mkdir -p "${lib_dir}"

tmpdir="$(mktemp -d)"

virtualenv "${tmpdir}"
pushd "${tmpdir}"
source "${tmpdir}/bin/activate"

pip install tornado==4.5.3 fuzzywuzzy ngram futures

venv_libs=$(file "${tmpdir}/lib/python"*"/site-packages" | cut -d: -f1)

ls -l "${venv_libs}"

cp -r "${venv_libs}/six.py" "${lib_dir}" || true
cp    "${venv_libs}/singledispatch" "${lib_dir}" || true
cp    "${venv_libs}/backports_abc.py" "${lib_dir}" || true
cp -r "${venv_libs}/concurrent" "${lib_dir}" || true
rm -r "${venv_libs}/tornado/test"
find  "${venv_libs}/tornado" -name '*.so' -exec rm -v "{}" \;
cp -r "${venv_libs}/tornado" "${lib_dir}"
cp -r "${venv_libs}/fuzzywuzzy" "${lib_dir}"
cp    "${venv_libs}/ngram.py" "${lib_dir}"

ls -l "${lib_dir}"

popd
rm -r "${tmpdir}"
