#!/usr/bin/env bash
# Pruebas automáticas + cálculo de los conjuntos de los dos ejercicios
set -e
cd "$(dirname "$0")"

echo "################ PRUEBAS AUTOMÁTICAS ################"
python3 -m unittest -v test_tarea

echo; echo "################ EJERCICIOS ################"
python3 conjuntos.py grammars/gramatica1.txt grammars/gramatica2.txt -o resultados.txt
