const gpmfExtract = require('gpmf-extract');
const goproTelemetry = require('gopro-telemetry');
const fs = require('fs');


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


const filename = '/local/jmm403/NIWA 2021 Jan/GoPro/128/GX010128.MP4';

const res = gpmfExtract(bufferAppender(filename, 100 * 1024 * 1024));
// "GRAV" Gravity vector
res.then(extracted => {
    goproTelemetry(extracted, 
        {stream: "CORI"}, 
        telemetry => {
            fs.writeFileSync('camera_quaternions.json', JSON.stringify(telemetry, null, 4));
            console.log('Telemetry saved as JSON');
        });
  })
  .catch(error => console.error(error));

res.then(extracted => {
    goproTelemetry(extracted, 
        {stream: "GPS5",
        repeatSticky: true}, 
        telemetry => {
            fs.writeFileSync('gps.json', JSON.stringify(telemetry, null, 4));
            console.log('Telemetry saved as JSON');
        });
  })
  .catch(error => console.error(error));

  res.then(extracted => {
    goproTelemetry(extracted, 
        {stream: "SHUT",
        repeatSticky: true}, 
        telemetry => {
            fs.writeFileSync('frames.json', JSON.stringify(telemetry, null, 4));
            console.log('Telemetry saved as JSON');
        });
  })
  .catch(error => console.error(error));

