/* c++ wrapper for python */
// for more information, refers to https://docs.python.org/3/extending/extending.html
#include <Python.h>
#include <string>
#include "mahjong.h" // header that defines the `action` function

using namespace std;

static PyObject *
MahjongBot_action(PyObject *self, PyObject *args) {
    std::string request = PyUnicode_AsUTF8(PyTuple_GetItem(args, 0));
    std::string response = action(request); // call the function
    return PyUnicode_FromString(response.c_str());
}

static PyMethodDef mahjongMethods[] = {
        // defines a method called `action`
        {"action", MahjongBot_action, METH_VARARGS, "make an action"},
        {NULL, NULL, 0, NULL},
};
static PyModuleDef mahjongbotModule = {
        // defines a module called `MahjongBot` with the above methods
        PyModuleDef_HEAD_INIT,
        "MahjongBot",
        "A C++ Mahjong Bot",
        -1,
        mahjongMethods,
};

PyMODINIT_FUNC
PyInit_MahjongBot(void) {
    return PyModule_Create(&mahjongbotModule);
}

