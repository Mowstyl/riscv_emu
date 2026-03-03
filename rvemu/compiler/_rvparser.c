/*---------------------------------------------------------------------------------*
 *   RISC-V Emulator
 *   Copyright (C) 2026  Mowstyl
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.

 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *--------------------------------------------------------------------------------*/

#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "RISC-V-Parser/rvp-utility-json.h"


static PyObject *rvParserError;

static PyObject *
rvparser_parse(PyObject *ignored,
			   PyObject *const *args,
			   Py_ssize_t nargs);

static PyMethodDef rvParserMethods[] = {
	{ "parse", (PyCFunction) rvparser_parse, METH_FASTCALL, "Parses an ASM code file and saves the result to a JSON formatted file" },
	{ NULL, NULL, 0, NULL } /* Sentinel */
};

static struct PyModuleDef rvparser_module = {
	PyModuleDef_HEAD_INIT, "_rvparser", /* name of module */
	NULL, /* module documentation, may be NULL */
	-1, /* size of per-interpreter state of the module,
	or -1 if the module keeps state in global variables. */
	rvParserMethods
};

PyMODINIT_FUNC
PyInit__rvparser(void)
{
	PyObject *m;

	assert(!PyErr_Occurred());
	m = PyModule_Create(&rvparser_module);
	if (m == NULL)
		return NULL;

	rvParserError = PyErr_NewException("rvemu.compiler.error", NULL, NULL);
	Py_XINCREF(rvParserError);
	if (PyModule_AddObject(m, "error", rvParserError) < 0) {
		Py_XDECREF(rvParserError);
		Py_CLEAR(rvParserError);
		Py_DECREF(m);
		return NULL;
	}

	return m;
}

//Arguments: input file, output file
static PyObject *
rvparser_parse(PyObject *ignored,
			   PyObject *const *args,
			   Py_ssize_t nargs) {
	FILE *in,
	     *out;
	const char *in_file,
			   *out_file;

	if (nargs != 2) {
		PyErr_SetString(rvParserError, "Syntax: parse(<infile>, <outfile>)");
		return NULL;
	}

	if (!PyUnicode_Check(args[0]) || !PyUnicode_Check(args[1])) {
		PyErr_SetString(rvParserError, "The arguments must be strings");
		return NULL;
	}

	in_file = PyUnicode_AsUTF8(args[0]);
	out_file = PyUnicode_AsUTF8(args[1]);

	if (!in_file || !out_file) {
		return NULL;
	}

	in = fopen(in_file, "r");
	out = fopen(out_file, "w");

	export_to_json(*parse(in), out);

	fclose(in);
	fclose(out);

	Py_RETURN_NONE;
}
