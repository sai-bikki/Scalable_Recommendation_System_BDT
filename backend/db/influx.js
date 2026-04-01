const { InfluxDB, Point } = require('@influxdata/influxdb-client');

let writeApi;
let queryApi;

function connectInflux() {
    const client = new InfluxDB({
        url: process.env.INFLUX_URL,
        token: process.env.INFLUX_TOKEN,
    });

    writeApi = client.getWriteApi(process.env.INFLUX_ORG, process.env.INFLUX_BUCKET, 'ns');
    queryApi = client.getQueryApi(process.env.INFLUX_ORG);
    console.log('✅ InfluxDB connected');
}

function getWriteApi() {
    return writeApi;
}

function getQueryApi() {
    return queryApi;
}

module.exports = { connectInflux, getWriteApi, getQueryApi, Point };
