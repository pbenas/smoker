#!/bin/bash

retval=0

[ -d packages ] && rm -rf packages
[ -f hiera.fragment.txt ] && rm -f hiera.fragment.txt

if [ ! -f setup.py ]; then
    echo "[ERROR] Can't find setup.py" 1>&2
    exit 1
fi

echo "[INFO] Cleaning up"
python setup.py clean

echo "[INFO] Running tests"
python setup.py test
# Fail if tests haven't passed
if [ $? -eq 0 ]; then
    echo "[SUCCESS] tests passed"
else
    echo "[ERROR] tests haven't passed, skipping build"
    exit $?
fi

echo "[INFO] Building $i"
if [ ! -f smoker.spec ]; then
    echo "[ERROR] Can't find smoker.spec" 1>&2
    exit 1
fi

mkdir -p ~/rpmbuild/{SPECS,SOURCES}
cp smoker.spec ~/rpmbuild/SPECS/

[ $BRANCH ] || BRANCH=master
wget -P ~/rpmbuild/SOURCES/ https://github.com/gooddata/smoker/archive/${BRANCH}.tar.gz
rpmbuild -ba ~/rpmbuild/SPECS/smoker.spec

mkdir -p packages/artifacts
mv ~/rpmbuild/RPMS/*/* packages/artifacts/
mv ~/rpmbuild/SRPMS/* packages/artifacts/

[ $BUILD_NUMBER ] || BUILD_NUMBER="0"
if [ "0" -eq "${BUILD_NUMBER}" ]; then
	echo "# local build " > hiera.fragment.txt
else
	echo "# ${BUILD_URL}" > hiera.fragment.txt
fi
rpm -qp --qf '%{sourcerpm}\n' packages/artifacts/*smoker*.rpm |
	sed -n 's/.*-\([^-]*\)-\(.*\).src.rpm/python_revision: \1-\2/p' |
	sort | uniq >> hiera.fragment.txt

exit $retval
