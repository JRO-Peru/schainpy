#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>


static PyObject *hildebrand_sekhon(PyObject *self, PyObject *args) {
  double navg;
  PyObject *data_obj, *data_array;

  if (!PyArg_ParseTuple(args, "Od", &data_obj, &navg)) {
      return NULL;
  }
  
  data_array = PyArray_FROM_OTF(data_obj, NPY_FLOAT64, NPY_IN_ARRAY);
  
  if (data_array == NULL) {
      Py_XDECREF(data_array);
      Py_XDECREF(data_obj);
      return NULL;
  }
  double *sortdata = (double*)PyArray_DATA(data_array);
  int lenOfData = (int)PyArray_SIZE(data_array) ;
  double nums_min = lenOfData*0.2;
  if (nums_min <= 5) nums_min = 5;
  double sump = 0;
  double sumq = 0;
  int j = 0;
  int cont = 1;
  double rtest = 0;
  while ((cont == 1) && (j < lenOfData)) {
    sump = sump + sortdata[j];
    sumq = sumq + pow(sortdata[j], 2);
    if (j > nums_min) {
      rtest = (double)j/(j-1) + 1/navg;
      if ((sumq*j) > (rtest*pow(sump, 2))) {
        j = j - 1;
        sump = sump - sortdata[j];
        sumq = sumq - pow(sortdata[j],2);
        cont = 0;
      }
    }
    j = j + 1;
  }

  double lnoise = sump / j;

  Py_DECREF(data_array);

  return PyLong_FromLong(lnoise);
  //return Py_BuildValue("d", lnoise);
}


static PyMethodDef noiseMethods[] = {
  { "hildebrand_sekhon", hildebrand_sekhon, METH_VARARGS, "Get noise with hildebrand_sekhon algorithm" },
  { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef noisemodule = {
  PyModuleDef_HEAD_INIT,
  "_noise",
  "Get noise with hildebrand_sekhon algorithm",
  -1,
  noiseMethods
};

#endif

#if PY_MAJOR_VERSION >= 3
  PyMODINIT_FUNC PyInit__noise(void) {
    Py_Initialize();
    import_array();
    return PyModule_Create(&noisemodule);
  }
#else
  PyMODINIT_FUNC init_noise() {
    Py_InitModule("_noise", noiseMethods);
    import_array();
  }
#endif
