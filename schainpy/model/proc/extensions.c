#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define NUM_CPY_THREADS 8
#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <complex.h>
#include <time.h>

// void printArr(int *array);
static PyObject *hildebrand_sekhon(PyObject *self, PyObject *args);
static PyObject *correlateByBlock(PyObject *self, PyObject *args);
#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

static PyMethodDef extensionsMethods[] = {
  { "correlateByBlock", (PyCFunction)correlateByBlock, METH_VARARGS, "get correlation by block" },
  { "hildebrand_sekhon", (PyCFunction)hildebrand_sekhon, METH_VARARGS, "get noise with hildebrand_sekhon" },
  { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC initcSchain() {
  Py_InitModule("cSchain", extensionsMethods);
  import_array();
}

static PyObject *correlateByBlock(PyObject *self, PyObject *args) {
 
  // int *x  = (int*) malloc(4000000 * 216 * sizeof(int));;
  // int a = 5;
  // x = &a;
  // int b = 6;
  // x = &b;
  // printf("Antes de imprimir x \n");
  // printf("%d \n", x[0]);

  PyObject *data_obj1, *data_obj2;
  PyArrayObject *data_array1, *data_array2, *correlateRow, *out, *dataRow, *codeRow; //, , 
  int mode;

  if (!PyArg_ParseTuple(args, "OOi", &data_obj1, &data_obj2, &mode)) return NULL;

  data_array1 = (PyArrayObject *) PyArray_FROM_OTF(data_obj1, NPY_COMPLEX128, NPY_ARRAY_IN_ARRAY);
  data_array2 = (PyArrayObject *) PyArray_FROM_OTF(data_obj2, NPY_FLOAT64, NPY_ARRAY_IN_ARRAY);

  npy_intp dims[1];
  dims[0] = 200;
  npy_intp dims_code[1];
  dims_code[0] = 16;

  double complex * dataRaw;
  double * codeRaw;
  dataRaw = (double complex*) PyArray_DATA(data_array1);
  codeRaw = (double *) PyArray_DATA(data_array2);
  double complex ** outC = malloc(40000*200*sizeof(double complex));
  int i;

  clock_t start = clock();
  for(i=0; i<40000; i++){
    // codeRow = PyArray_SimpleNewFromData(1, dims_code, NPY_FLOAT64, codeRaw + 16 * i);
    // dataRow = PyArray_SimpleNewFromData(1, dims, NPY_COMPLEX128, dataRaw + 200 * i);
    // Py_INCREF(codeRow);
    // Py_INCREF(dataRow);
    // PyArray_ENABLEFLAGS(codeRow, NPY_ARRAY_OWNDATA);
    // PyArray_ENABLEFLAGS(dataRow, NPY_ARRAY_OWNDATA);
    correlateRow = (PyArrayObject *) PyArray_Correlate2(PyArray_SimpleNewFromData(1, dims_code, NPY_FLOAT64, codeRaw + 16 * i), PyArray_SimpleNewFromData(1, dims, NPY_COMPLEX128, dataRaw + 200 * i), (npy_intp) 2);
    //Py_INCREF(correlateRow);
    // PyArray_ENABLEFLAGS(correlateRow, NPY_ARRAY_OWNDATA);
    memcpy(outC + 200*i, (double complex*) PyArray_DATA(correlateRow), 200 * sizeof(double complex));

    Py_DECREF(correlateRow);
    // Py_DECREF(codeRow);
    // Py_DECREF(dataRow);
  }
  clock_t end = clock();
  float seconds = (float)(end - start) / CLOCKS_PER_SEC;
  printf("%f", seconds);
  // 
  npy_intp dimsret[2];
  dimsret[0] = 40000;
  dimsret[1] = 200;
  out = PyArray_SimpleNewFromData(2, dimsret, NPY_COMPLEX128, outC);
  PyArray_ENABLEFLAGS(out, NPY_ARRAY_OWNDATA);
  //Py_INCREF(out);
  Py_DECREF(data_array1);
  Py_DECREF(data_array2);
  // PyArray_DebugPrint(out);
  // Py_DECREF(data_obj2);
  // Py_DECREF(data_obj1);
  // Py_DECREF(codeRow);
  // Py_DECREF(dataRow);
  // free(dataRaw);
  // free(codeRaw);
  
  return PyArray_Return(out);
}

static PyObject *hildebrand_sekhon(PyObject *self, PyObject *args) {
  double navg;
  PyObject *data_obj, *data_array;

  if (!PyArg_ParseTuple(args, "Od", &data_obj, &navg)) return NULL;
  data_array = PyArray_FROM_OTF(data_obj, NPY_FLOAT64, NPY_ARRAY_IN_ARRAY);
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

  return Py_BuildValue("d", lnoise);
}

