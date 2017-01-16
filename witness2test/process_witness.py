#!/usr/bin/python

from __future__ import print_function
from pycparser import c_ast, c_generator, c_parser, parse_file

import argparse
import hashlib
import re
import sys
#import xml.etree.CElementTree as ElementTree
import xml.etree.ElementTree as ElementTree

def validateConfig(graph, ns, witness, benchmark, bitwidth):
  config = {}
  for k in graph.findall('./graphml:data', ns):
    key = k.get('key')
    config[key] = k.text

  for k in ['witness-type', 'sourcecodelang', 'architecture', 'programhash']:
    if config.get(k) is None:
      print('INVALID WITNESS FILE: mandatory field {} missing'.format(k))
      sys.exit(1)

  if config['witness-type'] != 'violation_witness':
    raise ValueError('No support for ' + config['witness-type'])

  if config['sourcecodelang'] != 'C':
    raise ValueError('No support for language ' + config['sourcecodelang'])

  if config['architecture'] != '{}bit'.format(bitwidth):
    raise ValueError('Architecture mismatch')

  with open(benchmark, 'rb') as b:
    sha1hash = hashlib.sha1(b.read()).hexdigest()
    if config['programhash'] != sha1hash:
      print('INVALID WITNESS FILE: SHA1 mismatch')
      sys.exit(1)

  spec = re.sub(r'\s+', '', config['specification'])
  return re.sub(r'CHECK\(init\((\S+)\(\)\),LTL\((\S+)\)\)', '\g<1>', spec)


def setupTypes(ast, entryFunc, inputs, nondets, entry):
  for fun in ast.ext:
    if isinstance(fun, c_ast.Decl) and isinstance(fun.type, c_ast.FuncDecl):
      if fun.type.type.declname.startswith('__VERIFIER_nondet_'):
        info = {}
        info['type'] = c_generator.CGenerator().visit(fun.type)
        info['line'] = fun.coord.line
        nondets[fun.type.type.declname] = info
    elif isinstance(fun, c_ast.FuncDef):
      inputs[fun.decl.name] = {}
      for d in fun.body.block_items:
        if isinstance(d, c_ast.Decl):
          info = {}
          info['type'] = c_generator.CGenerator().visit(d.type)
          info['line'] = d.coord.line
          if d.init is None:
            inputs[fun.decl.name][d.name] = info
      if fun.decl.name == entryFunc:
        entry['type'] = c_generator.CGenerator().visit(fun.decl.type)
        entry['line'] = fun.coord.line


def setupWatch(ast, watch):
  class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self, watch):
      self.watch = watch

    def visit_FuncCall(self, node):
      if node.name.name.startswith('__VERIFIER_nondet_'):
        l = node.name.coord.line
        assert self.watch.get(l) is None
        self.watch[l] = node.name.name

  v = FuncCallVisitor(watch)
  v.visit(ast)


def checkTrace(trace, entryNode, violationNode):
  n = entryNode
  while trace[n].get('target') is not None:
    n = trace[n]['target']
  if n != violationNode:
    print("INVALID WITNESS FILE: trace does not end in violation node")
    sys.exit(1)


def buildTrace(graph, ns, trace):
  entryNode = None
  violationNode = None
  for n in graph.findall('./graphml:node', ns):
    i = n.get('id')
    trace[i] = {}
    for d in n.findall('./graphml:data', ns):
      if d.get('key') == 'entry' and d.text == 'true':
        assert entryNode is None
        entryNode = i
      elif d.get('key') == 'violation' and d.text == 'true':
        assert violationNode is None
        violationNode = i
  if entryNode is None:
    print("INVALID WITNESS FILE: no entry node")
    sys.exit(1)
  if violationNode is None:
    print("INVALID WITNESS FILE: no violation node")
    sys.exit(1)

  for e in graph.findall('./graphml:edge', ns):
    s = e.get('source')
    t = e.get('target')
    if s == violationNode:
      continue
    # only linear traces supported
    assert trace[s].get('target') is None
    trace[s]['target'] = t
    for d in e.findall('./graphml:data', ns):
      key = d.get('key')
      trace[s][key] = d.text

  checkTrace(trace, entryNode, violationNode)

  return entryNode


def processWitness(witness, benchmark, bitwidth):
  try:
    root = ElementTree.parse(witness).getroot()
  except:
    print("INVALID WITNESS FILE: failed to parse XML")
    sys.exit(1)
  # print(ElementTree.tostring(root))
  ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}
  graph = root.find('./graphml:graph', ns)
  if graph is None:
    print("INVALID WITNESS FILE: failed to parse XML - no graph node")
    sys.exit(1)

  entryFun = validateConfig(graph, ns, witness, benchmark, bitwidth)

  benchmarkString = ''
  with open(benchmark, 'r') as b:
    for line in b:
      line = re.sub(r'__attribute__\s*\(\(\s*[a-z_]+\s*\)\)\s*;', ';', line)
      line = re.sub(r'//.*', '', line)
      benchmarkString += line
  parser = c_parser.CParser()
  ast = parser.parse(benchmarkString, filename=benchmark)
  # ast.show(showcoord=True)

  inputs = {}
  nondets = {}
  entry = {}
  setupTypes(ast, entryFun, inputs, nondets, entry)
  assert entry
  watch = {}
  setupWatch(ast, watch)

  trace = {}
  entryNode = buildTrace(graph, ns, trace)

  values = []
  n = entryNode
  while trace[n].get('target') is not None:
    if trace[n].get('assumption') is not None:
      f = trace[n].get('assumption.scope')
      assert f is not None
      wrapped = 'void foo() { ' + trace[n]['assumption'] + '}'
      a_ast = parser.parse(wrapped).ext[0].body.block_items[0]
      if isinstance(a_ast, c_ast.Assignment):
        v = c_generator.CGenerator().visit(a_ast.rvalue)
        if inputs[f].get(a_ast.lvalue.name) is not None:
          values.append([f, a_ast.lvalue.name, v])
        elif watch.get(int(trace[n]['startline'])) is not None:
          w = watch[int(trace[n]['startline'])]
          values.append([w, v])
        # else:
        #   print(trace[n]['startline'])
        #   a_ast.show()
      # else:
      #   print(trace[n]['startline'])
      #   a_ast.show()

    n = trace[n]['target']

  # print('watch: ')
  # print(watch)
  # print('inputs: ')
  # print(inputs)
  # print('nondets: ')
  # print(nondets)
  assert values
  print('IN:')
  print('  ENTRY {n}()@[file {f} line {l}]'.format(
        n=entryFun, f=benchmark, l=entry['line']))

  for v in values:
    if len(v) == 3:
      info = inputs[v[0]][v[1]]
      print('  {t} {n}@[file {f} line {l} function {fun}]={value}'.format(
            t=info['type'], n=v[1], f=benchmark, l=info['line'], fun=v[0],
            value=v[2]))
    else:
      info = nondets[v[0]]
      print('  {t}@[file {f} line {l}]={value}'.format(
            t=info['type'], f=benchmark, l=info['line'], value=v[1]))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-w', '--witness', type=str, required=True,
                      help='graphml witness file')
  parser.add_argument('-b', '--benchmark', type=str, required=True,
                      help='benchmark file')
  parser.add_argument('-m', type=int,
                      help='bit width of system architecture')
  args = parser.parse_args()

  processWitness(args.witness, args.benchmark, args.m)


if __name__ == '__main__':
  main()
