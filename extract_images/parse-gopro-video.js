const gpmfExtract = require('gpmf-extract');
const goproTelemetry = require('gopro-telemetry');
const fs = require('fs');
const yargs = require('yargs/yargs')
const { hideBin } = require('yargs/helpers')

/* 
This is a work-around the problem of node not being able to open very large 
files. See: https://github.com/JuanIrache/gpmf-extract#handling-large-files
*/ 
function bufferAppender(path, chunkSize) {
    return function (mp4boxFile) {
      var stream = fs.createReadStream(path, { highWaterMark: chunkSize });
      var bytesRead = 0;
      stream.on('end', () => {
        mp4boxFile.flush();
      });
      stream.on('data', chunk => {
        var arrayBuffer = new Uint8Array(chunk).buffer;
        arrayBuffer.fileStart = bytesRead;
        mp4boxFile.appendBuffer(arrayBuffer);
        bytesRead += chunk.length;
      });
      stream.resume();
    };
  }


parameters = yargs(hideBin(process.argv))
  .command('$0 <input> [output]', 
  'A tool for extracting metadata from GoPro video.',
  (yargs) => {
    yargs
      .positional('input', {
        describe: 'file path of input video',
        type: 'string'
      })
      .positional('output', {
        describe: 'file path of outut json',
        type: 'string',
        default: 'video-metadata.json'
      })
  })
  .argv

const res = gpmfExtract(bufferAppender(parameters.input, 100 * 1024 * 1024));

res.then(extracted => {
    goproTelemetry(extracted, 
        {stream: ["CORI", "GPS5", "SHUT", "GRAV"]}, 
        telemetry => {
            fs.writeFileSync(parameters.output, JSON.stringify(telemetry, null, 4));
            console.log('Telemetry saved as JSON');
        });
  })
  .catch(error => console.error(error));



