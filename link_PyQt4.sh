#!/bin/bash
# This hook is run after a new virtualenv is activated.

python_version=python$(python -c "import sys; print (str(sys.version_info[0])+'.'+str(sys.version_info[1]))")
var=( $(which -a $python_version) )

get_python_lib_cmd="from distutils.sysconfig import get_python_lib; print (get_python_lib())"
lib_virtualenv_path=$(python -c "$get_python_lib_cmd")
lib_system_path=$(${var[-1]} -c "$get_python_lib_cmd")
sip_path=$(ls $lib_system_path/sip*.so)

echo "Linking Qt4..."
ln -s $lib_system_path/PyQt4 $lib_virtualenv_path/PyQt4
echo "Linking SIP..."
ln -s $sip_path $lib_virtualenv_path/sip.so
