'use strict';

const readline = require('readline');
const fs = require('fs');
const express = require('express');
const app = express();

//app.use(express.static('public'));

app.get('/', (req, res) => {
  res.write('<html>');
  res.write('<head><title>CBMC Continuous Benchmarking</title></head>');
  res.write('<link rel="stylesheet" href="styles.css">');
  res.write('<body>');
  res.write('<h1>CBMC Continuous Benchmarking</h1>');
  res.write('<h2>SV-COMP 2019 Benchmarks Results</h2>');
  res.write('<table>');
  res.write('<tr><td>ReachSafety-Arrays</td><td><a href="svcomp19/benchexec/results-ReachSafety-Arrays/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-Arrays/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-BitVectors</td><td><a href="svcomp19/benchexec/results-ReachSafety-BitVectors/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-BitVectors/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-ControlFlow</td><td><a href="svcomp19/benchexec/results-ReachSafety-ControlFlow/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-ControlFlow/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Floats</td><td><a href="svcomp19/benchexec/results-ReachSafety-Floats/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-Floats/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Heap</td><td><a href="svcomp19/benchexec/results-ReachSafety-Heap/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-Heap/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Loops</td><td><a href="svcomp19/benchexec/results-ReachSafety-Loops/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-Loops/diff.html">diff</a></td></tr>');
  res.write('<tr><td>MemSafety-Arrays</td><td><a href="svcomp19/benchexec/results-MemSafety-Arrays/index.html">table</a></td><td><a href="svcomp19/benchexec/results-MemSafety-Arrays/diff.html">diff</a></td></tr>');
  res.write('<tr><td>MemSafety-Heap</td><td><a href="svcomp19/benchexec/results-MemSafety-Heap/index.html">table</a></td><td><a href="svcomp19/benchexec/results-MemSafety-Heap/diff.html">diff</a></td></tr>');
  res.write('<tr><td>MemSafety-LinkedLists</td><td><a href="svcomp19/benchexec/results-MemSafety-LinkedLists/index.html">table</a></td><td><a href="svcomp19/benchexec/results-MemSafety-LinkedLists/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Java</td><td><a href="svcomp19/benchexec/results-ReachSafety-Java/index.html">table</a></td><td><a href="svcomp19/benchexec/results-ReachSafety-Java/diff.html">diff</a></td></tr>');
  res.write('</table>');

  var analyses = ['n/a', 'n/a', 'n/a', 'n/a'];
  var lineReader = readline.createInterface({
    input: fs.createReadStream('public/log')
  });
  lineReader.on('line', function (line) {
    if(line.includes('Starting evaluation')) {
      analyses.push(line.substring(52));
    }
  }).on('close', () => {
  res.write('<h2>Current Analysis</h2>');
  res.write(analyses[analyses.length-1]+'<br/>');
  res.write('<h2>Recent Analyses</h2>');
  res.write(analyses[analyses.length-2]+'<br/>');
  res.write(analyses[analyses.length-3]+'<br/>');
  res.write(analyses[analyses.length-4]+'<br/>');
  res.write('<h2>SV-COMP 2018 Benchmarks Results</h2>');
  res.write('<table>');
  res.write('<tr><td>ReachSafety-Arrays</td><td><a href="svcomp18/benchexec/results-ReachSafety-Arrays/index.html">table</a></td><td><a href="svcomp18/benchexec/results-ReachSafety-Arrays/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-BitVectors</td><td><a href="svcomp18/benchexec/results-ReachSafety-BitVectors/index.html">table</a></td><td><a href="svcomp18/benchexec/results-ReachSafety-BitVectors/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-ControlFlow</td><td><a href="svcomp18/benchexec/results-ReachSafety-ControlFlow/index.html">table</a></td><td><a href="svcomp18/benchexec/results-ReachSafety-ControlFlow/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Floats</td><td><a href="svcomp18/benchexec/results-ReachSafety-Floats/index.html">table</a></td><td><a href="svcomp18/benchexec/results-ReachSafety-Floats/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Heap</td><td><a href="svcomp18/benchexec/results-ReachSafety-Heap/index.html">table</a></td><td><a href="svcomp18/benchexec/results-ReachSafety-Heap/diff.html">diff</a></td></tr>');
  res.write('<tr><td>ReachSafety-Loops</td><td><a href="svcomp18/benchexec/results-ReachSafety-Loops/index.html">table</a></td><td><a href="svcomp18/benchexec/results-ReachSafety-Loops/diff.html">diff</a></td></tr>');
  res.write('<tr><td>MemSafety-Arrays</td><td><a href="svcomp18/benchexec/results-MemSafety-Arrays/index.html">table</a></td><td><a href="svcomp18/benchexec/results-MemSafety-Arrays/diff.html">diff</a></td></tr>');
  res.write('<tr><td>MemSafety-Heap</td><td><a href="svcomp18/benchexec/results-MemSafety-Heap/index.html">table</a></td><td><a href="svcomp18/benchexec/results-MemSafety-Heap/diff.html">diff</a></td></tr>');
  res.write('<tr><td>MemSafety-LinkedLists</td><td><a href="svcomp18/benchexec/results-MemSafety-LinkedLists/index.html">table</a></td><td><a href="svcomp18/benchexec/results-MemSafety-LinkedLists/diff.html">diff</a></td></tr>');
  res.write('</table>');
  res.write('</body>');
  res.write('</html>');
  res.end();
  });
});

app.use(express.static('public'));

app.use(function(req, res, next) {
    res.status(404).send("Sorry, that route doesn't exist.");
});

// Start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}`);
  console.log('Press Ctrl+C to quit.');
});

