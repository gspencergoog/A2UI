module.exports = function (config) {
  config.set({
    hostname: '127.0.0.1',
    listenAddress: '127.0.0.1',
    captureTimeout: 210000, // 3.5 minutes
    browserNoActivityTimeout: 210000,
    browserDisconnectTimeout: 10000,
    browserDisconnectTolerance: 3,
  });
};
