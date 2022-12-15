const request = require('request');

module.exports = {
  make_api_call: function (url, method, in_body) {
    return new Promise((resolve, reject) => {
      if(method.toLowerCase() == 'post')
      {
        request.post(
          {
            url: url,
            method: method,
            json: true,
            "body": in_body
          },
          (err, res, body) => {
              if (err) reject(err)
                resolve(body)
          }
        );
      }
      else if (method.toLowerCase() == 'get')
      {
        request.get(url, {json: true}, (err, res, body) => {
          if (err) reject(err)
          resolve(body)
        });
      }
      
    })
  }
}